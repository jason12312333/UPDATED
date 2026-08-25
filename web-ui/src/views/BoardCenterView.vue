<script setup lang="ts">
import { onMounted, ref } from 'vue'

import DataGrid from '../components/DataGrid.vue'

type Row = Record<string, any>

const boardType = ref('HY')
const days = ref(20)
const topN = ref(50)
const ranking = ref<Row[]>([])
const changeRanking = ref<Row[]>([])
const members = ref<Row[]>([])
const summary = ref<any>(null)
const selectedSymbol = ref('')
const selectedName = ref('')
const loading = ref(false)
const error = ref('')

async function get(url: string): Promise<any> {
  const res = await fetch(url)
  const text = await res.text()
  let data: any
  try { data = JSON.parse(text) } catch { data = text }
  if (!res.ok) throw new Error(typeof data === 'string' ? data : JSON.stringify(data))
  return data
}

async function loadRankings() {
  loading.value = true
  error.value = ''
  try {
    const [r1, r2] = await Promise.all([
      get(`/api/v1/board-mac/ranking?board_type=${boardType.value}&top_n=${topN.value}&sort_by=change_pct&ascending=false`),
      get(`/api/v1/board-mac/change-ranking?board_type=${boardType.value}&days=${days.value}&top_n=${topN.value}&ascending=false`),
    ])
    ranking.value = r1.data || []
    changeRanking.value = r2.data || []
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

function boardSymbolOf(row: Row): string {
  return String(row.board_symbol || row.symbol || row.code || row.block_code || '')
}

function boardNameOf(row: Row): string {
  return String(row.board_name || row.name || row.block_name || boardSymbolOf(row))
}

async function selectBoard(row: Row) {
  const symbol = boardSymbolOf(row)
  if (!symbol) return
  selectedSymbol.value = symbol
  selectedName.value = boardNameOf(row)
  error.value = ''
  try {
    const [m, s] = await Promise.allSettled([
      get(`/api/v1/board-mac/members?board_symbol=${encodeURIComponent(symbol)}&count=500&sort_type=CHANGE_PCT&sort_order=DESC`),
      get(`/api/v1/board-mac/summary?board_symbol=${encodeURIComponent(symbol)}&sort_type=CHANGE_PCT&sort_order=DESC`),
    ])
    members.value = m.status === 'fulfilled' ? (m.value.data || []) : []
    summary.value = s.status === 'fulfilled' ? (s.value.data || s.value) : null
  } catch (e: any) {
    error.value = e?.message || String(e)
  }
}

onMounted(loadRankings)
</script>

<template>
  <div class="board-page">
    <section class="toolbar">
      <div><h2>板块中心</h2><p>行业 / 概念 / 风格 / 地区实时排名、N日强弱、板块摘要与成分股。</p></div>
      <div class="filters">
        <select v-model="boardType"><option value="HY">行业</option><option value="HY2">二级行业</option><option value="GN">概念</option><option value="FG">风格</option><option value="DQ">地区</option></select>
        <label>N日 <input v-model.number="days" type="number" min="1" max="250" /></label>
        <label>TOP <input v-model.number="topN" type="number" min="10" max="200" /></label>
        <button @click="loadRankings">刷新排名</button>
      </div>
    </section>

    <div v-if="error" class="error">{{ error }}</div>

    <section class="rank-grid">
      <DataGrid title="今日板块涨幅排名" :rows="ranking" :loading="loading" @row-click="selectBoard" />
      <DataGrid :title="`${days}日板块强弱排名`" :rows="changeRanking" :loading="loading" @row-click="selectBoard" />
    </section>

    <section v-if="selectedSymbol" class="selected-head">
      <div><h3>{{ selectedName }}</h3><span>{{ selectedSymbol }}</span></div>
      <small>点击上方任一板块切换</small>
    </section>

    <section v-if="summary" class="summary"><pre>{{ JSON.stringify(summary, null, 2) }}</pre></section>
    <DataGrid v-if="selectedSymbol" :title="`${selectedName} · 成分股（按涨幅排序）`" :rows="members" />
  </div>
</template>

<style scoped>
.board-page { height: 100%; overflow: auto; padding: 16px 18px 28px; box-sizing: border-box; }.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 18px; margin-bottom: 12px; }.toolbar h2 { margin: 0 0 5px; font-size: 21px; }.toolbar p { margin: 0; color: var(--text-dim); font-size: 11px; }.filters { display: flex; gap: 8px; align-items: center; color: var(--text-dim); font-size: 11px; }.filters select,.filters input { border: 1px solid var(--border); background: var(--bg-panel); color: var(--text); border-radius: 6px; padding: 7px 8px; }.filters input { width: 55px; }.filters button { border: 0; border-radius: 6px; background: var(--accent); color: white; padding: 8px 13px; cursor: pointer; }.rank-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }.error { margin-bottom: 10px; padding: 10px 12px; color: #fca5a5; border: 1px solid #7f1d1d; border-radius: 7px; background: rgba(127,29,29,.12); }.selected-head { display: flex; justify-content: space-between; align-items: center; margin: 12px 0 8px; padding: 11px 13px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); }.selected-head h3 { margin: 0; font-size: 15px; }.selected-head span,.selected-head small { color: var(--text-dim); font-size: 10px; }.summary { margin-bottom: 10px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); padding: 10px 13px; }.summary pre { margin: 0; max-height: 240px; overflow: auto; color: var(--text-dim); font-size: 10px; white-space: pre-wrap; }
@media (max-width: 980px) { .toolbar { align-items: flex-start; flex-direction: column; }.filters { flex-wrap: wrap; }.rank-grid { grid-template-columns: 1fr; } }
</style>
