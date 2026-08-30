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
 * Four names are exempt from purely positional assignment, because on a chart
 * of energy carriers the colour is read as a statement about the carrier: hydro
 * claims blue, the low-carbon option claims green, oil claims brown, and coal
 * leaves the sequence for graphite. Each is a swap between two slots; none of
 * them re-orders the series. See the claims below `seriesColor`.
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
 * The slots the semantic claims below name, by the meaning each carries.
 *
 * Only these four have a meaning. Every other slot is a categorical hue and
 * says nothing about what it is drawn on.
 */
const GREEN_SLOT = 2
const BLUE_SLOT = 0
const BROWN_SLOT = 7

/**
 * Coal is drawn in graphite, which is not a categorical slot at all.
 *
 * There is no black in the twelve, and there should not be: the palette's dark
 * end is `totalColor`'s ink and adding a near-ink hue to the categorical
 * sequence would put it on whatever series happened to land there. So coal
 * leaves the sequence the way a total does, and the slot it would have taken
 * goes unused rather than shifting the series after it.
 *
 * Safe against the ink total only because no chart carrying `coal` carries one
 * -- checked across all 89. If one ever does, a black line over a graphite area
 * is the thing to look at first.
 *
 * The dark value is a mid grey rather than a dark one: coal on a #0d0d0d plane
 * has to be lighter than its background, so "coal is the dark one" inverts with
 * the theme and only the hue stays constant.
 */
export const COAL: Record<Mode, string> = {
  light: '#4a453d',
  dark: '#8a837a',
}

/**
 * Series that name the low-carbon option, highest claim first.
 *
 * On a chart that ranks its categories by how clean they are, green is not a
 * free categorical hue: a reader takes it as the verdict. Left to the
 * positional assignment it landed on coal in fourteen fuel-mix charts and on
 * `hybrid` in all ten vehicle charts, while electricity sat in pink and the
 * BEV series in blue -- the palette was saying the opposite of the data.
 *
 * So one series per chart may claim the green slot. Order here is the claim
 * order and it only ever decides between two candidates on the same chart:
 * heat pumps outrank the grid on the heating-system charts, electricity
 * outranks biomass on the final-energy ones, and biomass takes it on district
 * heat where no electric carrier appears at all.
 *
 * Deliberately not listed: `district_heat` (as clean as whatever fed it),
 * `waste`, and `hybrid`/`hybrid_plugin` (still combustion). Nothing here is
 * inferred from the key's spelling -- an `electricity_and_heat_generation`
 * *emitter* must not read as clean because its name starts the same way.
 */
const SUSTAINABLE = [
  'heat_pumps_solar',
  'electric',
  'electrified',
  'renewable_electricity',
  'electricity',
  'pv',
  'wind',
  'hydro',
  'ambient_heat',
  'biomass',
  'bio_diesel_monthly',
  'bio_diesel_12_month_average',
  'bio_gasoline_monthly',
  'bio_gasoline_12_month_average',
  'blended_biodiesel_monthly',
  'blended_biodiesel_12_month_average',
  'blended_biogasoline_monthly',
  'blended_biogasoline_12_month_average',
]

/**
 * Series that must never hold green, for the charts where nothing can.
 *
 * `emissions_fuels_monthly` is gas, oil and coal and has no clean member at
 * all; there the green slot is skipped rather than handed to the least bad
 * fossil fuel.
 *
 * Membership is "this series *is* a quantity of fossil fuel", which is why
 * `public_electricity_heat` is in here: on the two gas-by-sector charts it is
 * gas burned in power stations, and it held green while wearing the word
 * "electricity". A sector's *emissions* are not a fuel quantity, so the
 * emission-breakdown charts are untouched and their green stays what it has
 * always been -- one categorical hue among seven, claiming nothing.
 */
const FOSSIL = new Set([
  'coal',
  'oil',
  'gas',
  'natural_gas',
  'diesel',
  'gasoline',
  'diesel_monthly',
  'diesel_12_month_average',
  'gasoline_monthly',
  'gasoline_12_month_average',
  'public_electricity_heat',
])

/**
 * Assign colours to an ordered list of series keys.
 *
 * `total` is pulled out of the sequence rather than skipped in place, so the
 * remaining series keep slots 1..n regardless of where the total sits in the
 * manifest order -- otherwise adding a total to a chart would repaint every
 * series after it.
 *
 * Then four series names may claim the slot that means what they are: hydro
 * blue, the low-carbon option green, oil brown, coal graphite. Each claim is a
 * *swap*, not a re-ordering: the claimant and whoever held the slot trade
 * places and every other series keeps the colour it had. Rotating instead would
 * repaint three series per chart rather than two, and it costs the two-series
 * charts their orange -- `rail_tracks_rel` would come out green against blue,
 * which is the one pairing deuteranopia flattens.
 *
 * The series *order* is untouched throughout: this maps keys to slots, and the
 * manifest's order still decides who is drawn where and who is listed first.
 *
 * Claims run in a fixed order because they compete for holders, not for
 * targets: coal leaves first so the green claim on the fuel-mix charts finds
 * its slot already empty, and hydro takes blue off `pv` before the green claim
 * looks at who is sitting in green -- which is then `pv`, and it stays.
 */
export function seriesColors(
  mode: Mode,
  keys: string[],
  total?: string | null,
): Record<string, string> {
  const ordered = keys.filter((key) => !(total && key === total))
  const slots = new Map<string, number>()
  ordered.forEach((key, index) => slots.set(key, index))

  const out: Record<string, string> = {}
  const settled = new Set<number>()

  /** Give `key` the slot that means it, and hand its old one to the displaced. */
  const claim = (key: string, slot: number) => {
    const held = slots.get(key)
    if (held === undefined || held === slot || settled.has(slot)) return
    const holder = ordered.find((other) => slots.get(other) === slot)
    slots.set(key, slot)
    // No holder means the chart is too short to reach that slot, so the
    // claimant's old one simply goes unused.
    if (holder !== undefined) slots.set(holder, held)
    settled.add(slot)
  }

  if (slots.has('coal')) {
    out.coal = COAL[mode]
    slots.delete('coal')
  }
  claim('oil', BROWN_SLOT)
  claim('hydro', BLUE_SLOT)

  // Green is the one claim with more than one possible claimant, so it asks who
  // is already there first: on the electricity charts that is a renewable, and
  // repainting four of them to promote a different renewable would be churn.
  const green = ordered.find((key) => slots.get(key) === GREEN_SLOT)
  if (!(green !== undefined && SUSTAINABLE.includes(green))) {
    const claimant = SUSTAINABLE.find((key) => slots.has(key))
    if (claimant !== undefined) {
      claim(claimant, GREEN_SLOT)
    } else if (green !== undefined && FOSSIL.has(green)) {
      // Nothing on this chart is clean -- `road_fuels_consumption` is two fossil
      // road fuels and their averages. Skip green rather than hand it to one.
      for (const key of ordered) {
        const slot = slots.get(key)
        if (slot !== undefined && slot >= GREEN_SLOT) slots.set(key, slot + 1)
      }
    }
  }

  for (const key of keys) {
    if (key in out) continue
    out[key] =
      total && key === total ? totalColor(mode) : seriesColor(mode, slots.get(key)!)
  }
  return out
}
