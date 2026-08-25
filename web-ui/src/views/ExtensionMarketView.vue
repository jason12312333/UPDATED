<script setup lang="ts">
import { ref } from 'vue'

import DataGrid from '../components/DataGrid.vue'

type Row = Record<string, any>
type Mode = 'quote' | 'bars' | 'minute' | 'transaction' | 'mac-server'

const market = ref('HK_MAIN_BOARD')
const code = ref('00700')
const category = ref('DAY')
const mode = ref<Mode>('quote')
const rows = ref<Row[]>([])
const loading = ref(false)
const error = ref('')
const title = ref('扩展市场实时报价')

async function get(url: string): Promise<any> {
  const res = await fetch(url)
  const text = await res.text()
  let data: any
  try { data = JSON.parse(text) } catch { data = text }
  if (!res.ok) throw new Error(typeof data === 'string' ? data : JSON.stringify(data))
  return data
}

async function load() {
  loading.value = true
  error.value = ''
  rows.value = []
  try {
    let resp: any
    if (mode.value === 'mac-server') {
      title.value = 'MAC 服务器交易时段信息'
      resp = await get('/api/v1/mac/server-info')
    } else {
      const base = `market=${encodeURIComponent(market.value)}&code=${encodeURIComponent(code.value)}`
      if (mode.value === 'quote') {
        title.value = `${market.value} ${code.value} 实时报价`
        resp = await get(`/api/v1/ex/quote?${base}`)
      } else if (mode.value === 'bars') {
        title.value = `${market.value} ${code.value} K线`
        resp = await get(`/api/v1/ex/bars?${base}&category=${category.value}&start=0&count=500`)
      } else if (mode.value === 'minute') {
        title.value = `${market.value} ${code.value} 分时`
        resp = await get(`/api/v1/ex/minute?${base}`)
      } else {
        title.value = `${market.value} ${code.value} 逐笔成交`
        resp = await get(`/api/v1/ex/transaction?${base}&start=0&count=1000`)
      }
    }
    rows.value = resp.data || []
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

function setMode(next: Mode) {
  mode.value = next
  void load()
}

void load()
</script>

<template>
  <div class="ex-page">
    <section class="toolbar">
      <div><h2>港股 / 美股 / 期货</h2><p>easy_tdx 扩展市场客户端：实时报价、K线、分时、逐笔成交与 MAC 服务器信息。</p></div>
      <div class="inputs" v-if="mode !== 'mac-server'">
        <input v-model.trim="market" placeholder="HK_MAIN_BOARD" />
        <input v-model.trim="code" placeholder="00700" />
        <select v-model="category"><option>DAY</option><option>WEEK</option><option>MONTH</option><option>MIN_1</option><option>MIN_5</option><option>MIN_15</option><option>MIN_30</option><option>MIN_60</option></select>
        <button @click="load">查询</button>
      </div>
    </section>

    <nav class="tabs">
      <button :class="{ active: mode === 'quote' }" @click="setMode('quote')">实时报价</button>
      <button :class="{ active: mode === 'bars' }" @click="setMode('bars')">K线</button>
      <button :class="{ active: mode === 'minute' }" @click="setMode('minute')">分时</button>
      <button :class="{ active: mode === 'transaction' }" @click="setMode('transaction')">逐笔</button>
      <button :class="{ active: mode === 'mac-server' }" @click="setMode('mac-server')">MAC服务器</button>
    </nav>

    <div v-if="error" class="error"><strong>扩展市场连接异常</strong><span>{{ error }}</span><small>如果这里返回 503，请先检查扩展市场服务器是否可连接。</small></div>
    <DataGrid :title="title" :rows="rows" :loading="loading" />
  </div>
</template>

<style scoped>
.ex-page { height: 100%; overflow: auto; padding: 16px 18px 28px; box-sizing: border-box; }.toolbar { display: flex; justify-content: space-between; align-items: center; gap: 18px; }.toolbar h2 { margin: 0 0 5px; font-size: 21px; }.toolbar p { margin: 0; color: var(--text-dim); font-size: 11px; }.inputs { display: flex; gap: 7px; align-items: center; }.inputs input,.inputs select { border: 1px solid var(--border); background: var(--bg-panel); color: var(--text); border-radius: 6px; padding: 7px 9px; }.inputs input:first-child { width: 160px; }.inputs input:nth-child(2) { width: 90px; }.inputs button { border: 0; border-radius: 6px; background: var(--accent); color: white; padding: 8px 13px; cursor: pointer; }.tabs { display: flex; gap: 6px; margin: 14px 0 10px; }.tabs button { border: 1px solid var(--border); background: var(--bg-panel); color: var(--text-dim); border-radius: 6px; padding: 7px 11px; cursor: pointer; }.tabs button.active { color: var(--accent); border-color: var(--accent); }.error { display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; padding: 10px 12px; color: #fca5a5; border: 1px solid #7f1d1d; border-radius: 7px; background: rgba(127,29,29,.12); }.error small { color: var(--text-dim); }
@media (max-width: 900px) { .toolbar { align-items: flex-start; flex-direction: column; }.inputs { flex-wrap: wrap; width: 100%; } }
</style>
