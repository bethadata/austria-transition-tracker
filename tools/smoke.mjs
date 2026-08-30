/**
 * Headless smoke test against the built site.
 *
 * It checks the two failure modes that a typecheck cannot see and that both
 * render as a page that merely looks a bit wrong:
 *
 *  1. A chart that lost its locale key renders blank, not broken. Namespaced
 *     messages make this cheap to catch -- a missed key renders as the literal
 *     `charts.something.title`, so the assertion is that no visible text
 *     matches /^(charts|common|pages|about)\./.
 *  2. A chart whose data failed to load leaves a card with no <svg> in it.
 *  3. An interpolation placeholder the manifest did not fill -- a legend that
 *     reads "Observed: Jan – {month}". Series labels live in Plotly's SVG, so
 *     check 1 could not see them: innerText skips SVG text entirely, which meant
 *     a missing `common.series.*` key would have gone unnoticed in the one place
 *     series labels are actually shown.
 *
 * Run against `npm run preview` (port 4175), which serves the real build with
 * the real base path -- the one place a BASE_URL mistake actually shows up.
 */
import { chromium } from '@playwright/test'

const BASE = process.env.SMOKE_BASE ?? 'http://localhost:4175/austria-transition-tracker/'

const PAGES = [
  { hash: '#/', name: 'overview', minCharts: 6 },
  { hash: '#/energy', name: 'energy', minCharts: 12 },
  { hash: '#/fossil-fuels', name: 'fossil-fuels', minCharts: 20 },
  { hash: '#/sectors/transport', name: 'transport', minCharts: 22 },
  { hash: '#/sectors/buildings', name: 'buildings', minCharts: 7 },
  { hash: '#/sectors/agriculture', name: 'agriculture', minCharts: 13 },
  { hash: '#/sectors/energy-industry', name: 'energy-industry', minCharts: 3 },
  { hash: '#/sectors/lulucf', name: 'lulucf', minCharts: 3 },
  { hash: '#/sectors/waste', name: 'waste', minCharts: 2 },
  { hash: '#/sectors/f-gases', name: 'f-gases', minCharts: 1 },
  { hash: '#/methodology', name: 'methodology', minCharts: 0 },
  { hash: '#/about', name: 'about', minCharts: 0 },
]

const UNTRANSLATED = /(^|\s)(charts|common|pages|about)\.[a-z0-9_.]+/i
/** A {name} the locale string asked for and nothing supplied. */
const UNFILLED = /\{[a-z_]+\}/i

const failures = []
const notes = []

function fail(message) {
  failures.push(message)
}

const browser = await chromium.launch()
const consoleErrors = []

/**
 * A fresh context per locale, with the preference planted by an init script.
 *
 * Setting localStorage after navigating does not work here: goto() with a URL
 * that differs only in its hash is a same-document navigation, so the app keeps
 * the instance it already booted and the second locale is never actually
 * exercised. addInitScript runs before any page script on every load.
 */
async function contextFor(locale) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } })
  await context.addInitScript((l) => {
    localStorage.setItem('att-locale', l)
  }, locale)
  return context
}

let page

for (const locale of ['de', 'en']) {
  const context = await contextFor(locale)
  page = await context.newPage()
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text())
  })
  page.on('pageerror', (err) => consoleErrors.push(String(err)))

  for (const target of PAGES) {
    await page.goto(BASE + target.hash, { waitUntil: 'domcontentloaded' })
    await page.waitForSelector('h1', { timeout: 15000 })

    const heading = (await page.locator('h1').first().innerText()).trim()
    if (!heading) fail(`${locale} ${target.name}: empty <h1>`)

    // Untranslated keys anywhere on the page.
    const bodyText = await page.locator('body').innerText()
    const hit = bodyText.match(UNTRANSLATED)
    if (hit) fail(`${locale} ${target.name}: untranslated key on page -> ${hit[0].trim()}`)

    if (target.minCharts > 0) {
      const cards = await page.locator('.v-card').count()
      if (cards < target.minCharts) {
        fail(`${locale} ${target.name}: ${cards} cards, expected >= ${target.minCharts}`)
      }

      // Scroll the whole page so every lazily mounted chart is asked to render,
      // then wait for Plotly to actually paint.
      await page.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 600) {
          window.scrollTo(0, y)
          await new Promise((r) => setTimeout(r, 60))
        }
      })
      await page.waitForTimeout(2500)

      const plots = await page.locator('.js-plotly-plot').count()
      const empty = await page.getByText(/No data available|Keine Daten verf/).count()
      const errored = await page.getByText(/could not be loaded|konnte nicht geladen/).count()

      if (errored > 0) fail(`${locale} ${target.name}: ${errored} chart(s) failed to load`)
      if (plots + empty < target.minCharts) {
        fail(
          `${locale} ${target.name}: ${plots} rendered + ${empty} empty < ${target.minCharts} expected`,
        )
      }
      if (empty > 0) notes.push(`${locale} ${target.name}: ${empty} chart(s) report no data`)

      // Legend and axis labels live in Plotly's SVG, which innerText does not
      // reach -- so they are collected separately and checked for the same two
      // failures as the HTML text.
      const svgText = await page.evaluate(() =>
        Array.from(document.querySelectorAll('.js-plotly-plot text'))
          .map((el) => el.textContent ?? '')
          .join(' | '),
      )
      const svgKey = svgText.match(UNTRANSLATED)
      if (svgKey) {
        fail(`${locale} ${target.name}: untranslated key in a chart -> ${svgKey[0].trim()}`)
      }
      const unfilled = (bodyText + ' | ' + svgText).match(UNFILLED)
      if (unfilled) {
        fail(`${locale} ${target.name}: unfilled placeholder -> ${unfilled[0]}`)
      }

      // A rendered plot must actually contain traces.
      const traceless = await page.evaluate(() =>
        Array.from(document.querySelectorAll('.js-plotly-plot')).filter(
          (el) => el.querySelectorAll('.trace, .point, .bars, g.scatterlayer > g').length === 0,
        ).length,
      )
      if (traceless > 0) fail(`${locale} ${target.name}: ${traceless} plot(s) drew no traces`)
    }
  }

  // Prove the locale actually applied, rather than silently testing the default
  // twice: <html lang> is set from it on mount.
  const lang = await page.getAttribute('html', 'lang')
  if (lang !== locale) fail(`${locale}: html lang is ${lang}, locale did not apply`)

  await context.close()
}

// Reopen one context for the mobile check below.
const mobileContext = await contextFor('de')
page = await mobileContext.newPage()

// The page must not scroll horizontally at phone width.
await page.setViewportSize({ width: 390, height: 844 })
await page.goto(BASE + '#/sectors/transport', { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(1500)
const overflow = await page.evaluate(
  () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
)
if (overflow > 2) fail(`mobile: page scrolls horizontally by ${overflow}px`)

await browser.close()

if (consoleErrors.length) {
  const unique = [...new Set(consoleErrors)]
  for (const err of unique.slice(0, 10)) fail(`console error: ${err}`)
}

for (const note of [...new Set(notes)]) console.log(`note: ${note}`)

if (failures.length) {
  console.error(`\nFAIL (${failures.length}):`)
  for (const f of failures) console.error('  - ' + f)
  process.exit(1)
}
console.log(`\nOK: ${PAGES.length} routes x 2 locales, charts render, no untranslated keys`)
