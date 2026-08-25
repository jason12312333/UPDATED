<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

type ApiParam = {
  name: string
  in: 'path' | 'query' | 'header' | string
  required?: boolean
  description?: string
  schema?: { type?: string; default?: unknown; enum?: unknown[] }
}

type Operation = {
  id: string
  method: string
  path: string
  summary: string
  description: string
  tags: string[]
  parameters: ApiParam[]
  requestBody?: unknown
  raw: any
}

const route = useRoute()
const spec = ref<any>(null)
const loadError = ref('')
const search = ref(String(route.query.q || ''))
const selectedId = ref('')
const paramValues = ref<Record<string, string>>({})
const bodyText = ref('{}')
const resultText = ref('')
const resultStatus = ref('')
const running = ref(false)

const httpMethods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

function resolveRef(schema: any): any {
  if (!schema || !schema.$ref || !spec.value) return schema
  const parts = String(schema.$ref).replace(/^#\//, '').split('/')
  let cur = spec.value
  for (const part of parts) cur = cur?.[part]
  return cur || schema
}

function schemaExample(schema: any): any {
  schema = resolveRef(schema)
  if (!schema) return null
  if (schema.example !== undefined) return schema.example
  if (schema.default !== undefined) return schema.default
  if (schema.enum?.length) return schema.enum[0]
  if (schema.type === 'array') return [schemaExample(schema.items)]
  if (schema.type === 'object' || schema.properties) {
    const out: Record<string, unknown> = {}
    for (const [key, value] of Object.entries(schema.properties || {})) {
      out[key] = schemaExample(value)
    }
    return out
  }
  if (schema.type === 'integer' || schema.type === 'number') return 0
  if (schema.type === 'boolean') return false
  return ''
}

const operations = computed<Operation[]>(() => {
  if (!spec.value?.paths) return []
  const rows: Operation[] = []
  for (const [path, pathItem] of Object.entries<any>(spec.value.paths)) {
    for (const method of httpMethods) {
      const raw = pathItem?.[method]
      if (!raw) continue
      rows.push({
        id: `${method}:${path}`,
        method: method.toUpperCase(),
        path,
        summary: raw.summary || raw.operationId || path,
        description: raw.description || '',
        tags: raw.tags || ['未分类'],
        parameters: [...(pathItem.parameters || []), ...(raw.parameters || [])],
        requestBody: raw.requestBody,
        raw,
      })
    }
  }
  return rows.sort((a, b) => (a.tags[0] || '').localeCompare(b.tags[0] || '') || a.path.localeCompare(b.path))
})

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return operations.value
  return operations.value.filter((op) =>
    [op.path, op.summary, op.description, op.method, ...op.tags].join(' ').toLowerCase().includes(q),
  )
})

const selected = computed(() => operations.value.find((op) => op.id === selectedId.value) || null)

const grouped = computed(() => {
  const map = new Map<string, Operation[]>()
  for (const op of filtered.value) {
    const tag = op.tags[0] || '未分类'
    if (!map.has(tag)) map.set(tag, [])
    map.get(tag)!.push(op)
  }
  return [...map.entries()]
})

function selectOperation(op: Operation) {
  selectedId.value = op.id
  resultText.value = ''
  resultStatus.value = ''
  const vals: Record<string, string> = {}
  for (const p of op.parameters) {
    const value = p.schema?.default ?? p.schema?.enum?.[0] ?? ''
    vals[`${p.in}:${p.name}`] = value === undefined || value === null ? '' : String(value)
  }
  paramValues.value = vals

  const body = (op.raw.requestBody?.content?.['application/json'] || op.raw.requestBody?.content?.['application/*+json'])?.schema
  bodyText.value = body ? JSON.stringify(schemaExample(body), null, 2) : '{}'
}

async function runOperation() {
  if (!selected.value) return
  running.value = true
  resultText.value = ''
  resultStatus.value = '请求中…'
  const op = selected.value
  try {
    let url = op.path
    const query = new URLSearchParams()
    const headers: Record<string, string> = {}

    for (const p of op.parameters) {
      const key = `${p.in}:${p.name}`
      const value = paramValues.value[key] ?? ''
      if (p.required && !value) throw new Error(`必填参数 ${p.name} 不能为空`)
      if (!value) continue
      if (p.in === 'path') url = url.replace(`{${p.name}}`, encodeURIComponent(value))
      else if (p.in === 'query') query.append(p.name, value)
      else if (p.in === 'header') headers[p.name] = value
    }

    const qs = query.toString()
    if (qs) url += `?${qs}`

    const init: RequestInit = { method: op.method, headers }
    if (!['GET', 'HEAD'].includes(op.method) && op.raw.requestBody) {
      headers['Content-Type'] = 'application/json'
      const trimmed = bodyText.value.trim()
      if (trimmed) {
        JSON.parse(trimmed)
        init.body = trimmed
      }
    }

    const started = performance.now()
    const response = await fetch(url, init)
    const elapsed = Math.round(performance.now() - started)
    const text = await response.text()
    resultStatus.value = `${response.status} ${response.statusText} · ${elapsed} ms`
    try {
      resultText.value = JSON.stringify(JSON.parse(text), null, 2)
    } catch {
      resultText.value = text
    }
  } catch (err: any) {
    resultStatus.value = '执行失败'
    resultText.value = err?.message || String(err)
  } finally {
    running.value = false
  }
}

onMounted(async () => {
  try {
    const r = await fetch('/openapi.json')
    if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
    spec.value = await r.json()
    if (filtered.value.length) selectOperation(filtered.value[0])
  } catch (err: any) {
    loadError.value = `OpenAPI 加载失败：${err?.message || err}`
  }
})

watch(
  () => route.query.q,
  (q) => {
    search.value = String(q || '')
  },
)
</script>

<template>
  <div class="api-page">
    <aside class="sidebar">
      <div class="side-head">
        <div>
          <h2>全 API 操作台</h2>
          <p>自动读取 easy_tdx OpenAPI；新增后端接口后这里会自动出现。</p>
        </div>
        <input v-model="search" placeholder="搜索 行情 / 板块 / indicator / backtest…" />
      </div>

      <div v-if="loadError" class="error-box">{{ loadError }}</div>
      <div v-else class="ops-list">
        <div class="count">{{ filtered.length }} / {{ operations.length }} 个接口</div>
        <section v-for="[tag, ops] in grouped" :key="tag" class="tag-group">
          <h3>{{ tag }}</h3>
          <button
            v-for="op in ops"
            :key="op.id"
            :class="['op-row', { active: op.id === selectedId }]"
            @click="selectOperation(op)"
          >
            <span :class="['method', op.method.toLowerCase()]">{{ op.method }}</span>
            <span class="op-copy">
              <strong>{{ op.summary }}</strong>
              <small>{{ op.path }}</small>
            </span>
          </button>
        </section>
      </div>
    </aside>

    <main class="workspace">
      <div v-if="!selected" class="empty">选择左侧接口开始调用。</div>
      <template v-else>
        <section class="op-title">
          <div class="title-line">
            <span :class="['method', selected.method.toLowerCase()]">{{ selected.method }}</span>
            <code>{{ selected.path }}</code>
          </div>
          <h2>{{ selected.summary }}</h2>
          <p v-if="selected.description">{{ selected.description }}</p>
          <div class="tags"><span v-for="tag in selected.tags" :key="tag">{{ tag }}</span></div>
        </section>

        <section v-if="selected.parameters.length" class="panel">
          <h3>参数</h3>
          <div class="param-grid">
            <label v-for="p in selected.parameters" :key="`${p.in}:${p.name}`">
              <span>
                {{ p.name }}
                <b v-if="p.required">*</b>
                <em>{{ p.in }}</em>
              </span>
              <select v-if="p.schema?.enum?.length" v-model="paramValues[`${p.in}:${p.name}`]">
                <option value="">请选择</option>
                <option v-for="v in p.schema.enum" :key="String(v)" :value="String(v)">{{ v }}</option>
              </select>
              <input v-else v-model="paramValues[`${p.in}:${p.name}`]" :placeholder="p.description || p.schema?.type || ''" />
              <small v-if="p.description">{{ p.description }}</small>
            </label>
          </div>
        </section>

        <section v-if="selected.raw.requestBody" class="panel">
          <h3>JSON 请求体</h3>
          <textarea v-model="bodyText" spellcheck="false" />
        </section>

        <div class="actions">
          <button class="run" :disabled="running" @click="runOperation">
            {{ running ? '执行中…' : '执行接口' }}
          </button>
          <a href="/docs" target="_blank" rel="noreferrer">查看 Swagger</a>
        </div>

        <section class="panel result-panel">
          <div class="result-head">
            <h3>返回结果</h3>
            <span>{{ resultStatus || '尚未执行' }}</span>
          </div>
          <pre>{{ resultText || '点击“执行接口”后，这里显示 JSON / 文本结果。' }}</pre>
        </section>
      </template>
    </main>
  </div>
</template>

<style scoped>
.api-page { display: grid; grid-template-columns: 360px minmax(0, 1fr); height: 100%; min-height: 0; }
.sidebar { border-right: 1px solid var(--border); background: var(--bg-panel); min-height: 0; display: flex; flex-direction: column; }
.side-head { padding: 14px; border-bottom: 1px solid var(--border); }
.side-head h2 { margin: 0 0 4px; font-size: 17px; }
.side-head p { margin: 0 0 12px; color: var(--text-dim); font-size: 11px; line-height: 1.5; }
.side-head input, .param-grid input, .param-grid select { width: 100%; box-sizing: border-box; border: 1px solid var(--border); background: var(--bg); color: var(--text); border-radius: 6px; padding: 8px 9px; outline: none; }
.ops-list { overflow: auto; padding: 8px; }
.count { padding: 4px 6px 8px; color: var(--text-dim); font-size: 11px; }
.tag-group h3 { margin: 12px 6px 6px; color: var(--text-dim); font-size: 11px; text-transform: uppercase; }
.op-row { width: 100%; display: flex; align-items: flex-start; gap: 8px; padding: 8px; margin-bottom: 4px; border: 1px solid transparent; border-radius: 6px; background: transparent; color: var(--text); text-align: left; cursor: pointer; }
.op-row:hover, .op-row.active { background: var(--bg); border-color: var(--border); }
.op-copy { min-width: 0; display: flex; flex-direction: column; gap: 3px; }
.op-copy strong { font-size: 12px; font-weight: 500; }
.op-copy small { color: var(--text-dim); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.method { display: inline-flex; min-width: 44px; justify-content: center; padding: 3px 5px; border-radius: 4px; font-size: 9px; font-weight: 700; color: white; letter-spacing: .3px; }
.method.get { background: #1677ff; } .method.post { background: #16a34a; } .method.put, .method.patch { background: #d97706; } .method.delete { background: #dc2626; } .method.head, .method.options { background: #6b7280; }
.workspace { min-width: 0; overflow: auto; padding: 18px 22px 28px; }
.empty { height: 100%; display: grid; place-items: center; color: var(--text-dim); }
.op-title { padding-bottom: 14px; border-bottom: 1px solid var(--border); }
.title-line { display: flex; align-items: center; gap: 9px; }
.title-line code { color: var(--accent); }
.op-title h2 { margin: 10px 0 6px; font-size: 20px; }
.op-title p { color: var(--text-dim); line-height: 1.6; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; }.tags span { font-size: 10px; border: 1px solid var(--border); padding: 3px 6px; border-radius: 999px; color: var(--text-dim); }
.panel { margin-top: 14px; padding: 14px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-panel); }
.panel h3 { margin: 0 0 12px; font-size: 13px; }
.param-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.param-grid label { display: flex; flex-direction: column; gap: 5px; }
.param-grid label > span { font-size: 11px; }.param-grid b { color: #dc2626; }.param-grid em { font-style: normal; color: var(--text-dim); margin-left: 6px; }
.param-grid small { color: var(--text-dim); line-height: 1.4; }
textarea { width: 100%; min-height: 180px; box-sizing: border-box; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; resize: vertical; }
.actions { display: flex; align-items: center; gap: 12px; margin-top: 14px; }.actions a { color: var(--accent); font-size: 12px; text-decoration: none; }
.run { border: 0; border-radius: 6px; padding: 9px 18px; background: var(--accent); color: white; cursor: pointer; }.run:disabled { opacity: .55; cursor: wait; }
.result-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; }.result-head span { color: var(--text-dim); font-size: 11px; }
pre { margin: 0; overflow: auto; max-height: 520px; padding: 12px; background: var(--bg); border-radius: 6px; color: var(--text); font-size: 11px; line-height: 1.55; white-space: pre-wrap; word-break: break-word; }
.error-box { padding: 14px; color: #dc2626; }
@media (max-width: 900px) { .api-page { grid-template-columns: 1fr; grid-template-rows: 330px minmax(0, 1fr); } .sidebar { border-right: 0; border-bottom: 1px solid var(--border); } }
</style>
