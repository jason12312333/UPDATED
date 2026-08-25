<script setup lang="ts">
import { computed, ref } from 'vue'

import DataGrid from '../components/DataGrid.vue'
import KlineChart from '../components/KlineChart.vue'
import { detectMarket } from '../market'
import type { Bar } from '../types'

type Row = Record<string, any>

const vipdoc = ref('')
const blockDir = ref('')
const code = ref('000001')
const rows = ref<Row[]>([])
const blocks = ref<Row[]>([])
const status = ref<Record<string, any> | null>(null)
const loading = ref(false)
const error = ref('')

const market = computed(() => detectMarket(code.value) === 'SH' ? 'SH' : 'SZ')
const chartBars = computed<Bar[]>(() => rows.value.map((r) => ({
  datetime: `${String(r.date || '').slice(0, 10)}T00:00:00`,
  open: Number(r.open || 0), high: Number(r.high || 0), low: Number(r.low || 0), close: Number(r.close || 0),
  vol: Number(r.vol || 0), amount: Number(r.amount || 0),
})))

async function get(url: string): Promise<any> {
  const res = await fetch(url)
  const text = await res.text()
  let data: any
  try { data = JSON.parse(text) } catch { data = text }
  if (!res.ok) throw new Error(typeof data === 'string' ? data : JSON.stringify(data))
  return data
}

async function detect() {
  error.value = ''
  try {
    const q = vipdoc.value ? `?vipdoc=${encodeURIComponent(vipdoc.value)}` : ''
    status.value = await get(`/api/v1/offline/status${q}`)
    if (!vipdoc.value && status.value?.vipdoc) vipdoc.value = String(status.value.vipdoc)
  } catch (e: any) { error.value = e?.message || String(e) }
}

async function loadDaily() {
  loading.value = true
  error.value = ''
  try {
    const p = new URLSearchParams({ market: market.value, code: code.value, count: '800' })
    if (vipdoc.value) p.set('vipdoc', vipdoc.value)
    const resp = await get(`/api/v1/offline/daily?${p}`)
    rows.value = resp.data || []
  } catch (e: any) { error.value = e?.message || String(e) }
  finally { loading.value = false }
}

async function loadBlocks() {
  error.value = ''
  if (!blockDir.value) { error.value = '请输入自定义板块目录，例如 T0002\\blocknew'; return }
  try {
    const resp = await get(`/api/v1/offline/customer-blocks?block_dir=${encodeURIComponent(blockDir.value)}`)
    blocks.value = resp.data || []
  } catch (e: any) { error.value = e?.message || String(e) }
}

void detect()
</script>

<template>
  <div class="offline-page">
    <section class="toolbar"><div><h2>本地通达信数据</h2><p>直接读取你电脑上的 vipdoc/.day 和自定义板块，不走网络行情。</p></div><button @click="detect">重新检测</button></section>

    <section class="status-box">
      <label>vipdoc 路径<input v-model="vipdoc" placeholder="H:\\tdx1\\vipdoc" /></label>
      <div v-if="status" class="status"><span>自动检测：{{ status.auto_detected ? '成功' : '未找到' }}</span><span>TDX_HOME：{{ status.tdx_home || '--' }}</span><span>vipdoc：{{ status.vipdoc_exists ? '可用' : '不可用' }}</span></div>
    </section>

    <div v-if="error" class="error">{{ error }}</div>

    <section class="query-row">
      <div><strong>本地日线</strong><span>{{ market }}</span><input v-model.trim="code" maxlength="6" placeholder="000001" /><button @click="loadDaily">读取 .day</button></div>
      <div><strong>自定义板块</strong><input v-model="blockDir" placeholder="H:\\tdx1\\T0002\\blocknew" /><button @click="loadBlocks">读取板块</button></div>
    </section>

    <section v-if="chartBars.length" class="chart-box"><KlineChart :bars="chartBars" :trades="[]" /></section>
    <DataGrid title="本地 .day 日线" :rows="rows" :loading="loading" />
    <div class="spacer"></div>
    <DataGrid v-if="blocks.length" title="本地自定义板块" :rows="blocks" />
  </div>
</template>

<style scoped>
.offline-page { height: 100%; overflow: auto; padding: 16px 18px 28px; box-sizing: border-box; }.toolbar { display:flex;align-items:center;justify-content:space-between;gap:18px }.toolbar h2{margin:0 0 5px;font-size:21px}.toolbar p{margin:0;color:var(--text-dim);font-size:11px}.toolbar button,.query-row button{border:0;border-radius:6px;background:var(--accent);color:#fff;padding:8px 13px;cursor:pointer}.status-box{margin:12px 0;padding:11px 13px;border:1px solid var(--border);border-radius:8px;background:var(--bg-panel)}.status-box label{display:flex;align-items:center;gap:10px;font-size:11px;color:var(--text-dim)}.status-box input{flex:1;border:1px solid var(--border);background:var(--bg);color:var(--text);border-radius:6px;padding:7px 9px}.status{display:flex;gap:18px;flex-wrap:wrap;margin-top:9px;color:var(--text-dim);font-size:10px}.query-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px}.query-row>div{display:flex;align-items:center;gap:7px;padding:10px;border:1px solid var(--border);border-radius:8px;background:var(--bg-panel)}.query-row strong{font-size:12px}.query-row span{color:var(--accent);font-size:10px}.query-row input{min-width:0;flex:1;border:1px solid var(--border);background:var(--bg);color:var(--text);border-radius:6px;padding:7px 9px}.error{margin-bottom:10px;padding:10px 12px;color:#fca5a5;border:1px solid #7f1d1d;border-radius:7px;background:rgba(127,29,29,.12)}.chart-box{height:420px;margin-bottom:10px;border:1px solid var(--border);border-radius:8px;background:var(--bg-panel);overflow:hidden}.chart-box :deep(.chart){height:100%}.spacer{height:10px}@media(max-width:900px){.query-row{grid-template-columns:1fr}.query-row>div{flex-wrap:wrap}.status-box label{align-items:flex-start;flex-direction:column}.status-box input{width:100%;box-sizing:border-box}}
</style>
