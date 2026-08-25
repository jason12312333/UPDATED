<script setup lang="ts">
import { computed } from 'vue'

type Row = Record<string, unknown>

const props = withDefaults(defineProps<{
  title?: string
  rows: Row[]
  loading?: boolean
  error?: string
  emptyText?: string
}>(), {
  title: '',
  loading: false,
  error: '',
  emptyText: '暂无数据',
})

const emit = defineEmits<{ rowClick: [row: Row] }>()

const columns = computed(() => {
  const set = new Set<string>()
  for (const row of props.rows.slice(0, 50)) {
    for (const key of Object.keys(row)) set.add(key)
  }
  return [...set]
})

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '--'
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) return '--'
    const abs = Math.abs(value)
    if (abs >= 1e12) return `${(value / 1e12).toFixed(2)}万亿`
    if (abs >= 1e8) return `${(value / 1e8).toFixed(2)}亿`
    if (abs >= 1e4) return value.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
    return value.toLocaleString('zh-CN', { maximumFractionDigits: 4 })
  }
  if (typeof value === 'boolean') return value ? '是' : '否'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

function tone(key: string, value: unknown): string {
  const n = Number(value)
  if (!Number.isFinite(n)) return ''
  const k = key.toLowerCase()
  if (!/(change|pct|return|profit|pnl|rise|涨跌|涨幅)/.test(k)) return ''
  return n > 0 ? 'up' : n < 0 ? 'down' : ''
}
</script>

<template>
  <section class="grid-panel">
    <div v-if="title" class="panel-head">
      <h3>{{ title }}</h3>
      <span>{{ rows.length }} 条</span>
    </div>
    <div v-if="loading" class="state">加载中…</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <div v-else-if="rows.length === 0" class="state">{{ emptyText }}</div>
    <div v-else class="table-wrap">
      <table>
        <thead><tr><th v-for="col in columns" :key="col">{{ col }}</th></tr></thead>
        <tbody>
          <tr v-for="(row, i) in rows" :key="i" @click="emit('rowClick', row)">
            <td v-for="col in columns" :key="col" :class="tone(col, row[col])" :title="formatValue(row[col])">{{ formatValue(row[col]) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.grid-panel { min-width: 0; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); overflow: hidden; }
.panel-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 11px 13px; border-bottom: 1px solid var(--border); }
.panel-head h3 { margin: 0; font-size: 13px; }.panel-head span { color: var(--text-dim); font-size: 10px; }
.table-wrap { max-width: 100%; overflow: auto; }table { width: 100%; border-collapse: collapse; font-size: 11px; white-space: nowrap; }
th,td { padding: 7px 9px; border-bottom: 1px solid var(--border); text-align: right; max-width: 260px; overflow: hidden; text-overflow: ellipsis; }th { position: sticky; top: 0; z-index: 1; background: var(--bg-panel); color: var(--text-dim); font-weight: 500; }th:first-child,td:first-child { text-align: left; }tbody tr { cursor: pointer; }tbody tr:hover { background: rgba(255,255,255,.025); }.state { padding: 34px 14px; color: var(--text-dim); text-align: center; }.state.error { color: #fca5a5; }.up { color: #ef4146; }.down { color: #18a058; }
</style>
