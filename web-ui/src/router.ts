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

// 保留 easy_tdx 原有回测入口，同时增加全功能中心和动态 OpenAPI 操作台。
// / 继续兼容原来的单标的回测；/backtest 作为更清晰的显式别名。
const routes = [
  { path: '/', name: 'backtest', component: BacktestView, alias: '/backtest' },
  { path: '/features', name: 'features', component: FeatureCenterView },
  { path: '/api-explorer', name: 'api-explorer', component: ApiExplorerView },
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
