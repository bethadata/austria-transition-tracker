<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import ChartCard from '@/components/ChartCard.vue'
import type { ChartSpec } from '@/types/data'

defineProps<{
  page: string
  sections: { key: string; charts: ChartSpec[] }[]
}>()

const { t } = useI18n()

/**
 * "overview" is the bucket for charts that carried no heading on the page this
 * replaces -- the sector's headline emissions chart, sitting directly under the
 * page title. Drawing a heading there would add a level the original never had,
 * and "Transport / Overview" reads as a stutter. The locale key is kept: it
 * names the group in the manifest even when it is not printed.
 */
function showsHeading(key: string): boolean {
  return key !== 'overview'
}
</script>

<template>
  <section v-for="section in sections" :key="section.key" class="mb-8">
    <template v-if="showsHeading(section.key)">
      <h2 class="text-title-medium mb-1">
        {{ t(`pages.${page}.sections.${section.key}`) }}
      </h2>
      <v-divider class="mb-4" />
    </template>

    <!--
      Two up on desktop, one up below. Charts are the page: a third column
      squeezes the x axis to the point where the tick labels thin out and the
      series stop being readable, which is worse than scrolling.

      A section holding a single chart takes the full width instead of leaving
      half the row empty -- that is the sector headline chart, which is the one
      most worth reading large.
    -->
    <v-row dense>
      <v-col
        v-for="chart in section.charts"
        :key="chart.id"
        cols="12"
        :lg="section.charts.length === 1 ? 12 : 6"
      >
        <ChartCard :spec="chart" :height="section.charts.length === 1 ? 380 : 320" />
      </v-col>
    </v-row>
  </section>
</template>
