<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import ChartGrid from '@/components/ChartGrid.vue'
import { useChartStore } from '@/stores/charts'

/**
 * Every chart page, driven by the manifest.
 *
 * There is one component rather than ten because the pages differ only in which
 * charts they carry and what they are called -- both of which are data. A new
 * page needs a route and a locale entry, not a file.
 */
const props = defineProps<{ page: string }>()

const store = useChartStore()
const { t, te } = useI18n()

const sections = computed(() => store.pageSections(props.page))
const introKey = computed(() => `pages.${props.page}.intro`)
const hasIntro = computed(() => te(introKey.value))
const known = computed(() => !store.ready || store.pages.has(props.page))
</script>

<template>
  <div>
    <h1 class="text-headline-small mb-2">{{ t(`pages.${page}.title`) }}</h1>
    <!--
      The intro runs the full content width rather than the ~68ch measure a
      column of prose would want. It is one short paragraph sitting above a grid
      of full-width cards, so a narrow measure reads as a stray column against
      the charts below instead of as a considered text block.
    -->
    <p v-if="hasIntro" class="text-body-medium text-medium-emphasis mb-6">
      {{ t(introKey) }}
    </p>

    <v-alert v-if="store.error" type="error" variant="tonal" class="mb-6">
      {{ t('common.error.manifest') }}
    </v-alert>

    <div v-else-if="!store.ready" class="d-flex justify-center pa-12">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <v-alert v-else-if="!known" type="info" variant="tonal">
      {{ t('common.error.not_found') }}
    </v-alert>

    <ChartGrid v-else :page="page" :sections="sections" />
  </div>
</template>
