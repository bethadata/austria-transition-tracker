import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

import AboutView from '@/views/AboutView.vue'
import ChartPageView from '@/views/ChartPageView.vue'
import MethodologyView from '@/views/MethodologyView.vue'

/**
 * The seven sector routes, in the order the navigation lists them.
 *
 * `page` is the manifest's page key, which is also the locale key -- one string
 * addresses the charts, the title and the section headings alike.
 */
export const SECTORS = [
  { slug: 'transport', page: 'transport', icon: 'mdi-car-outline' },
  { slug: 'buildings', page: 'buildings', icon: 'mdi-home-outline' },
  { slug: 'energy-industry', page: 'energy-industry', icon: 'mdi-factory' },
  { slug: 'agriculture', page: 'agriculture', icon: 'mdi-sprout-outline' },
  { slug: 'lulucf', page: 'lulucf', icon: 'mdi-pine-tree' },
  { slug: 'waste', page: 'waste', icon: 'mdi-trash-can-outline' },
  { slug: 'f-gases', page: 'f-gases', icon: 'mdi-air-filter' },
] as const

export const TOP_LEVEL = [
  { path: '/', page: 'overview', icon: 'mdi-chart-box-outline' },
  { path: '/energy', page: 'energy', icon: 'mdi-lightning-bolt-outline' },
  { path: '/fossil-fuels', page: 'fossil-fuels', icon: 'mdi-barrel-outline' },
] as const

const chartRoutes: RouteRecordRaw[] = [
  ...TOP_LEVEL.map((entry) => ({
    path: entry.path,
    component: ChartPageView,
    props: { page: entry.page },
  })),
  ...SECTORS.map((sector) => ({
    path: `/sectors/${sector.slug}`,
    component: ChartPageView,
    props: { page: sector.page },
  })),
]

export const router = createRouter({
  // Hash history rather than HTML5: GitHub Pages serves static files and has no
  // rewrite rule, so a deep link like /sectors/transport would 404 on reload.
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    ...chartRoutes,
    { path: '/methodology', component: MethodologyView },
    { path: '/about', component: AboutView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior() {
    // Every route is a long scrolling page; landing mid-page after a nav click
    // reads as a broken link.
    return { top: 0 }
  },
})
