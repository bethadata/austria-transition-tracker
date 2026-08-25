<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import FormulaBlock from '@/components/FormulaBlock.vue'

const { t, tm, rt } = useI18n()

const BASE = import.meta.env.BASE_URL

/**
 * The formulas, as LaTeX.
 *
 * They live here rather than in the locale files because mathematical notation
 * is language-independent: a formula duplicated per locale is a formula that
 * can silently drift between them, and there is nothing in it to translate.
 *
 * Restored from the source of the Jekyll page, with one correction --
 * \hat{\sigma_{x}} put the hat over the whole subscripted symbol, which
 * typesets as a hat floating above a wide expression; \hat{\sigma}_{x} is
 * what was meant.
 */
const FORMULAS = {
  scaling: String.raw`C_{f,y} = F^{cons}_{f,m,y} \cdot C_{f,m,y}`,
  mean: String.raw`\overline{F^{cons}_{f,m}} = \frac{1}{N}\sum_y F^{cons}_{f,m,y}`,
  sigma: String.raw`\hat{\sigma}_{F^{cons}_{f,m}} = \sqrt{\frac{1}{N-1.5}\sum_y \left(\overline{F^{cons}_{f,m}} - F^{cons}_{f,m,y}\right)^2}`,
  estimate: String.raw`E^{estimated}_{y} = \sum_f C_{f,y} \cdot NCV_f \cdot e_f`,
  scaled: String.raw`E^{scaled}_{y} = E^{estimated}_{y} \cdot \overline{F^{em}_y}`,
  total: String.raw`E^{scaled}_{y} = \left(\sum_f C_{f,m,y} \cdot \overline{F^{cons}_{f,m}} \cdot NCV_f \cdot e_f\right) \cdot \overline{F^{em}_y}`,
  uncertainty: String.raw`\sigma^{E,total}_{y} = \sum_f \left(C_{f,m,y} \cdot NCV_f \cdot e_f \cdot \overline{F^{em}_y} \cdot \hat{\sigma}_{F^{cons}_{f,m}}\right) + \left(\sum_f C_{f,m,y} \cdot \overline{F^{cons}_{f,m}} \cdot NCV_f \cdot e_f\right) \cdot \hat{\sigma}_{F^{em}_y}`,
}

const FIGURES = {
  step1: 'fossil_fuel_consumption_estimation.png',
  step2: 'emissions_estimation.png',
  step3: 'emissions_projection_2022.png',
}

function rows(path: string): string[][] {
  const raw = (tm(path) as unknown[]) ?? []
  return raw.map((row) => ((row as unknown[]) ?? []).map((cell) => rt(cell as string)))
}

function list(path: string): string[] {
  return ((tm(path) as unknown[]) ?? []).map((item) => rt(item as string))
}

function image(name: string): string {
  return `${BASE}images/${name}`
}
</script>

<template>
  <div style="max-width: 88ch">
    <h1 class="text-headline-small mb-2">{{ t('about.methodology.title') }}</h1>
    <p class="text-body-medium text-medium-emphasis mb-8">{{ t('about.methodology.intro') }}</p>

    <!-- Step 1 -->
    <section class="mb-10">
      <h2 class="text-title-medium mb-2">{{ t('about.methodology.step1.title') }}</h2>
      <p class="text-body-medium mb-4">{{ t('about.methodology.step1.body') }}</p>

      <div class="mb-4" style="overflow-x: auto">
        <v-table density="compact">
          <thead>
            <tr>
              <th
                v-for="col in list('about.methodology.step1.columns')"
                :key="col"
                class="text-label-large"
              >
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows('about.methodology.step1.rows')" :key="row[0]">
              <td v-for="(cell, i) in row" :key="i" class="text-body-small">{{ cell }}</td>
            </tr>
          </tbody>
        </v-table>
      </div>

      <p class="text-body-medium mb-2">{{ t('about.methodology.step1.factors') }}</p>
      <FormulaBlock :tex="FORMULAS.scaling" />
      <p class="text-body-medium mb-2">{{ t('about.methodology.step1.mean') }}</p>
      <FormulaBlock :tex="FORMULAS.mean" />
      <p class="text-body-medium mb-2">{{ t('about.methodology.step1.sigma') }}</p>
      <FormulaBlock :tex="FORMULAS.sigma" />

      <p class="text-body-medium mb-4">{{ t('about.methodology.step1.caveat') }}</p>
      <v-img :src="image(FIGURES.step1)" :alt="t('about.methodology.step1.figure_alt')" class="figure" />
    </section>

    <!-- Step 2 -->
    <section class="mb-10">
      <h2 class="text-title-medium mb-2">{{ t('about.methodology.step2.title') }}</h2>
      <p class="text-body-medium mb-4">{{ t('about.methodology.step2.body') }}</p>

      <div class="mb-4" style="overflow-x: auto">
        <v-table density="compact">
          <thead>
            <tr>
              <th
                v-for="col in list('about.methodology.step2.columns')"
                :key="col"
                class="text-label-large"
              >
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows('about.methodology.step2.rows')" :key="row[0]">
              <td v-for="(cell, i) in row" :key="i" class="text-body-small">{{ cell }}</td>
            </tr>
          </tbody>
        </v-table>
      </div>

      <FormulaBlock :tex="FORMULAS.estimate" />
      <p class="text-body-medium mb-4">{{ t('about.methodology.step2.biofuels') }}</p>

      <p class="text-body-medium mb-2">{{ t('about.methodology.step2.gap') }}</p>
      <ul class="text-body-medium mb-4 pl-6">
        <li v-for="reason in list('about.methodology.step2.gap_reasons')" :key="reason" class="mb-1">
          {{ reason }}
        </li>
      </ul>

      <p class="text-body-medium mb-2">{{ t('about.methodology.step2.scaling') }}</p>
      <FormulaBlock :tex="FORMULAS.scaled" />
      <v-img :src="image(FIGURES.step2)" :alt="t('about.methodology.step2.figure_alt')" class="figure" />
    </section>

    <!-- Step 3 -->
    <section class="mb-10">
      <h2 class="text-title-medium mb-2">{{ t('about.methodology.step3.title') }}</h2>
      <p class="text-body-medium mb-2">{{ t('about.methodology.step3.body') }}</p>
      <FormulaBlock :tex="FORMULAS.total" />

      <p class="text-body-medium mb-2">{{ t('about.methodology.step3.uncertainty') }}</p>
      <FormulaBlock :tex="FORMULAS.uncertainty" />
      <p class="text-body-medium mb-4">{{ t('about.methodology.step3.terms') }}</p>

      <p class="text-body-medium mb-4">{{ t('about.methodology.step3.other_sectors') }}</p>
      <v-img :src="image(FIGURES.step3)" :alt="t('about.methodology.step3.figure_alt')" class="figure" />
      <p class="text-body-small text-medium-emphasis mt-2">
        {{ t('about.methodology.step3.figure_caption') }}
      </p>
    </section>
  </div>
</template>

<style scoped>
.figure {
  border: 1px solid rgba(var(--v-border-color), 0.16);
  border-radius: 4px;
}
</style>
