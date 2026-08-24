<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import TimeSeriesChart from '@/components/TimeSeriesChart.vue'
import { useLazyMount } from '@/composables/useLazyMount'
import { useChartStore } from '@/stores/charts'
import type { ChartSpec, ToggleView } from '@/types/data'

const props = withDefaults(
  defineProps<{
    spec: ChartSpec
    /** Plot height; a full-width headline chart is run taller than a half-width one. */
    height?: number
  }>(),
  { height: 320 },
)

const store = useChartStore()
const { t, te } = useI18n()

const root = ref<HTMLElement | null>(null)
const { visible } = useLazyMount(root)

const view = ref<ToggleView>(props.spec.initial ?? 'area')
const group = ref<string>(props.spec.groups?.[0] ?? '')
const showLegend = ref(true)

const data = computed(() => store.data.get(props.spec.id) ?? null)
const failed = computed(() => store.failed.has(props.spec.id))

// The fetch is tied to visibility rather than to mount: the Transport page has
// 22 charts and would otherwise open 22 requests at once.
watch(
  visible,
  (isVisible) => {
    if (isVisible) void store.ensure(props.spec.id)
  },
  { immediate: true },
)

const title = computed(() => t(`charts.${props.spec.id}.title`))
const infoKey = computed(() => `charts.${props.spec.id}.info`)
const hasInfo = computed(() => te(infoKey.value))

const sourceText = computed(() => {
  const source = props.spec.source
  if (!source) return null
  const name = t(`common.sources.${source.key}`)
  return source.code ? `${name} (${source.code})` : name
})

const VIEW_ICONS: Record<ToggleView, string> = {
  area: 'mdi-chart-areaspline',
  bar: 'mdi-chart-bar',
  line: 'mdi-chart-line',
}

/**
 * Download the chart's own data file.
 *
 * A plain link to public/data/<id>.json would work, but the file is served with
 * whatever name the store used; naming it here keeps the saved file recognisable
 * next to a dozen others.
 */
async function download() {
  const payload = data.value ?? (await store.ensure(props.spec.id))
  if (!payload) return
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${props.spec.id}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
</script>

<template>
  <v-card flat border class="h-100 d-flex flex-column">
    <div class="pa-4 pb-2">
      <h3 class="text-title-small">{{ title }}</h3>
      <p v-if="hasInfo" class="text-body-small text-medium-emphasis mt-1 mb-0">
        {{ t(infoKey) }}
      </p>
    </div>

    <!--
      The observer target is this div rather than the v-card: a ref on a Vuetify
      component resolves to the component instance, and observe() then throws on
      a non-Element, which silently leaves every chart unmounted.
    -->
    <div ref="root" class="px-2 flex-grow-1">
      <TimeSeriesChart
        v-if="visible && data"
        :spec="spec"
        :data="data"
        :view="view"
        :group="group"
        :show-legend="showLegend"
        :height="height"
      />
      <div
        v-else-if="failed"
        class="text-medium-emphasis pa-8 text-center text-body-small"
      >
        {{ t('common.chart.error') }}
      </div>
      <div
        v-else
        class="d-flex align-center justify-center"
        :style="{ minHeight: height + 'px' }"
      >
        <v-progress-circular indeterminate size="24" width="2" color="primary" />
      </div>
    </div>

    <div class="d-flex align-center flex-wrap ga-2 px-4 py-2">
      <!-- Dataset selector, for the charts that carry one (formerly area_button). -->
      <v-select
        v-if="spec.groups?.length"
        v-model="group"
        :items="spec.groups.map((key) => ({ value: key, title: t(`common.groups.${key}`) }))"
        :label="t('common.chart.dataset')"
        density="compact"
        variant="outlined"
        hide-details
        class="flex-grow-0"
        style="max-width: 190px"
      />

      <v-btn-toggle
        v-if="spec.toggle?.length"
        v-model="view"
        density="compact"
        variant="outlined"
        divided
        mandatory
      >
        <v-btn
          v-for="option in spec.toggle"
          :key="option"
          :value="option"
          size="small"
          :icon="VIEW_ICONS[option]"
          :aria-label="t(`common.chart.view_${option}`)"
        />
      </v-btn-toggle>

      <v-spacer />

      <v-btn
        v-if="spec.series.length > 1"
        :icon="showLegend ? 'mdi-format-list-bulleted' : 'mdi-format-list-bulleted-type'"
        variant="text"
        size="small"
        :aria-label="t('common.chart.legend')"
        @click="showLegend = !showLegend"
      />
      <v-btn
        icon="mdi-download-outline"
        variant="text"
        size="small"
        :aria-label="t('common.chart.download')"
        :title="t('common.chart.download_hint')"
        @click="download"
      />
    </div>

    <div v-if="sourceText" class="px-4 pb-3">
      <span class="text-body-small text-medium-emphasis">
        {{ t('common.chart.source') }}: {{ sourceText }}
      </span>
    </div>
  </v-card>
</template>
