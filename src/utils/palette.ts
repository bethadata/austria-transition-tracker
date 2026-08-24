/**
 * Visualization palette.
 *
 * Slots 1-5 are byte-identical to austria_population's `SERIES`, which is the
 * workspace reference implementation, so the two dashboards read as siblings.
 * Both modes are selected rather than derived: the dark column is the same hues
 * re-stepped for the dark surface, not an automatic flip.
 *
 * The categorical order is the CVD-safety mechanism. The manifest's `series`
 * array is that order; never re-sort it for display, and never cycle the array
 * when a chart has more series than slots.
 *
 * ## Why twelve slots and not five
 *
 * The reference carries five and folds a sixth series into "other". This
 * project cannot: the emission-sector charts have seven real sectors, the
 * energy balances eight fuels, and the car-registration charts twelve brands
 * plus a total. Those categories come from the source data and are not ours to
 * merge.
 *
 * So the extension is deliberate and tiered, and the tiers mean different
 * things:
 *
 * - **Slots 1-8 are eight distinct hues.** This is roughly the ceiling for
 *   categorical colour that still survives deuteranopia, and they are ordered
 *   so that adjacent slots differ on the blue-yellow axis, which is the axis
 *   red-green CVD leaves intact.
 * - **Slots 9-12 are slots 1-4 re-stepped in lightness** - darker on the light
 *   surface, lighter on the dark one. Past eight series, hue has stopped
 *   carrying identity and saying so in the code is more honest than minting
 *   four more hues that only look distinct to normal vision.
 *
 * The relief mechanism is therefore mandatory rather than decorative: charts
 * always carry a legend, hover names the series, and `hovermode: 'x unified'`
 * lists every series at the cursor. A twelve-series chart is read through the
 * hover box, not by matching colours to a key.
 */

export type Mode = 'light' | 'dark'

/** Categorical slots, in fixed order. Index = the manifest's series order. */
export const SERIES: Record<Mode, string[]> = {
  light: [
    '#2a78d6', // blue
    '#eb6834', // orange
    '#1baf7a', // green
    '#eda100', // amber
    '#e87ba4', // pink
    '#8a63d2', // violet
    '#0f8f99', // teal
    '#8c6239', // brown
    '#1b4f8f', // blue, darker
    '#a8421c', // orange, darker
    '#11724f', // green, darker
    '#9c6b00', // amber, darker
  ],
  dark: [
    '#3987e5',
    '#d95926',
    '#199e70',
    '#c98500',
    '#d55181',
    '#9b7ae0',
    '#2aa3ad',
    '#a5794c',
    '#8fc0f2', // blue, lighter
    '#f0906a', // orange, lighter
    '#63d0a6', // green, lighter
    '#edc35c', // amber, lighter
  ],
}

/**
 * Chart chrome. Text always wears ink tokens, never a series colour.
 * Identical to the reference so Vuetify surfaces and Plotly panels match.
 */
export const CHROME: Record<Mode, Record<string, string>> = {
  light: {
    surface: '#fcfcfb',
    plane: '#f9f9f7',
    primary: '#0b0b0b',
    secondary: '#52514e',
    muted: '#898781',
    grid: '#e1e0d9',
    axis: '#c3c2b7',
    border: 'rgba(11,11,11,0.10)',
  },
  dark: {
    surface: '#1a1a19',
    plane: '#0d0d0d',
    primary: '#ffffff',
    secondary: '#c3c2b7',
    muted: '#898781',
    grid: '#2c2c2a',
    axis: '#383835',
    border: 'rgba(255,255,255,0.10)',
  },
}

/**
 * A "total" series is drawn in ink rather than taking a palette slot.
 *
 * It is not one category among the others: it is their sum, drawn over a
 * stacked area or beside a set of bars. Giving it a hue would imply it competes
 * with the sectors it totals, and would cost a slot on charts that already need
 * every one.
 */
export function totalColor(mode: Mode): string {
  return CHROME[mode].primary
}

/**
 * Colour for series index `i`, given how many slots the chart actually needs.
 *
 * Past the end of the array the colour repeats rather than throwing -- a chart
 * that renders in the wrong colour is a bug worth seeing, a chart that fails to
 * render at all hides the rest of the page. `seriesColors` below is what pages
 * use; this exists for the one-off cases.
 */
export function seriesColor(mode: Mode, index: number): string {
  const slots = SERIES[mode]
  return slots[index % slots.length]
}

/**
 * Assign colours to an ordered list of series keys.
 *
 * `total` is pulled out of the sequence rather than skipped in place, so the
 * remaining series keep slots 1..n regardless of where the total sits in the
 * manifest order -- otherwise adding a total to a chart would repaint every
 * series after it.
 */
export function seriesColors(
  mode: Mode,
  keys: string[],
  total?: string | null,
): Record<string, string> {
  const out: Record<string, string> = {}
  let slot = 0
  for (const key of keys) {
    if (total && key === total) {
      out[key] = totalColor(mode)
      continue
    }
    out[key] = seriesColor(mode, slot)
    slot += 1
  }
  return out
}
