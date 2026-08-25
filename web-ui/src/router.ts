import { createRouter, createWebHistory } from 'vue-router'

import ApiExplorerView from './views/ApiExplorerView.vue'
import BacktestView from './views/BacktestView.vue'
import CompareView from './views/CompareView.vue'
import FeatureCenterView from './views/FeatureCenterView.vue'
import OptimizeView from './views/OptimizeView.vue'
import PortfolioView from './views/PortfolioView.vue'
import ServerSettingsView from './views/ServerSettingsView.vue'
import SignalRadarView from './views/SignalRadarView.vue'
import StrategiesView from './views/StrategiesView.vue'

// UPDATED 默认进入全功能中心；原 easy_tdx 回测入口继续保留在 /backtest。
const routes = [
  { path: '/', name: 'features-home', component: FeatureCenterView, alias: '/features' },
  { path: '/api-explorer', name: 'api-explorer', component: ApiExplorerView },
  { path: '/backtest', name: 'backtest', component: BacktestView },
  { path: '/portfolio', name: 'portfolio', component: PortfolioView },
  { path: '/optimize', name: 'optimize', component: OptimizeView },
  { path: '/compare', name: 'compare', component: CompareView },
  { path: '/strategies', name: 'strategies', component: StrategiesView },
  { path: '/signals', name: 'signals', component: SignalRadarView },
  { path: '/settings', name: 'settings', component: ServerSettingsView },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
