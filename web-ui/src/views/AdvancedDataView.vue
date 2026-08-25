<script setup lang="ts">
import { ref } from 'vue'

import DataGrid from '../components/DataGrid.vue'
import { detectMarket } from '../market'

type Row = Record<string, any>
type Mode = 'history-minute' | 'history-txn' | 'history-fund' | 'auction' | 'block' | 'financial-files' | 'indicators'

const mode = ref<Mode>('history-minute')
const code = ref('000001')
const date = ref(new Date().toISOString().slice(0, 10).replaceAll('-', ''))
const blockFile = ref('block_gn.dat')
const rows = ref<Row[]>([])
const secondary = ref<Row[]>([])
const title = ref('历史分时')
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

async function load() {
  loading.value = true
  error.value = ''
  rows.value = []
  secondary.value = []
  try {
    const market = detectMarket(code.value)
    if (mode.value === 'history-minute') {
      title.value = `${code.value} ${date.value} 历史分时`
      const r = await get(`/api/v1/minute/history?market=${market}&code=${code.value}&date=${date.value}`)
      rows.value = r.data || []
    } else if (mode.value === 'history-txn') {
      title.value = `${code.value} ${date.value} 历史逐笔`
      const r = await get(`/api/v1/transaction/history?market=${market}&code=${code.value}&date=${date.value}&start=0&count=800`)
      rows.value = r.data || []
    } else if (mode.value === 'history-fund') {
      title.value = `${code.value} 历史资金流`
      const r = await get(`/api/v1/fund-flow/history?market=${market}&code=${code.value}&start=0&count=300`)
      rows.value = r.data || []
    } else if (mode.value === 'auction') {
      title.value = `${code.value} 集合竞价`
      const r = await get(`/api/v1/mac/auction?market=${market}&code=${code.value}`)
      rows.value = r.data || []
    } else if (mode.value === 'block') {
      title.value = `${blockFile.value} 板块文件`
      const r = await get(`/api/v1/block?filename=${encodeURIComponent(blockFile.value)}`)
      rows.value = r.data || []
    } else if (mode.value === 'financial-files') {
      title.value = '专业财务文件列表'
      const r = await get('/api/v1/financial/file-list')
      rows.value = r.data || []
    } else {
      title.value = '可用技术指标清单'
      const r = await get('/api/v1/indicator/list')
      rows.value = Array.isArray(r) ? r : []
    }
  } catch (e: any) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

async function rowClick(row: Row) {
  if (mode.value !== 'financial-files') return
  const filename = String(row.filename || row.file || row.name || '')
  if (!filename) return
  try {
    const r = await get(`/api/v1/financial/records?filename=${encodeURIComponent(filename)}`)
    secondary.value = r.data || []
  } catch (e: any) { error.value = e?.message || String(e) }
}

function setMode(next: Mode) { mode.value = next; void load() }
void load()
</script>

<template>
  <div class="advanced-page">
    <section class="toolbar"><div><h2>高级数据中心</h2><p>把 easy_tdx 其余数据能力从 API 变成可点击功能。</p></div><button @click="load">刷新</button></section>
    <nav class="tabs">
      <button :class="{active:mode==='history-minute'}" @click="setMode('history-minute')">历史分时</button>
      <button :class="{active:mode==='history-txn'}" @click="setMode('history-txn')">历史逐笔</button>
      <button :class="{active:mode==='history-fund'}" @click="setMode('history-fund')">历史资金流</button>
      <button :class="{active:mode==='auction'}" @click="setMode('auction')">集合竞价</button>
      <button :class="{active:mode==='block'}" @click="setMode('block')">传统板块</button>
      <button :class="{active:mode==='financial-files'}" @click="setMode('financial-files')">专业财务</button>
      <button :class="{active:mode==='indicators'}" @click="setMode('indicators')">指标清单</button>
    </nav>
    <section class="filters">
      <template v-if="['history-minute','history-txn','history-fund','auction'].includes(mode)">
        <label>代码<input v-model.trim="code" maxlength="6" /></label>
      </template>
      <label v-if="mode==='history-minute'||mode==='history-txn'">日期<input v-model="date" maxlength="8" /></label>
      <label v-if="mode==='block'">板块文件<select v-model="blockFile"><option>block_gn.dat</option><option>block_zs.dat</option><option>block_fg.dat</option></select></label>
      <button @click="load">执行</button>
    </section>
    <div v-if="error" class="error">{{ error }}</div>
    <DataGrid :title="title" :rows="rows" :loading="loading" @row-click="rowClick" />
    <div class="spacer"></div>
    <DataGrid v-if="secondary.length" title="专业财务文件记录" :rows="secondary" />
  </div>
</template>

<style scoped>
.advanced-page{height:100%;overflow:auto;padding:16px 18px 28px;box-sizing:border-box}.toolbar{display:flex;justify-content:space-between;align-items:center;gap:18px}.toolbar h2{margin:0 0 5px;font-size:21px}.toolbar p{margin:0;color:var(--text-dim);font-size:11px}.toolbar button,.filters button{border:0;border-radius:6px;background:var(--accent);color:#fff;padding:8px 13px;cursor:pointer}.tabs{display:flex;gap:6px;margin:14px 0 10px;overflow-x:auto}.tabs button{white-space:nowrap;border:1px solid var(--border);background:var(--bg-panel);color:var(--text-dim);border-radius:6px;padding:7px 10px;cursor:pointer}.tabs button.active{color:var(--accent);border-color:var(--accent)}.filters{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:10px;padding:10px 12px;border:1px solid var(--border);border-radius:8px;background:var(--bg-panel)}.filters label{display:flex;gap:6px;align-items:center;color:var(--text-dim);font-size:11px}.filters input,.filters select{border:1px solid var(--border);background:var(--bg);color:var(--text);border-radius:5px;padding:6px 8px}.error{margin-bottom:10px;padding:10px 12px;color:#fca5a5;border:1px solid #7f1d1d;border-radius:7px;background:rgba(127,29,29,.12)}.spacer{height:10px}
</style>
