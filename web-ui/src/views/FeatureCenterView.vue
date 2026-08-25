<script setup lang="ts">
const groups = [
  { title: 'A股市场', desc: '证券列表、实时五档报价、全市场统计、资金流、强势股排名。', items: ['证券列表', '批量报价', '市场统计', '个股资金流', '历史资金流', '强势股排名'], q: 'market' },
  { title: 'K线 / 分时 / 逐笔', desc: '股票与指数K线、分钟线、分时、历史分时和逐笔成交。', items: ['日/周/月K线', '1/5/15/30/60分钟', '指数K线', '分时', '历史分时', '逐笔成交'], q: 'bars' },
  { title: '实时监控', desc: '集合竞价、异动、即时监控和实时市场相关能力。', items: ['集合竞价', '市场异动', '实时数据', '监控接口'], q: 'realtime' },
  { title: '板块基础', desc: '通达信板块文件、行业/概念、板块成员及股票所属板块。', items: ['板块列表', '板块成员', '所属板块', '板块文件'], q: 'block' },
  { title: '板块增强', desc: 'MAC协议板块、板块汇总、排行、成交额与涨跌幅等增强数据。', items: ['行业/概念', '板块汇总', '板块排行', '成分股', 'N日涨跌幅'], q: 'board' },
  { title: '技术指标', desc: '34个技术指标与MyTT兼容指标能力，支持多指标和自定义参数。', items: ['MACD', 'KDJ', 'RSI', 'BOLL', 'DMI/ATR', 'BIAS/OBV'], q: 'indicator' },
  { title: '缠论分析', desc: 'K线合并、分型、笔、中枢、线段、买卖点、背驰及多级别联立。', items: ['分型', '笔', '中枢', '线段', '买卖点', '背驰'], q: 'chanlun' },
  { title: '财务数据', desc: '通达信财务信息、公司相关财务数据与基础资料。', items: ['财务信息', '公司资料', '股本数据', '财务字段'], q: 'finance' },
  { title: '公告中心', desc: '巨潮资讯公告检索与公告PDF相关能力。', items: ['公告检索', '分页', 'PDF链接', '公告下载'], q: 'announcement' },
  { title: '财报三表', desc: '新浪独立数据源的利润表、资产负债表、现金流量表。', items: ['利润表', '资产负债表', '现金流量表'], q: 'sina' },
  { title: 'MAC增强行情', desc: 'MAC协议复权K线、增强报价和额外数据能力。', items: ['前复权', '后复权', '增强报价', 'MAC数据'], q: 'mac' },
  { title: '港美股 / 期货', desc: '扩展市场客户端，覆盖港股、美股、期货等行情能力。', items: ['港股', '美股', '期货', '扩展市场'], q: 'ex' },
  { title: '回测中心', desc: '18个经典策略、单标的回测、组合回测、参数寻优和结果对比。', items: ['单标的', '组合', '参数寻优', '结果对比', '19项绩效'], route: '/backtest' },
  { title: '策略库', desc: 'SQLite持久化保存单策略、组合策略及其参数和绩效快照。', items: ['保存策略', '组合策略', '持久化', '加载/删除'], route: '/strategies' },
  { title: '信号雷达', desc: '一键扫描已保存策略最近买卖信号与当前持仓状态。', items: ['全策略扫描', '买入信号', '卖出信号', '持仓状态'], route: '/signals' },
  { title: '服务器与连接', desc: 'TDX服务器列表、测速、切换、MAC连接及服务状态设置。', items: ['服务器测速', '切换Host', '连接状态', '故障转移'], route: '/settings' },
  { title: 'Python API / CLI / 离线数据', desc: '完整保留easy_tdx Python API、CLI、本地vipdoc/.day/分钟数据和扫描器。', items: ['Python API', 'CLI', 'vipdoc', '.day读取', '离线分钟', '全市场扫描'], q: 'server' },
]
</script>

<template>
  <div class="feature-page">
    <section class="hero">
      <div>
        <div class="eyebrow">UPDATED · easy_tdx 1.20.8 全量底座</div>
        <h2>easy_tdx 全功能中心</h2>
        <p>当前策略是“原功能一个不删 + Web补齐入口”。所有FastAPI接口由全API操作台自动读取OpenAPI，因此后端以后新增接口也会自动出现。</p>
      </div>
      <div class="hero-actions">
        <RouterLink class="primary" to="/api-explorer">全 API 操作台</RouterLink>
        <RouterLink class="secondary" to="/backtest">进入回测</RouterLink>
        <a class="secondary" href="/docs" target="_blank" rel="noreferrer">Swagger</a>
      </div>
    </section>

    <section class="notice">
      <strong>完整覆盖：</strong>
      A股行情、K线/分时/逐笔、板块、资金、指标、缠论、财务、公告、财报、MAC增强行情、港美股/期货、回测、寻优、策略库、信号雷达、服务器、Python API、CLI与本地通达信离线数据全部保留。
    </section>

    <section class="grid">
      <article v-for="group in groups" :key="group.title" class="card">
        <div class="card-head">
          <h3>{{ group.title }}</h3>
          <RouterLink v-if="group.route" :to="group.route">进入 →</RouterLink>
          <RouterLink v-else :to="{ path: '/api-explorer', query: { q: group.q } }">调用 →</RouterLink>
        </div>
        <p>{{ group.desc }}</p>
        <div class="chips"><span v-for="item in group.items" :key="item">{{ item }}</span></div>
      </article>
    </section>

    <section class="quick-links">
      <RouterLink to="/api-explorer">全部REST接口</RouterLink>
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
.hero-actions { display: flex; gap: 10px; flex-shrink: 0; flex-wrap: wrap; }
.hero-actions a, .quick-links a { text-decoration: none; }
.primary, .secondary { padding: 9px 14px; border-radius: 7px; font-size: 13px; }
.primary { background: var(--accent); color: white; }
.secondary { border: 1px solid var(--border); color: var(--text); }
.notice { margin: 14px 0; padding: 12px 14px; border: 1px solid var(--border); border-radius: 8px; color: var(--text-dim); line-height: 1.6; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 12px; }
.card { padding: 16px; border: 1px solid var(--border); background: var(--bg-panel); border-radius: 9px; min-height: 164px; }
.card-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.card h3 { margin: 0; font-size: 16px; }
.card-head a { color: var(--accent); font-size: 12px; text-decoration: none; }
.card p { color: var(--text-dim); font-size: 13px; line-height: 1.6; min-height: 42px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chips span { padding: 4px 7px; border: 1px solid var(--border); border-radius: 999px; color: var(--text-dim); font-size: 11px; }
.quick-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; padding-bottom: 20px; }
.quick-links a { color: var(--accent); border: 1px solid var(--border); border-radius: 6px; padding: 7px 10px; font-size: 12px; }
@media (max-width: 760px) { .hero { align-items: flex-start; flex-direction: column; } .hero-actions { width: 100%; } }
</style>
