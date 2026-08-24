import { createI18n } from 'vue-i18n'

import deAbout from '@/locales/de/about.json'
import deCharts from '@/locales/de/charts.json'
import deCommon from '@/locales/de/common.json'
import dePages from '@/locales/de/pages.json'
import enAbout from '@/locales/en/about.json'
import enCharts from '@/locales/en/charts.json'
import enCommon from '@/locales/en/common.json'
import enPages from '@/locales/en/pages.json'

const STORAGE_KEY = 'att-locale'

export type Locale = 'de' | 'en'

function initialLocale(): Locale {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'de' || stored === 'en') return stored
  // German-speaking visitors are the primary audience, so German is the default
  // for anything that is not explicitly an English browser.
  return navigator.language?.toLowerCase().startsWith('en') ? 'en' : 'de'
}

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale(),
  // German is default *and* fallback. Note what that hides: a key present in
  // de/ but missing from en/ silently serves German to an English reader --
  // visible to a human, invisible to a typecheck. The de/en key-set comparison
  // belongs in the test harness, not in review.
  fallbackLocale: 'de',
  // Namespaced, not spread-merged. austria_power_sim does
  // `{ ...enAbout, ...enCommon }`, which flattens every domain into one key
  // space and makes the file split organisational only -- with ~90 chart
  // titles plus series labels and units, that is exactly where a duplicate key
  // silently gives one chart another's title. Here a key reads
  // `charts.<id>.title` and a collision is impossible by construction.
  messages: {
    de: { about: deAbout, charts: deCharts, common: deCommon, pages: dePages },
    en: { about: enAbout, charts: enCharts, common: enCommon, pages: enPages },
  },
})

export function setLocale(locale: Locale) {
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
  document.documentElement.lang = locale
}
