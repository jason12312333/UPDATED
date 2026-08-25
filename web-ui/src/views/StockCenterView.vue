<script setup lang="ts">
import { computed, ref } from 'vue'

import DataGrid from '../components/DataGrid.vue'
import KlineChart from '../components/KlineChart.vue'
import { detectMarket } from '../market'
import type { Bar } from '../types'

type Row = Record<string, any>
type TabKey = 'quote' | 'kline' | 'minute' | 'transaction' | 'fund' | 'finance' | 'company' | 'announcement' | 'report' | 'indicator' | 'chanlun' | 'board'

const tabs: Array<{ key: TabKey; label: string }> = [
  { key: 'quote', label: '实时行情' },
  { key: 'kline', label: 'K线' },
  { key: 'minute', label: '分时' },
  { key: 'transaction', label: '逐笔' },
  { key: 'fund', label: '资金流' },
  { key: 'finance', label: '财务/除权' },
  { key: 'company', label: '公司资料' },
  { key: 'announcement', label: '公告' },
  { key: 'report', label: '财报三表' },
  { key: 'indicator', label: '技术指标' },
  { key: 'chanlun', label: '缠论' },
  { key: 'board', label: '所属板块' },
]

const code = ref('000001')
const active = ref<TabKey>('quote')
const category = ref('DAY')
const count = ref(300)
const reportType = ref('lrb')
const indicatorsText = ref('MACD,KDJ,RSI,BOLL')
const rows = ref<Row[]>([])
const secondaryRows = ref<Row[]>([])
const rawResult = ref<any>(null)
const loading = ref(false)
const error = ref('')
const title = ref('实时行情')

const market = computed(() => detectMarket(code.value))
const symbol = computed(() => `${market.value}${code.value}`)

const chartBars = computed<Bar[]>(() => rows.value
  .filter((r) => r.open !== undefined && r.close !== undefined && r.high !== undefined && r.low !== undefined)
  .map((r) => ({
    datetime: String(r.datetime || r.date || '').slice(0, 19).replace(' ', 'T') + (String(r.datetime || r.date || '').length <= 10 ? 'T00:00:00' : ''),
    open: Number(r.open || 0),
    high: Number(r.high || 0),
    low: Number(r.low || 0),
    close: Number(r.close || 0),
    vol: Number(r.vol || r.volume || 0),
    amount: Number(r.amount || 0),
  })))

async function request(url: string, init?: RequestInit): Promise<any> {
  const res = await fetch(url, init)
  const text = await res.text()
  let data: any = null
  try { data = text ? JSON.parse(text) : null } catch { data = text }
  if (!res.ok) throw new Error(typeof data === 'string' ? data : JSON.stringify(data))
  return data
}

function qs(extra: Record<string, string | number> = {}): string {
  const p = new URLSearchParams({ market: market.value, code: code.value })
  for (const [k, v] of Object.entries(extra)) p.set(k, String(v))
  return p.toString()
}

async function fetchBars(): Promise<Row[]> {
  const resp = await request(`/api/v1/bars?${qs({ category: category.value, start: 0, count: count.value })}`)
  return Array.isArray(resp.data) ? resp.data : []
}

async function run() {
  if (!/^\d{6}$/.test(code.value)) {
    error.value = '请输入 6 位证券代码'
    return
  }
  loading.value = true
  error.value = ''
  rows.value = []
  secondaryRows.value = []
  rawResult.value = null
  try {
    if (active.value === 'quote') {
      title.value = `${symbol.value} 实时行情`
      const resp = await request('/api/v1/quotes', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stocks: [{ market: market.value, code: code.value }] }),
      })
      rows.value = resp.data || []
    } else if (active.value === 'kline') {
      title.value = `${symbol.value} ${category.value} K线`
      rows.value = await fetchBars()
    } else if (active.value === 'minute') {
      title.value = `${symbol.value} 今日分时`
      const resp = await request(`/api/v1/minute?${qs()}`)
      rows.value = resp.data || []
    } else if (active.value === 'transaction') {
      title.value = `${symbol.value} 今日逐笔成交`
      const resp = await request(`/api/v1/transaction?${qs({ start: 0, count: 800 })}`)
      rows.value = resp.data || []
    } else if (active.value === 'fund') {
      title.value = `${symbol.value} 资金流向`
      const [standard, mac] = await Promise.allSettled([
        request(`/api/v1/fund-flow?${qs()}`),
        request(`/api/v1/mac/capital-flow?${qs()}`),
      ])
      if (standard.status === 'fulfilled') rows.value = standard.value.data || []
      if (mac.status === 'fulfilled') secondaryRows.value = mac.value.data || []
      if (!rows.value.length && !secondaryRows.value.length) throw new Error('标准资金流与 MAC 资金流均不可用')
    } else if (active.value === 'finance') {
      title.value = `${symbol.value} 财务数据`
      const [finance, xdxr, symbolInfo] = await Promise.allSettled([
        request(`/api/v1/finance?${qs()}`),
        request(`/api/v1/xdxr?${qs()}`),
        request(`/api/v1/mac/symbol-info?${qs()}`),
      ])
      if (finance.status === 'fulfilled') rows.value = finance.value.data || []
      if (xdxr.status === 'fulfilled') secondaryRows.value = xdxr.value.data || []
      if (symbolInfo.status === 'fulfilled') rawResult.value = symbolInfo.value.data || []
    } else if (active.value === 'company') {
      title.value = `${symbol.value} 公司资料目录`
      const resp = await request(`/api/v1/company/category?${qs()}`)
      rows.value = resp.data || []
    } else if (active.value === 'announcement') {
      title.value = `${symbol.value} 公司公告`
      const resp = await request(`/api/v1/announcements?code=${encodeURIComponent(code.value)}&count=50&page=1`)
      rows.value = resp.data || []
    } else if (active.value === 'report') {
      title.value = `${symbol.value} 财报三表`
      const resp = await request(`/api/v1/sina/financial-report?code=${encodeURIComponent(code.value)}&type=${reportType.value}&num=12`)
      rows.value = resp.data || []
    } else if (active.value === 'indicator') {
      title.value = `${symbol.value} 技术指标`
      const bars = await fetchBars()
      const indicators = indicatorsText.value.split(',').map((x) => x.trim()).filter(Boolean)
      const resp = await request('/api/v1/indicator/compute', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: bars, indicators, keep_ohlcv: true, tail: 120 }),
      })
      rows.value = resp.data || []
    } else if (active.value === 'chanlun') {
      title.value = `${symbol.value} 缠论分析`
      rawResult.value = await request('/api/v1/chanlun/analyze', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ market: market.value, code: code.value, category: category.value, count: Math.min(count.value, 800), start: 0 }),
      })
    } else if (active.value === 'board') {
      title.value = `${symbol.value} 所属板块`
      const resp = await request(`/api/v1/board-mac/belong?${qs()}`)
      rows.value = resp.data || []
    }
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

async function openCompanyRow(row: Row) {
  if (active.value !== 'company') return
  const filename = String(row.filename || row.file_name || row.name || '')
  if (!filename) return
  try {
    const resp = await request(`/api/v1/company/content?${qs({ filename, offset: 0, length: 12000 })}`)
    rawResult.value = resp.content || resp
  } catch (e: any) {
    error.value = e?.message || String(e)
  }
}

function selectTab(key: TabKey) {
  active.value = key
  void run()
}

void run()
</script>

<template>
  <div class="stock-page">
    <section class="toolbar">
      <div><h2>个股中心</h2><p>一只股票集中查看实时行情、K线、资金、财务、公告、指标、缠论与板块。</p></div>
      <div class="search-box">
        <span>{{ market }}</span>
        <input v-model.trim="code" maxlength="6" placeholder="000001" @keyup.enter="run" />
        <select v-model="category"><option>DAY</option><option>WEEK</option><option>MONTH</option><option>MIN_1</option><option>MIN_5</option><option>MIN_15</option><option>MIN_30</option><option>MIN_60</option></select>
        <input v-model.number="count" class="count" type="number" min="20" max="800" />
        <button @click="run">查询</button>
      </div>
    </section>

    <nav class="tabs">
      <button v-for="tab in tabs" :key="tab.key" :class="{ active: active === tab.key }" @click="selectTab(tab.key)">{{ tab.label }}</button>
    </nav>

    <section v-if="active === 'report' || active === 'indicator'" class="options">
      <label v-if="active === 'report'">报表<select v-model="reportType"><option value="lrb">利润表</option><option value="fzb">资产负债表</option><option value="llb">现金流量表</option></select></label>
      <label v-if="active === 'indicator'" class="wide">指标<input v-model="indicatorsText" placeholder="MACD,KDJ,RSI,BOLL" /></label>
      <button @click="run">重新计算</button>
    </section>

    <div v-if="error" class="error">{{ error }}</div>

    <section v-if="active === 'kline' && chartBars.length" class="chart-box">
      <KlineChart :bars="chartBars" :trades="[]" />
    </section>

    <DataGrid v-if="rows.length || loading" :title="title" :rows="rows" :loading="loading" @row-click="openCompanyRow" />
    <DataGrid v-if="secondaryRows.length" :title="active === 'fund' ? 'MAC 主力/散户资金流' : '除权除息历史'" :rows="secondaryRows" />

    <section v-if="rawResult !== null" class="raw-panel">
      <h3>{{ active === 'company' ? '公司资料正文' : active === 'chanlun' ? '缠论结构化结果' : '补充数据' }}</h3>
      <pre>{{ typeof rawResult === 'string' ? rawResult : JSON.stringify(rawResult, null, 2) }}</pre>
    </section>

    <div v-if="!loading && !error && !rows.length && rawResult === null" class="empty">当前功能暂无返回数据。</div>
  </div>
</template>

<style scoped>
.stock-page { height: 100%; overflow: auto; padding: 16px 18px 28px; box-sizing: border-box; }.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 18px; }.toolbar h2 { margin: 0 0 5px; font-size: 21px; }.toolbar p { margin: 0; color: var(--text-dim); font-size: 11px; }.search-box { display: flex; gap: 7px; align-items: center; }.search-box span { color: var(--accent); font-size: 11px; font-weight: 700; }.search-box input,.search-box select,.options input,.options select { border: 1px solid var(--border); background: var(--bg-panel); color: var(--text); border-radius: 6px; padding: 7px 9px; outline: none; }.search-box input { width: 94px; }.search-box .count { width: 64px; }.search-box button,.options button { border: 0; border-radius: 6px; padding: 8px 14px; background: var(--accent); color: #fff; cursor: pointer; }.tabs { display: flex; gap: 6px; margin: 14px 0 10px; overflow-x: auto; }.tabs button { white-space: nowrap; border: 1px solid var(--border); background: var(--bg-panel); color: var(--text-dim); border-radius: 6px; padding: 7px 10px; cursor: pointer; }.tabs button.active { border-color: var(--accent); color: var(--accent); }.options { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding: 10px; border: 1px solid var(--border); border-radius: 7px; background: var(--bg-panel); }.options label { display: flex; gap: 7px; align-items: center; color: var(--text-dim); font-size: 11px; }.options .wide { flex: 1; }.options .wide input { flex: 1; }.error { margin-bottom: 10px; padding: 10px 12px; border: 1px solid #7f1d1d; background: rgba(127,29,29,.12); color: #fca5a5; border-radius: 7px; font-size: 11px; }.chart-box { height: 430px; margin-bottom: 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); overflow: hidden; }.chart-box :deep(.chart) { height: 100%; }.raw-panel { margin-top: 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); padding: 13px; }.raw-panel h3 { margin: 0 0 10px; font-size: 13px; }.raw-panel pre { margin: 0; max-height: 560px; overflow: auto; white-space: pre-wrap; color: var(--text-dim); font-size: 10px; line-height: 1.55; }.empty { padding: 60px 0; text-align: center; color: var(--text-dim); }
@media (max-width: 900px) { .toolbar { align-items: flex-start; flex-direction: column; }.search-box { width: 100%; flex-wrap: wrap; } }
</style>
