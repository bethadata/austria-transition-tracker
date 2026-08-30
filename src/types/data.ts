/**
 * The data contract, mirroring services/charts/manifest.py.
 *
 * Nothing here carries human-readable text. Every label the reader sees is
 * looked up from the locale files by one of these ids: `charts.<id>.title`,
 * `common.series.<key>`, `common.units.<key>`, `common.sources.<key>`.
 */

export type ChartType = 'line' | 'area' | 'area_neg' | 'bar' | 'toggle' | 'groups'
export type ToggleView = 'area' | 'bar' | 'line'
export type TimeRes = 'yearly' | 'monthly'

export interface ChartSource {
  key: string
  /** Dataset code at the provider, e.g. nrg_bal_c. Absent for manual sources. */
  code?: string
}

export interface ChartSpec {
  id: string
  page: string
  section: string
  /** Position within the section, as the page was composed. */
  order: number
  type: ChartType
  time_res: TimeRes
  unit: string | null
  /** Ordered: this is the colour order, and it is a CVD-safety mechanism. */
  series: string[]
  /** Present only when type === 'groups': keys of the dataset selector. */
  groups?: string[]
  /** Present only when type === 'toggle'. */
  toggle?: ToggleView[]
  initial?: ToggleView
  /** Series drawn in ink rather than taking a palette slot. */
  total?: string
  /** Series carrying error bars. */
  uncertainty?: string[]
  /** Series stacked as areas even when the chart type is not itself an area. */
  areas?: string[]
  /**
   * Interpolation values for a series' legend label, keyed by series.
   *
   * The fuel-consumption charts need the month their data reaches ("Observed:
   * Jan – Jun"). Encoding it in the series *key* meant four new locale keys in
   * both locales every month the data advanced, and a missed one renders as the
   * literal key. So the key is stable, the locale string carries a {month}
   * placeholder, and only the number travels -- which is also what lets each
   * locale spell the month itself.
   */
  labels?: Record<string, { month?: number }>
  /**
   * The newest point is provisional -- a Statistik Austria "vorlaeufige Daten"
   * drop rather than a final figure. Set by the pipeline, absent otherwise, so
   * the caveat stops being rendered on its own once the final figure lands.
   */
  preliminary?: boolean
  source?: ChartSource
}

export interface Manifest {
  generated: string
  charts: ChartSpec[]
}

/** One series' values, aligned to the block's `x`. null means no data. */
export type Column = (number | null)[]

export interface DataBlock {
  x: string[]
  series: Record<string, Column>
}

export interface ChartData {
  id: string
  updated: string
  /** Flat charts carry x/series directly ... */
  x?: string[]
  series?: Record<string, Column>
  /** ... and `groups` charts carry one block per selectable dataset. */
  groups?: Record<string, DataBlock>
  /**
   * Error-bar half-widths, keyed by series and aligned to `x`, for the series
   * the manifest lists under `uncertainty`. The manifest names *which* series
   * carries a band; only this says how wide it is.
   */
  uncertainty?: Record<string, Column>
}
