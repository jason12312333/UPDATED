<script setup lang="ts">
import { onMounted, ref } from 'vue'

import DataGrid from '../components/DataGrid.vue'

type Row = Record<string, any>
type Mode = 'quote' | 'strength' | 'unusual' | 'security'

const mode = ref<Mode>('quote')
const category = ref('A')
const topN = ref(100)
const preset = ref('balanced')
const universe = ref('all')
const minAmount = ref(0)
const market = ref('SH')
const rows = ref<Row[]>([])
const loading = ref(false)
const error = ref('')
const title = ref('全市场涨幅榜')

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
    if (mode.value === 'quote') {
      title.value = '全市场实时排行'
      resp = await get(`/api/v1/mac/quote-list?category=${category.value}&start=0&count=${topN.value}&sort_type=CHANGE_PCT&sort_order=DESC`)
    } else if (mode.value === 'strength') {
      title.value = '本地通达信强势股排名'
      resp = await get(`/api/v1/market/strength?preset=${preset.value}&top_n=${topN.value}&universe=${universe.value}&min_amount=${minAmount.value}`)
    } else if (mode.value === 'unusual') {
      title.value = `${market.value} 市场异动`
      resp = await get(`/api/v1/mac/unusual?market=${market.value}&start=0&count=${Math.min(topN.value, 500)}`)
    } else {
      title.value = '沪深A股证券列表'
      resp = await get('/api/v1/security/list-all?pages=6')
    }
    rows.value = resp.data || []
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

function chooseMode(next: Mode) {
  mode.value = next
  void load()
}

onMounted(load)
</script>

<template>
  <div class="scanner-page">
    <section class="toolbar">
      <div><h2>全市场扫描</h2><p>实时涨幅排行、本地历史强势排名、市场异动和证券全表直接使用。</p></div>
      <button @click="load">立即刷新</button>
    </section>

    <nav class="tabs">
      <button :class="{ active: mode === 'quote' }" @click="chooseMode('quote')">实时排行</button>
      <button :class="{ active: mode === 'strength' }" @click="chooseMode('strength')">强势股排名</button>
      <button :class="{ active: mode === 'unusual' }" @click="chooseMode('unusual')">市场异动</button>
      <button :class="{ active: mode === 'security' }" @click="chooseMode('security')">证券列表</button>
    </nav>

    <section class="filters">
      <template v-if="mode === 'quote'">
        <label>范围<select v-model="category"><option>A</option><option>SH</option><option>SZ</option><option>CYB</option><option>KCB</option><option>BJ</option></select></label>
      </template>
      <template v-if="mode === 'strength'">
        <label>模型<select v-model="preset"><option value="steady">稳健</option><option value="breakout">短线爆发</option><option value="balanced">均衡</option></select></label>
        <label>市场<select v-model="universe"><option value="all">全部</option><option value="sh">沪市</option><option value="sz">深市</option></select></label>
        <label>5日日均成交额下限<input v-model.number="minAmount" type="number" min="0" step="1000000" /></label>
      </template>
      <template v-if="mode === 'unusual'">
        <label>市场<select v-model="market"><option>SH</option><option>SZ</option></select></label>
      </template>
      <label v-if="mode !== 'security'">数量<input v-model.number="topN" type="number" min="10" max="5000" /></label>
      <button @click="load">应用</button>
    </section>

    <div v-if="error" class="error">{{ error }}</div>
    <DataGrid :title="title" :rows="rows" :loading="loading" />
  </div>
</template>

<style scoped>
.scanner-page { height: 100%; overflow: auto; padding: 16px 18px 28px; box-sizing: border-box; }.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 18px; }.toolbar h2 { margin: 0 0 5px; font-size: 21px; }.toolbar p { margin: 0; color: var(--text-dim); font-size: 11px; }.toolbar > button,.filters button { border: 0; border-radius: 6px; background: var(--accent); color: #fff; padding: 8px 13px; cursor: pointer; }.tabs { display: flex; gap: 6px; margin: 14px 0 10px; }.tabs button { border: 1px solid var(--border); background: var(--bg-panel); color: var(--text-dim); border-radius: 6px; padding: 7px 11px; cursor: pointer; }.tabs button.active { color: var(--accent); border-color: var(--accent); }.filters { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 10px; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); }.filters label { display: flex; align-items: center; gap: 6px; color: var(--text-dim); font-size: 11px; }.filters input,.filters select { border: 1px solid var(--border); background: var(--bg); color: var(--text); border-radius: 5px; padding: 6px 8px; }.filters input { width: 110px; }.error { margin-bottom: 10px; padding: 10px 12px; color: #fca5a5; border: 1px solid #7f1d1d; border-radius: 7px; background: rgba(127,29,29,.12); }
</style>
