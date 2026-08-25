<script setup lang="ts">
// UPDATED 根组件：大盘实时为第一入口，保留 easy_tdx 全功能与原回测能力。
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div class="brand">
        <h1>UPDATED</h1>
        <span>easy_tdx 全功能量化平台</span>
      </div>
      <nav class="app-nav">
        <RouterLink to="/market" active-class="active">大盘实时</RouterLink>
        <RouterLink to="/features" active-class="active">全功能中心</RouterLink>
        <RouterLink to="/api-explorer" active-class="active">全 API</RouterLink>
        <RouterLink to="/backtest" active-class="active">单标的回测</RouterLink>
        <RouterLink to="/portfolio" active-class="active">组合回测</RouterLink>
        <RouterLink to="/optimize" active-class="active">参数寻优</RouterLink>
        <RouterLink to="/compare" active-class="active">结果对比</RouterLink>
        <RouterLink to="/strategies" active-class="active">策略库</RouterLink>
        <RouterLink to="/signals" active-class="active">信号雷达</RouterLink>
        <RouterLink to="/settings" active-class="active">服务器设置</RouterLink>
      </nav>
    </header>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app { display: flex; flex-direction: column; height: 100vh; }
.app-header { display: flex; align-items: center; gap: 24px; padding: 0 20px; min-height: 52px; background: var(--bg-panel); border-bottom: 1px solid var(--border); flex-shrink: 0; }
.brand { display: flex; align-items: baseline; gap: 8px; flex-shrink: 0; }
.brand h1 { margin: 0; font-size: 16px; font-weight: 700; color: var(--accent); }
.brand span { color: var(--text-dim); font-size: 11px; white-space: nowrap; }
.app-nav { display: flex; align-items: center; gap: 16px; min-width: 0; overflow-x: auto; scrollbar-width: thin; }
.app-nav a { color: var(--text-dim); text-decoration: none; font-size: 13px; padding: 16px 0 14px; border-bottom: 2px solid transparent; white-space: nowrap; }
.app-nav a:hover { color: var(--text); }.app-nav a.active { color: var(--accent); border-bottom-color: var(--accent); }
.app-main { flex: 1; min-height: 0; overflow: hidden; }
@media (max-width: 760px) { .app-header { gap: 12px; padding: 0 12px; }.brand span { display: none; }.app-nav { gap: 12px; } }
</style>
