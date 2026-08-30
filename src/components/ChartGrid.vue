<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import ChartCard from '@/components/ChartCard.vue'
import ChartNote from '@/components/ChartNote.vue'
import type { ChartSpec } from '@/types/data'

const props = defineProps<{
  page: string
  sections: { key: string; charts: ChartSpec[] }[]
}>()

const { t, te } = useI18n()

type Cell =
  | { kind: 'chart'; key: string; chart: ChartSpec }
  | { kind: 'note'; key: string; id: string }

/**
 * Each section resolved to grid slots.
 *
 * A chart with an explanatory note takes one slot and hands the next to its
 * prose, so the pair reads side by side and the charts after it flow on as
 * usual. That is the layout the Jekyll page had for the emissions projection,
 * and it is why the note cannot simply live inside the card.
 *
 * "overview" is the bucket for charts that carried no heading on the page this
 * replaces -- the sector's headline chart, sitting directly under the page
 * title. Printing one would add a level the original never had, and
 * "Transport / Overview" reads as a stutter. The key is kept regardless: it
 * names the group in the manifest even when it is not shown.
 */
const layout = computed(() =>
  props.sections.map((section) => {
    // The headline chart's note reads *before* it, everywhere else *after*.
    // That is not a per-chart setting but the difference in what the prose is
    // doing: on the headline chart it introduces the page and has to be read
    // first, which is also the right order once the columns stack on a phone;
    // further down it explains a chart the reader is already looking at. It is
    // the arrangement every Jekyll page had -- text left, chart right at the
    // top, chart left and text right for the projection.
    const noteFirst = section.key === 'overview'
    const cells: Cell[] = []
    for (const chart of section.charts) {
      const note: Cell = { kind: 'note', key: `${chart.id}:note`, id: chart.id }
      const has = te(`charts.${chart.id}.note.p1`)
      if (has && noteFirst) cells.push(note)
      cells.push({ kind: 'chart', key: chart.id, chart })
      if (has && !noteFirst) cells.push(note)
    }
    // A section holding a single slot runs full width rather than leaving half
    // the row empty, and is drawn taller because it is the one worth reading
    // large.
    const solo = cells.length === 1
    return {
      key: section.key,
      heading: section.key !== 'overview',
      cells,
      cols: solo ? 12 : 6,
      height: solo ? 380 : 320,
    }
  }),
)
</script>

<template>
  <section v-for="section in layout" :key="section.key" class="mb-8">
    <template v-if="section.heading">
      <h2 class="text-title-medium mb-1">
        {{ t(`pages.${page}.sections.${section.key}`) }}
      </h2>
      <v-divider class="mb-4" />
    </template>

    <!--
      Two up on desktop, one up below. Charts are the page: a third column
      squeezes the x axis to the point where the tick labels thin out and the
      series stop being readable, which is worse than scrolling.
    -->
    <v-row dense>
      <v-col v-for="cell in section.cells" :key="cell.key" cols="12" :lg="section.cols">
        <ChartCard
          v-if="cell.kind === 'chart'"
          :spec="cell.chart"
          :height="section.height"
        />
        <ChartNote v-else :id="cell.id" />
      </v-col>
    </v-row>
  </section>
</template>
