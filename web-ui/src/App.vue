<script setup lang="ts">
// UPDATED：easy_tdx API 全量保留，但主导航优先展示已接好的功能页面。
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div class="brand"><h1>UPDATED</h1><span>easy_tdx 全功能量化平台</span></div>
      <nav class="app-nav">
        <RouterLink to="/market" active-class="active">大盘实时</RouterLink>
        <RouterLink to="/stock" active-class="active">个股中心</RouterLink>
        <RouterLink to="/boards" active-class="active">板块中心</RouterLink>
        <RouterLink to="/scanner" active-class="active">全市场扫描</RouterLink>
        <RouterLink to="/advanced" active-class="active">高级数据</RouterLink>
        <RouterLink to="/backtest" active-class="active">回测</RouterLink>
        <RouterLink to="/optimize" active-class="active">一键全测</RouterLink>
        <RouterLink to="/strategies" active-class="active">策略库</RouterLink>
        <RouterLink to="/signals" active-class="active">信号雷达</RouterLink>
        <RouterLink to="/extension" active-class="active">港美股/期货</RouterLink>
        <RouterLink to="/offline" active-class="active">本地通达信</RouterLink>
        <RouterLink to="/features" active-class="active">全部功能</RouterLink>
        <RouterLink to="/api-explorer" active-class="active">API</RouterLink>
        <RouterLink to="/settings" active-class="active">设置</RouterLink>
      </nav>
    </header>
    <main class="app-main"><RouterView /></main>
  </div>
</template>

<style scoped>
.app{display:flex;flex-direction:column;height:100vh}.app-header{display:flex;align-items:center;gap:24px;padding:0 20px;min-height:52px;background:var(--bg-panel);border-bottom:1px solid var(--border);flex-shrink:0}.brand{display:flex;align-items:baseline;gap:8px;flex-shrink:0}.brand h1{margin:0;font-size:16px;font-weight:700;color:var(--accent)}.brand span{color:var(--text-dim);font-size:11px;white-space:nowrap}.app-nav{display:flex;align-items:center;gap:15px;min-width:0;overflow-x:auto;scrollbar-width:thin}.app-nav a{color:var(--text-dim);text-decoration:none;font-size:12px;padding:16px 0 14px;border-bottom:2px solid transparent;white-space:nowrap}.app-nav a:hover{color:var(--text)}.app-nav a.active{color:var(--accent);border-bottom-color:var(--accent)}.app-main{flex:1;min-height:0;overflow:hidden}@media(max-width:760px){.app-header{gap:12px;padding:0 12px}.brand span{display:none}.app-nav{gap:12px}}
</style>
