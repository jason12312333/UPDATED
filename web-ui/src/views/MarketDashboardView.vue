<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import echarts, { DOWN_COLOR, UP_COLOR } from '../echarts-setup'

type IndexDef = { name: string; market: 'SH' | 'SZ'; code: string; short: string }
type Row = Record<string, any>

const INDEXES: IndexDef[] = [
  { name: '上证指数', short: '上证', market: 'SH', code: '000001' },
  { name: '深证成指', short: '深成', market: 'SZ', code: '399001' },
  { name: '创业板指', short: '创业板', market: 'SZ', code: '399006' },
  { name: '沪深300', short: '沪深300', market: 'SH', code: '000300' },
  { name: '上证50', short: '上证50', market: 'SH', code: '000016' },
  { name: '中证1000', short: '中证1000', market: 'SH', code: '000852' },
]

const quotes = ref<Row[]>([])
const stat = ref<Row | null>(null)
const selected = ref<IndexDef>(INDEXES[0])
const minuteBars = ref<Row[]>([])
const loading = ref(false)
const error = ref('')
const lastUpdate = ref('')
const autoRefresh = ref(true)
const chartEl = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
let quoteTimer: number | undefined
let minuteTimer: number | undefined

function num(v: unknown): number {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

function fmt(v: unknown, digits = 2): string {
  const n = num(v)
  return n.toLocaleString('zh-CN', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}

function fmtAmount(v: unknown): string {
  const n = num(v)
  if (Math.abs(n) >= 1e12) return `${(n / 1e12).toFixed(2)}万亿`
  if (Math.abs(n) >= 1e8) return `${(n / 1e8).toFixed(2)}亿`
  if (Math.abs(n) >= 1e4) return `${(n / 1e4).toFixed(2)}万`
  return fmt(n, 0)
}

function quoteFor(index: IndexDef): Row {
  return quotes.value.find((q) => String(q.code) === index.code) || {}
}

function changeOf(q: Row): number {
  return num(q.price) - num(q.pre_close)
}

function pctOf(q: Row): number {
  const pre = num(q.pre_close)
  return pre ? (changeOf(q) / pre) * 100 : 0
}

function tone(v: number): string {
  return v > 0 ? 'up' : v < 0 ? 'down' : 'flat'
}

const marketBreadth = computed(() => {
  const s = stat.value || {}
  const up = num(s.up_count)
  const down = num(s.down_count)
  const neutral = num(s.neutral_count)
  const active = up + down + neutral
  return active ? (up / active) * 100 : 0
})

const selectedQuote = computed(() => quoteFor(selected.value))

async function fetchJson(url: string, init?: RequestInit): Promise<any> {
  const res = await fetch(url, init)
  if (!res.ok) {
    let detail = ''
    try { detail = JSON.stringify(await res.json()) } catch { detail = await res.text().catch(() => '') }
    throw new Error(`${res.status} ${res.statusText}${detail ? ` · ${detail}` : ''}`)
  }
  return res.json()
}

async function loadQuotesAndStat(showLoading = false) {
  if (showLoading) loading.value = true
  try {
    const [quoteResp, statResp] = await Promise.all([
      fetchJson('/api/v1/quotes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stocks: INDEXES.map((x) => ({ market: x.market, code: x.code })) }),
      }),
      fetchJson('/api/v1/market/stat'),
    ])
    quotes.value = Array.isArray(quoteResp.data) ? quoteResp.data : []
    stat.value = Array.isArray(statResp.data) ? statResp.data[0] || null : null
    lastUpdate.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    error.value = ''
  } catch (e: any) {
    error.value = `实时行情获取失败：${e?.message || e}`
  } finally {
    if (showLoading) loading.value = false
  }
}

async function loadMinute() {
  const x = selected.value
  try {
    const params = new URLSearchParams({
      market: x.market,
      code: x.code,
      category: 'MIN_1',
      start: '0',
      count: '240',
    })
    const resp = await fetchJson(`/api/v1/bars/index?${params}`)
    const rows: Row[] = Array.isArray(resp.data) ? resp.data : []
    minuteBars.value = [...rows].sort((a, b) => String(a.datetime || a.date || '').localeCompare(String(b.datetime || b.date || '')))
    await nextTick()
    renderChart()
  } catch (e: any) {
    // 指数实时卡片仍然可用；分时失败单独提示，不覆盖已有行情。
    error.value = `指数分时获取失败：${e?.message || e}`
  }
}

function renderChart() {
  if (!chartEl.value) return
  chart ??= echarts.init(chartEl.value, 'dark')
  const rows = minuteBars.value
  if (!rows.length) {
    chart.clear()
    return
  }
  const q = selectedQuote.value
  const pre = num(q.pre_close)
  const labels = rows.map((r) => {
    const raw = String(r.datetime || r.date || '')
    return raw.includes('T') ? raw.slice(11, 16) : raw.includes(' ') ? raw.slice(11, 16) : raw.slice(-5)
  })
  const values = rows.map((r) => num(r.close))
  const prices = values.filter((x) => x > 0)
  const minPrice = Math.min(...prices, pre || Infinity)
  const maxPrice = Math.max(...prices, pre || -Infinity)
  const padding = Math.max((maxPrice - minPrice) * 0.12, maxPrice * 0.0015)

  chart.setOption({
    animation: false,
    backgroundColor: 'transparent',
    grid: { left: 58, right: 58, top: 22, bottom: 32 },
    tooltip: { trigger: 'axis', valueFormatter: (v: unknown) => fmt(v, 2) },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: labels,
      axisLabel: { interval: Math.max(0, Math.floor(labels.length / 6) - 1) },
    },
    yAxis: {
      type: 'value',
      scale: true,
      min: Number.isFinite(minPrice) ? minPrice - padding : undefined,
      max: Number.isFinite(maxPrice) ? maxPrice + padding : undefined,
      axisLabel: { formatter: (v: number) => v.toFixed(2) },
    },
    series: [
      {
        name: selected.value.name,
        type: 'line',
        data: values,
        showSymbol: false,
        smooth: false,
        lineStyle: { width: 1.6, color: '#4da3ff' },
        areaStyle: { opacity: 0.08, color: '#4da3ff' },
      },
      ...(pre > 0 ? [{
        name: '昨收',
        type: 'line',
        data: labels.map(() => pre),
        showSymbol: false,
        silent: true,
        lineStyle: { width: 1, type: 'dashed', color: '#6b7280' },
      }] : []),
    ],
  }, true)
}

async function selectIndex(index: IndexDef) {
  selected.value = index
  await loadMinute()
}

async function refreshAll() {
  await loadQuotesAndStat(true)
  await loadMinute()
}

function startTimers() {
  stopTimers()
  if (!autoRefresh.value) return
  quoteTimer = window.setInterval(() => { void loadQuotesAndStat(false) }, 3000)
  minuteTimer = window.setInterval(() => { void loadMinute() }, 15000)
}

function stopTimers() {
  if (quoteTimer !== undefined) window.clearInterval(quoteTimer)
  if (minuteTimer !== undefined) window.clearInterval(minuteTimer)
  quoteTimer = undefined
  minuteTimer = undefined
}

function onResize() { chart?.resize() }

watch(autoRefresh, startTimers)
watch(selectedQuote, () => renderChart(), { deep: true })

onMounted(async () => {
  window.addEventListener('resize', onResize)
  await refreshAll()
  startTimers()
})

onBeforeUnmount(() => {
  stopTimers()
  window.removeEventListener('resize', onResize)
  chart?.dispose()
  chart = null
})
</script>

<template>
  <div class="market-page">
    <section class="topbar">
      <div>
        <h2>A股大盘实时</h2>
        <p>easy_tdx 通达信实时行情 · 指数 3 秒刷新 · 分时 15 秒刷新</p>
      </div>
      <div class="actions">
        <label><input v-model="autoRefresh" type="checkbox" /> 自动刷新</label>
        <span class="time">更新 {{ lastUpdate || '--:--:--' }}</span>
        <button :disabled="loading" @click="refreshAll">{{ loading ? '刷新中…' : '立即刷新' }}</button>
      </div>
    </section>

    <div v-if="error" class="error-box">
      <strong>数据连接异常</strong><span>{{ error }}</span>
      <RouterLink to="/settings">检查服务器 →</RouterLink>
    </div>

    <section class="index-grid">
      <button
        v-for="idx in INDEXES"
        :key="`${idx.market}${idx.code}`"
        :class="['index-card', { active: selected.code === idx.code && selected.market === idx.market }]"
        @click="selectIndex(idx)"
      >
        <div class="card-title"><strong>{{ idx.name }}</strong><small>{{ idx.market }}{{ idx.code }}</small></div>
        <template v-if="quoteFor(idx).price">
          <div :class="['price', tone(changeOf(quoteFor(idx)))]">{{ fmt(quoteFor(idx).price, 2) }}</div>
          <div :class="['change', tone(changeOf(quoteFor(idx)))]">
            <span>{{ changeOf(quoteFor(idx)) >= 0 ? '+' : '' }}{{ fmt(changeOf(quoteFor(idx)), 2) }}</span>
            <b>{{ pctOf(quoteFor(idx)) >= 0 ? '+' : '' }}{{ pctOf(quoteFor(idx)).toFixed(2) }}%</b>
          </div>
          <div class="mini"><span>额 {{ fmtAmount(quoteFor(idx).amount) }}</span><span>{{ quoteFor(idx).server_time || '' }}</span></div>
        </template>
        <div v-else class="no-data">等待实时行情…</div>
      </button>
    </section>

    <section class="breadth" v-if="stat">
      <div class="stat-card"><small>上涨</small><strong class="up">{{ fmt(stat.up_count, 0) }}</strong></div>
      <div class="stat-card"><small>下跌</small><strong class="down">{{ fmt(stat.down_count, 0) }}</strong></div>
      <div class="stat-card"><small>平盘</small><strong>{{ fmt(stat.neutral_count, 0) }}</strong></div>
      <div class="stat-card"><small>涨停</small><strong class="up">{{ fmt(stat.limit_up_count, 0) }}</strong></div>
      <div class="stat-card"><small>跌停</small><strong class="down">{{ fmt(stat.limit_down_count, 0) }}</strong></div>
      <div class="stat-card"><small>总成交额</small><strong>{{ fmtAmount(stat.total_amount) }}</strong></div>
      <div class="stat-card"><small>市场宽度</small><strong :class="tone(marketBreadth - 50)">{{ marketBreadth.toFixed(1) }}%</strong></div>
      <div class="stat-card"><small>股票总数</small><strong>{{ fmt(stat.total_count, 0) }}</strong></div>
    </section>

    <section class="main-grid">
      <article class="chart-panel">
        <div class="panel-head">
          <div>
            <h3>{{ selected.name }} · 今日1分钟</h3>
            <span>{{ selected.market }}{{ selected.code }}</span>
          </div>
          <div v-if="selectedQuote.price" :class="['head-price', tone(changeOf(selectedQuote))]">
            {{ fmt(selectedQuote.price, 2) }} · {{ pctOf(selectedQuote) >= 0 ? '+' : '' }}{{ pctOf(selectedQuote).toFixed(2) }}%
          </div>
        </div>
        <div ref="chartEl" class="chart"></div>
      </article>

      <aside class="detail-panel">
        <h3>{{ selected.name }} 实时数据</h3>
        <div class="detail-row"><span>现价</span><b :class="tone(changeOf(selectedQuote))">{{ fmt(selectedQuote.price, 2) }}</b></div>
        <div class="detail-row"><span>昨收</span><b>{{ fmt(selectedQuote.pre_close, 2) }}</b></div>
        <div class="detail-row"><span>今开</span><b>{{ fmt(selectedQuote.open, 2) }}</b></div>
        <div class="detail-row"><span>最高</span><b class="up">{{ fmt(selectedQuote.high, 2) }}</b></div>
        <div class="detail-row"><span>最低</span><b class="down">{{ fmt(selectedQuote.low, 2) }}</b></div>
        <div class="detail-row"><span>成交量</span><b>{{ fmtAmount(selectedQuote.vol) }}</b></div>
        <div class="detail-row"><span>成交额</span><b>{{ fmtAmount(selectedQuote.amount) }}</b></div>
        <div class="detail-row"><span>服务器时间</span><b>{{ selectedQuote.server_time || '--' }}</b></div>
        <div class="detail-row"><span>停牌家数</span><b>{{ fmt(stat?.suspended_count, 0) }}</b></div>
        <div class="detail-row"><span>总市值</span><b>{{ fmtAmount(stat?.total_market_cap) }}</b></div>
      </aside>
    </section>

    <section class="quote-table">
      <div class="panel-head"><h3>核心指数</h3><span>红涨绿跌</span></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>指数</th><th>现价</th><th>涨跌幅</th><th>涨跌额</th><th>今开</th><th>最高</th><th>最低</th><th>成交额</th><th>时间</th></tr></thead>
          <tbody>
            <tr v-for="idx in INDEXES" :key="`row-${idx.market}${idx.code}`" @click="selectIndex(idx)">
              <td><b>{{ idx.name }}</b><small>{{ idx.market }}{{ idx.code }}</small></td>
              <td :class="tone(changeOf(quoteFor(idx)))">{{ fmt(quoteFor(idx).price, 2) }}</td>
              <td :class="tone(changeOf(quoteFor(idx)))">{{ pctOf(quoteFor(idx)) >= 0 ? '+' : '' }}{{ pctOf(quoteFor(idx)).toFixed(2) }}%</td>
              <td :class="tone(changeOf(quoteFor(idx)))">{{ changeOf(quoteFor(idx)) >= 0 ? '+' : '' }}{{ fmt(changeOf(quoteFor(idx)), 2) }}</td>
              <td>{{ fmt(quoteFor(idx).open, 2) }}</td><td>{{ fmt(quoteFor(idx).high, 2) }}</td><td>{{ fmt(quoteFor(idx).low, 2) }}</td>
              <td>{{ fmtAmount(quoteFor(idx).amount) }}</td><td>{{ quoteFor(idx).server_time || '--' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.market-page { height: 100%; overflow: auto; padding: 16px 18px 28px; box-sizing: border-box; }
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 14px; }
.topbar h2 { margin: 0 0 5px; font-size: 22px; }.topbar p { margin: 0; color: var(--text-dim); font-size: 12px; }
.actions { display: flex; align-items: center; gap: 12px; color: var(--text-dim); font-size: 12px; }.actions label { display: flex; gap: 5px; align-items: center; }.actions button { border: 1px solid var(--border); border-radius: 6px; background: var(--bg-panel); color: var(--text); padding: 7px 12px; cursor: pointer; }.actions button:disabled { opacity: .5; }.time { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.error-box { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; padding: 10px 12px; border: 1px solid #7f1d1d; background: rgba(127,29,29,.14); border-radius: 7px; color: #fca5a5; font-size: 12px; }.error-box span { flex: 1; }.error-box a { color: #fca5a5; }
.index-grid { display: grid; grid-template-columns: repeat(6, minmax(150px, 1fr)); gap: 9px; }
.index-card { min-width: 0; text-align: left; padding: 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); color: var(--text); cursor: pointer; }.index-card:hover,.index-card.active { border-color: var(--accent); }.card-title { display: flex; justify-content: space-between; gap: 8px; align-items: baseline; }.card-title strong { font-size: 13px; }.card-title small { color: var(--text-dim); font-size: 9px; }.price { margin-top: 8px; font-size: 22px; font-weight: 650; letter-spacing: -.4px; }.change { display: flex; gap: 8px; margin-top: 3px; font-size: 12px; }.change b { font-weight: 600; }.mini { display: flex; justify-content: space-between; gap: 6px; margin-top: 8px; color: var(--text-dim); font-size: 9px; }.no-data { padding: 22px 0 8px; color: var(--text-dim); font-size: 11px; }
.up { color: #ef4146 !important; }.down { color: #18a058 !important; }.flat { color: var(--text) !important; }
.breadth { display: grid; grid-template-columns: repeat(8, minmax(100px, 1fr)); gap: 9px; margin-top: 10px; }.stat-card { border: 1px solid var(--border); border-radius: 7px; background: var(--bg-panel); padding: 10px 12px; display: flex; flex-direction: column; gap: 5px; }.stat-card small { color: var(--text-dim); }.stat-card strong { font-size: 17px; }
.main-grid { display: grid; grid-template-columns: minmax(0, 1fr) 260px; gap: 10px; margin-top: 10px; }.chart-panel,.detail-panel,.quote-table { border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); }.chart-panel { min-height: 390px; padding: 13px; }.panel-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; }.panel-head h3 { margin: 0; font-size: 14px; }.panel-head span,.panel-head div > span { color: var(--text-dim); font-size: 10px; }.head-price { font-size: 14px; font-weight: 600; }.chart { height: 340px; margin-top: 8px; }
.detail-panel { padding: 13px 14px; }.detail-panel h3 { margin: 0 0 10px; font-size: 14px; }.detail-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 12px; }.detail-row:last-child { border-bottom: 0; }.detail-row span { color: var(--text-dim); }.detail-row b { font-weight: 550; }
.quote-table { margin-top: 10px; padding: 13px; }.table-wrap { overflow: auto; margin-top: 10px; }table { width: 100%; border-collapse: collapse; font-size: 11px; }th { color: var(--text-dim); font-weight: 500; text-align: right; padding: 7px 8px; border-bottom: 1px solid var(--border); }th:first-child,td:first-child { text-align: left; }td { text-align: right; padding: 8px; border-bottom: 1px solid var(--border); }tbody tr { cursor: pointer; }tbody tr:hover { background: rgba(255,255,255,.025); }td:first-child b { display: block; }td:first-child small { display: block; color: var(--text-dim); margin-top: 2px; font-size: 9px; }
@media (max-width: 1200px) { .index-grid { grid-template-columns: repeat(3, 1fr); }.breadth { grid-template-columns: repeat(4, 1fr); } }
@media (max-width: 760px) { .market-page { padding: 12px; }.topbar { align-items: flex-start; flex-direction: column; }.actions { flex-wrap: wrap; }.index-grid { grid-template-columns: repeat(2, 1fr); }.breadth { grid-template-columns: repeat(2, 1fr); }.main-grid { grid-template-columns: 1fr; }.detail-panel { order: -1; }.chart { height: 300px; } }
</style>
