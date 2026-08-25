<script setup lang="ts">
const groups = [
  {
    title: '行情与市场',
    desc: 'A股实时行情、K线、指数、分时、逐笔、集合竞价、市场统计与异动。',
    items: ['实时/批量报价', '日线/分钟K线', '指数行情', '分时与逐笔', '集合竞价', '市场统计/异动'],
    q: '行情',
  },
  {
    title: '板块与资金',
    desc: '行业/概念板块、成分股、板块排行、涨跌幅排行、资金流与板块汇总。',
    items: ['行业/概念板块', '板块成分', '所属板块', '板块排名', 'N日涨跌幅', '资金流向'],
    q: '板块',
  },
  {
    title: '技术分析',
    desc: '34个技术指标、MyTT公式能力，以及缠论分型、笔、中枢、线段、买卖点、背驰。',
    items: ['MACD/KDJ/RSI/BOLL', 'DMI/ATR/CCI/WR', 'BIAS/OBV', '多指标计算', '缠论', '多级别联立'],
    q: 'indicator',
  },
  {
    title: '公司与资讯',
    desc: '财务数据、公司资料、巨潮公告与新浪财报三表等独立数据源。',
    items: ['财务信息', '股本/公司资料', '巨潮公告', '公告PDF', '利润表', '资产负债表/现金流量表'],
    q: 'finance',
  },
  {
    title: '扩展市场',
    desc: '港股、美股、期货等扩展市场数据能力，以及MAC协议增强行情接口。',
    items: ['港股', '美股', '期货', 'MAC复权K线', 'MAC报价', '扩展市场行情'],
    q: 'market',
  },
  {
    title: '策略与回测',
    desc: '18个经典策略、单标的/组合回测、参数寻优、结果对比、策略库与信号雷达。',
    items: ['单标的回测', '组合回测', '参数寻优', '结果对比', '策略库', '信号雷达'],
    route: '/backtest',
  },
  {
    title: '全市场扫描',
    desc: '策略选股扫描、已保存策略统一扫描、最近买卖信号与当前持仓状态。',
    items: ['策略扫描', '多策略扫描', '最近1/3/5/10根信号', '买卖信号', '持仓状态', '失败容错'],
    route: '/signals',
  },
  {
    title: '本地通达信与开发接口',
    desc: '保留easy_tdx完整Python API、CLI、离线通达信文件读取，以及FastAPI/OpenAPI能力。',
    items: ['Python API', 'CLI', '本地.day读取', '离线分钟数据', 'REST API', 'OpenAPI文档'],
    q: 'server',
  },
]
</script>

<template>
  <div class="feature-page">
    <section class="hero">
      <div>
        <div class="eyebrow">UPDATED · easy_tdx 1.20.8 全量底座</div>
        <h2>easy_tdx 全功能中心</h2>
        <p>不删原能力。行情、板块、资金、指标、缠论、财务、公告、扩展市场、回测、策略库、信号雷达、CLI 与 API 全部保留。</p>
      </div>
      <div class="hero-actions">
        <RouterLink class="primary" to="/api-explorer">打开全 API 操作台</RouterLink>
        <a class="secondary" href="/docs" target="_blank" rel="noreferrer">Swagger 文档</a>
      </div>
    </section>

    <section class="notice">
      <strong>使用原则：</strong>
      原 easy_tdx 已经具备的后端能力直接复用，不重复造轮子；Web UI 没有单独页面的功能，先通过“全 API 操作台”立即可用，再逐步升级成专用中文页面。
    </section>

    <section class="grid">
      <article v-for="group in groups" :key="group.title" class="card">
        <div class="card-head">
          <h3>{{ group.title }}</h3>
          <RouterLink v-if="group.route" :to="group.route">进入 →</RouterLink>
          <RouterLink v-else :to="{ path: '/api-explorer', query: { q: group.q } }">调用 →</RouterLink>
        </div>
        <p>{{ group.desc }}</p>
        <div class="chips">
          <span v-for="item in group.items" :key="item">{{ item }}</span>
        </div>
      </article>
    </section>

    <section class="quick-links">
      <RouterLink to="/backtest">单标的回测</RouterLink>
      <RouterLink to="/portfolio">组合回测</RouterLink>
      <RouterLink to="/optimize">参数寻优</RouterLink>
      <RouterLink to="/compare">结果对比</RouterLink>
      <RouterLink to="/strategies">策略库</RouterLink>
      <RouterLink to="/signals">信号雷达</RouterLink>
      <RouterLink to="/settings">服务器设置</RouterLink>
      <a href="/redoc" target="_blank" rel="noreferrer">ReDoc</a>
    </section>
  </div>
</template>

<style scoped>
.feature-page { height: 100%; overflow: auto; padding: 20px; }
.hero { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 22px; border: 1px solid var(--border); background: var(--bg-panel); border-radius: 10px; }
.eyebrow { color: var(--accent); font-size: 12px; margin-bottom: 8px; }
h2 { margin: 0 0 8px; font-size: 24px; }
.hero p { margin: 0; color: var(--text-dim); max-width: 820px; line-height: 1.7; }
.hero-actions { display: flex; gap: 10px; flex-shrink: 0; }
.hero-actions a, .quick-links a { text-decoration: none; }
.primary, .secondary { padding: 9px 14px; border-radius: 7px; font-size: 13px; }
.primary { background: var(--accent); color: white; }
.secondary { border: 1px solid var(--border); color: var(--text); }
.notice { margin: 14px 0; padding: 12px 14px; border: 1px solid var(--border); border-radius: 8px; color: var(--text-dim); line-height: 1.6; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.card { padding: 16px; border: 1px solid var(--border); background: var(--bg-panel); border-radius: 9px; min-height: 170px; }
.card-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.card h3 { margin: 0; font-size: 16px; }
.card-head a { color: var(--accent); font-size: 12px; text-decoration: none; }
.card p { color: var(--text-dim); font-size: 13px; line-height: 1.6; min-height: 42px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chips span { padding: 4px 7px; border: 1px solid var(--border); border-radius: 999px; color: var(--text-dim); font-size: 11px; }
.quick-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; padding-bottom: 20px; }
.quick-links a { color: var(--accent); border: 1px solid var(--border); border-radius: 6px; padding: 7px 10px; font-size: 12px; }
@media (max-width: 760px) { .hero { align-items: flex-start; flex-direction: column; } .hero-actions { width: 100%; flex-wrap: wrap; } }
</style>
