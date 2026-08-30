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

/**
 * The provisional-data caveat is one shared string keyed off a manifest flag,
 * not part of the chart's own `info`. A chart has exactly one `info` key per
 * locale, so anything conditional written into it can only ever describe one of
 * the two cases -- which is how this note came to state a date that was two
 * refreshes old.
 */
const isPreliminary = computed(() => props.spec.preliminary === true)

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
      <p v-if="isPreliminary" class="text-body-small text-medium-emphasis mt-1 mb-0">
        {{ t('common.chart.preliminary') }}
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

      <!--
        A segmented control, not three icon buttons in a box. As icons alone the
        three chart glyphs are near-indistinguishable at 16px and the selected
        one was told apart only by a slightly darker fill, so the reader could
        not see which view they were looking at without clicking. The label
        carries the meaning; the icon is recognition, not the message.
      -->
      <div v-if="spec.toggle?.length" class="view-toggle" role="group">
        <button
          v-for="option in spec.toggle"
          :key="option"
          type="button"
          class="view-toggle__option text-label-small"
          :class="{ 'view-toggle__option--active': view === option }"
          :aria-pressed="view === option"
          :aria-label="t(`common.chart.view_${option}`)"
          @click="view = option"
        >
          <v-icon :icon="VIEW_ICONS[option]" size="15" />
          <span>{{ t(`common.chart.view_${option}`) }}</span>
        </button>
      </div>

      <!--
        `ml-auto` on a group rather than a v-spacer between siblings: the row
        wraps on a phone, and a spacer only pushes on the line it happens to sit
        on -- the download button then wrapped alone to the left of the next
        line while the legend button stayed right on the first.
      -->
      <div class="d-flex align-center ga-1 ml-auto">
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
    </div>

    <div v-if="sourceText" class="px-4 pb-3">
      <span class="text-body-small text-medium-emphasis">
        {{ t('common.chart.source') }}: {{ sourceText }}
      </span>
    </div>
  </v-card>
</template>

<style scoped>
/*
 * Tokens rather than literal colours: the card sits on `surface` in both
 * themes, and a hardcoded grey would go invisible in one of them.
 */
.view-toggle {
  display: inline-flex;
  border: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  overflow: hidden;
}

.view-toggle__option {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border: 0;
  background: transparent;
  color: rgba(var(--v-theme-on-surface), var(--v-medium-emphasis-opacity));
  cursor: pointer;
  white-space: nowrap;
}

.view-toggle__option + .view-toggle__option {
  border-left: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.view-toggle__option:hover {
  background: rgba(var(--v-theme-on-surface), 0.05);
}

.view-toggle__option:focus-visible {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: -2px;
}

/* Selected state is carried by fill *and* colour *and* weight -- one of the
   three alone is what made the old toggle unreadable. */
.view-toggle__option--active {
  background: rgba(var(--v-theme-primary), 0.14);
  color: rgb(var(--v-theme-primary));
  font-weight: 600;
}
</style>
