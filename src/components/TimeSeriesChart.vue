<script setup lang="ts">
// The basic bundle carries scatter and bar and drops the 3D, geo and statistical
// trace families this dashboard never renders - roughly a quarter the weight of
// the full distribution.
import Plotly from 'plotly.js-basic-dist-min'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDisplay } from 'vuetify'

import { useAppTheme } from '@/composables/useTheme'
import type { ChartData, ChartSpec, ToggleView } from '@/types/data'
import { CHROME, seriesColors } from '@/utils/palette'

const props = withDefaults(
  defineProps<{
    spec: ChartSpec
    data: ChartData
    /** Current view for a toggle chart; ignored for every other type. */
    view?: ToggleView
    /** Selected dataset for a `groups` chart. */
    group?: string
    showLegend?: boolean
    height?: number
  }>(),
  { height: 320, showLegend: true },
)

const { mode } = useAppTheme()
const { t, locale } = useI18n()
const display = useDisplay()

const container = ref<HTMLDivElement | null>(null)

/** The block to draw: a `groups` chart selects one, everything else has one. */
const block = computed(() => {
  if (props.data.groups) {
    const key = props.group ?? props.spec.groups?.[0]
    return (key && props.data.groups[key]) || Object.values(props.data.groups)[0] || null
  }
  if (props.data.x && props.data.series) {
    return { x: props.data.x, series: props.data.series }
  }
  return null
})

const hasData = computed(() => {
  const b = block.value
  if (!b || !b.x.length) return false
  return Object.values(b.series).some((col) => col.some((v) => v !== null))
})

/**
 * The trace shape actually drawn.
 *
 * `toggle` charts follow the reader's choice; everything else follows the
 * manifest. `area_neg` is a stacked area that also carries negative values --
 * the LULUCF sink -- which Plotly only stacks correctly in 'relative' mode.
 */
const effectiveView = computed<ToggleView | 'area_neg'>(() => {
  if (props.spec.type === 'toggle') return props.view ?? props.spec.initial ?? 'area'
  if (props.spec.type === 'area_neg') return 'area_neg'
  if (props.spec.type === 'groups') return 'area'
  if (props.spec.type === 'bar') return 'bar'
  if (props.spec.type === 'area') return 'area'
  return 'line'
})

function label(key: string): string {
  return t(`common.series.${key}`)
}

function buildTraces(): Partial<Plotly.PlotData>[] {
  const b = block.value
  if (!b) return []
  const chrome = CHROME[mode.value]
  const colors = seriesColors(mode.value, props.spec.series, props.spec.total)
  const view = effectiveView.value
  const total = props.spec.total

  return props.spec.series.map((key) => {
    const y = b.series[key] ?? []
    const isTotal = key === total
    const color = colors[key]

    // A total is never stacked into the area it totals: it is drawn as a line
    // on top, in ink, or the stack would double-count it.
    const stacked = (view === 'area' || view === 'area_neg') && !isTotal
    const asBar = view === 'bar' && !isTotal

    const trace: Partial<Plotly.PlotData> = {
      x: b.x,
      y,
      name: label(key),
      hovertemplate: `%{y:,.2f}<extra>${label(key)}</extra>`,
    }

    if (asBar) {
      trace.type = 'bar'
      trace.marker = { color }
    } else {
      trace.type = 'scatter'
      trace.mode = 'lines'
      trace.line = { color, width: isTotal ? 2.5 : 2, shape: 'linear' }
      if (stacked) {
        trace.stackgroup = 'one'
        // 'relative' stacks negatives below the axis instead of folding them
        // into the positive stack, which is what a carbon sink needs.
        if (view === 'area_neg') trace.orientation = 'v'
        trace.fillcolor = color
        trace.line = { color, width: 1, shape: 'linear' }
      }
      // connectgaps stays false: a null is a gap in the data and must read as
      // one. Bridging it would draw a straight line across months that were
      // never published.
      trace.connectgaps = false
    }

    if (isTotal) {
      trace.line = { color: chrome.primary, width: 2.5, shape: 'linear' }
      trace.marker = { color: chrome.primary }
    }

    if (props.spec.uncertainty?.includes(key)) {
      const band = b.series[key] ?? []
      trace.error_y = {
        type: 'data',
        array: band.map(() => 0),
        visible: false,
      }
    }

    return trace
  })
}

function layout(): Partial<Plotly.Layout> {
  const chrome = CHROME[mode.value]
  const view = effectiveView.value
  const unit = props.spec.unit ? t(`common.units.${props.spec.unit}`) : ''

  return {
    autosize: true,
    height: props.height,
    // Decimal and thousands separators, so hover figures read the way the rest
    // of the page does.
    separators: locale.value === 'de' ? ',.' : '.,',
    margin: { l: 62, r: 14, t: 8, b: 34 },
    paper_bgcolor: chrome.surface,
    plot_bgcolor: chrome.surface,
    font: {
      family: "system-ui, -apple-system, 'Segoe UI', sans-serif",
      size: 11,
      color: chrome.secondary,
    },
    barmode: view === 'bar' ? 'relative' : undefined,
    xaxis: {
      type: 'date',
      showgrid: false,
      zeroline: false,
      linecolor: chrome.axis,
      tickcolor: chrome.axis,
      tickfont: { color: chrome.muted },
      automargin: true,
      hoverformat: hoverFormat(),
      tickformat: '%Y',
    },
    yaxis: {
      title: { text: unit, font: { color: chrome.secondary } },
      gridcolor: chrome.grid,
      // Negative values need a visible baseline to read against; a purely
      // positive chart does not, and the line only adds ink.
      zeroline: props.spec.type === 'area_neg',
      zerolinecolor: chrome.axis,
      linecolor: chrome.axis,
      tickfont: { color: chrome.muted },
      separatethousands: true,
      automargin: true,
    },
    // The legend is not decoration. With up to twelve series the palette alone
    // cannot carry identity, so it is always present for more than one series.
    showlegend: props.showLegend && props.spec.series.length > 1,
    legend: {
      orientation: 'h',
      yanchor: 'bottom',
      y: 1.02,
      xanchor: 'left',
      x: 0,
      font: { color: chrome.secondary, size: 10 },
    },
    dragmode: display.smAndDown.value ? false : 'zoom',
    hovermode: 'x unified',
    hoverlabel: {
      bgcolor: chrome.surface,
      bordercolor: chrome.axis,
      font: { color: chrome.primary, size: 11 },
    },
  }
}

/** Monthly series need the month in the hover box; yearly ones would be noise. */
function hoverFormat(): string {
  if (props.spec.time_res === 'monthly') {
    return locale.value === 'de' ? '%m/%Y' : '%b %Y'
  }
  return '%Y'
}

function config(): Partial<Plotly.Config> {
  const small = display.smAndDown.value
  return {
    displaylogo: false,
    responsive: true,
    // The mode bar is a row of small targets that is unusable by thumb, and
    // scroll-zoom would hijack the page scroll.
    displayModeBar: small ? false : 'hover',
    scrollZoom: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d', 'toImage'],
  }
}

async function render() {
  if (!container.value || !hasData.value) return
  await Plotly.react(container.value, buildTraces(), layout(), config())
}

let resizeObserver: ResizeObserver | null = null
let resizeTimer: number | undefined

onMounted(async () => {
  await render()
  if (container.value) {
    resizeObserver = new ResizeObserver(() => {
      window.clearTimeout(resizeTimer)
      resizeTimer = window.setTimeout(render, 150)
    })
    resizeObserver.observe(container.value)
  }
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  window.clearTimeout(resizeTimer)
  if (container.value) Plotly.purge(container.value)
})

watch(
  [
    () => props.data,
    () => props.view,
    () => props.group,
    () => props.showLegend,
    () => props.height,
    display.smAndDown,
    mode,
    locale,
  ],
  render,
)
</script>

<template>
  <div>
    <div v-if="!hasData" class="text-medium-emphasis pa-8 text-center text-body-small">
      {{ t('common.chart.no_data') }}
    </div>
    <div v-show="hasData" ref="container" />
  </div>
</template>
