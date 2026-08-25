import { createRouter, createWebHistory } from 'vue-router'

import ApiExplorerView from './views/ApiExplorerView.vue'
import BacktestView from './views/BacktestView.vue'
import BoardCenterView from './views/BoardCenterView.vue'
import CompareView from './views/CompareView.vue'
import ExtensionMarketView from './views/ExtensionMarketView.vue'
import FeatureCenterView from './views/FeatureCenterView.vue'
import MarketDashboardView from './views/MarketDashboardView.vue'
import MarketScannerView from './views/MarketScannerView.vue'
import OfflineDataView from './views/OfflineDataView.vue'
import OptimizeView from './views/OptimizeView.vue'
import PortfolioView from './views/PortfolioView.vue'
import ServerSettingsView from './views/ServerSettingsView.vue'
import SignalRadarView from './views/SignalRadarView.vue'
import StockCenterView from './views/StockCenterView.vue'
import StrategiesView from './views/StrategiesView.vue'

const routes = [
  { path: '/', name: 'market-home', component: MarketDashboardView, alias: '/market' },
  { path: '/stock', name: 'stock', component: StockCenterView },
  { path: '/boards', name: 'boards', component: BoardCenterView },
  { path: '/scanner', name: 'scanner', component: MarketScannerView },
  { path: '/extension', name: 'extension', component: ExtensionMarketView },
  { path: '/offline', name: 'offline', component: OfflineDataView },
  { path: '/features', name: 'features', component: FeatureCenterView },
  { path: '/api-explorer', name: 'api-explorer', component: ApiExplorerView },
  { path: '/backtest', name: 'backtest', component: BacktestView },
  { path: '/portfolio', name: 'portfolio', component: PortfolioView },
  { path: '/optimize', name: 'optimize', component: OptimizeView },
  { path: '/compare', name: 'compare', component: CompareView },
  { path: '/strategies', name: 'strategies', component: StrategiesView },
  { path: '/signals', name: 'signals', component: SignalRadarView },
  { path: '/settings', name: 'settings', component: ServerSettingsView },
]

export const router = createRouter({ history: createWebHistory(), routes })
