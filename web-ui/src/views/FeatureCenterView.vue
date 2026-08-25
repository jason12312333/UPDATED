<script setup lang="ts">
const groups = [
  { title: '大盘实时', desc: '核心指数、全市场涨跌家数、涨停跌停、成交额、市场宽度与分时。', items: ['上证/深成/创业板', '沪深300/上证50/中证1000', '3秒刷新', '1分钟分时'], route: '/market' },
  { title: '个股中心', desc: '一只股票集中查看行情、K线、分时、逐笔、资金、财务、公告、指标、缠论、板块。', items: ['实时五档', 'K线/分时', '资金流', '财务/公告', '34指标', '缠论'], route: '/stock' },
  { title: '板块中心', desc: '行业/概念/风格/地区排名、N日强弱、板块摘要与成分股。', items: ['行业', '概念', '风格', '地区', '板块排名', '成分股'], route: '/boards' },
  { title: '全市场扫描', desc: '实时涨幅排行、强势股排名、市场异动、证券全表。', items: ['实时排行', '强势股', '异动', '沪深列表'], route: '/scanner' },
  { title: '高级数据', desc: '历史分时、历史逐笔、历史资金流、集合竞价、传统板块、专业财务、指标清单。', items: ['历史分时', '历史逐笔', '历史资金', '集合竞价', '专业财务'], route: '/advanced' },
  { title: '回测中心', desc: '18个经典策略、单标的/组合回测、参数寻优与结果对比。', items: ['单标的', '组合', '寻优', '19项绩效'], route: '/backtest' },
  { title: '策略库', desc: 'SQLite 持久化保存单策略、组合策略及参数和绩效快照。', items: ['保存', '加载', '组合', '删除'], route: '/strategies' },
  { title: '信号雷达', desc: '扫描已保存策略最近买卖信号和当前持仓状态。', items: ['买入信号', '卖出信号', '持仓状态', '全策略扫描'], route: '/signals' },
  { title: '港美股 / 期货', desc: '扩展市场实时报价、K线、分时和逐笔成交。', items: ['港股', '美股', '期货', '扩展市场'], route: '/extension' },
  { title: '本地通达信', desc: '直接读取本机 vipdoc/.day 和自定义板块，不依赖网络行情。', items: ['自动检测', 'vipdoc', '.day日线', '自定义板块'], route: '/offline' },
  { title: '服务器设置', desc: 'TDX服务器测速、切换、连接状态和故障转移。', items: ['测速', '切换Host', '连接状态', '故障转移'], route: '/settings' },
  { title: '开发接口', desc: '保留 OpenAPI/Swagger 作为开发与排错入口，不再作为日常主界面。', items: ['OpenAPI', 'Swagger', 'ReDoc', 'Python API/CLI'], route: '/api-explorer' },
]
</script>

<template>
  <div class="feature-page">
    <section class="hero">
      <div><div class="eyebrow">UPDATED · easy_tdx 全功能接入版</div><h2>功能中心</h2><p>现在优先进入真正的业务页面，不需要再到 API 操作台手填参数。底层 easy_tdx API 仍完整保留用于开发和排错。</p></div>
      <div class="hero-actions"><RouterLink class="primary" to="/market">开始看盘</RouterLink><RouterLink class="secondary" to="/stock">个股中心</RouterLink><RouterLink class="secondary" to="/backtest">回测中心</RouterLink></div>
    </section>
    <section class="grid">
      <article v-for="group in groups" :key="group.title" class="card">
        <div class="card-head"><h3>{{ group.title }}</h3><RouterLink :to="group.route">进入 →</RouterLink></div>
        <p>{{ group.desc }}</p><div class="chips"><span v-for="item in group.items" :key="item">{{ item }}</span></div>
      </article>
    </section>
  </div>
</template>

<style scoped>
.feature-page{height:100%;overflow:auto;padding:20px}.hero{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:22px;border:1px solid var(--border);background:var(--bg-panel);border-radius:10px;margin-bottom:14px}.eyebrow{color:var(--accent);font-size:12px;margin-bottom:8px}h2{margin:0 0 8px;font-size:24px}.hero p{margin:0;color:var(--text-dim);max-width:760px;line-height:1.7}.hero-actions{display:flex;gap:9px;flex-wrap:wrap;flex-shrink:0}.hero-actions a{text-decoration:none}.primary,.secondary{padding:9px 14px;border-radius:7px;font-size:13px}.primary{background:var(--accent);color:#fff}.secondary{border:1px solid var(--border);color:var(--text)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px}.card{padding:16px;border:1px solid var(--border);background:var(--bg-panel);border-radius:9px;min-height:150px}.card-head{display:flex;align-items:center;justify-content:space-between;gap:12px}.card h3{margin:0;font-size:16px}.card-head a{color:var(--accent);font-size:12px;text-decoration:none}.card p{color:var(--text-dim);font-size:13px;line-height:1.6;min-height:42px}.chips{display:flex;flex-wrap:wrap;gap:6px}.chips span{padding:4px 7px;border:1px solid var(--border);border-radius:999px;color:var(--text-dim);font-size:11px}@media(max-width:760px){.hero{align-items:flex-start;flex-direction:column}}
</style>
