<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t, tm, rt } = useI18n()

const BASE = import.meta.env.BASE_URL

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
      <pre class="formula">{{ t('about.methodology.step1.formula_scaling') }}</pre>
      <p class="text-body-medium mb-2">{{ t('about.methodology.step1.mean') }}</p>
      <pre class="formula">{{ t('about.methodology.step1.formula_mean') }}</pre>
      <p class="text-body-medium mb-2">{{ t('about.methodology.step1.sigma') }}</p>
      <pre class="formula">{{ t('about.methodology.step1.formula_sigma') }}</pre>

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

      <pre class="formula">{{ t('about.methodology.step2.formula_estimate') }}</pre>
      <p class="text-body-medium mb-4">{{ t('about.methodology.step2.biofuels') }}</p>

      <p class="text-body-medium mb-2">{{ t('about.methodology.step2.gap') }}</p>
      <ul class="text-body-medium mb-4 pl-6">
        <li v-for="reason in list('about.methodology.step2.gap_reasons')" :key="reason" class="mb-1">
          {{ reason }}
        </li>
      </ul>

      <p class="text-body-medium mb-2">{{ t('about.methodology.step2.scaling') }}</p>
      <pre class="formula">{{ t('about.methodology.step2.formula_scaled') }}</pre>
      <v-img :src="image(FIGURES.step2)" :alt="t('about.methodology.step2.figure_alt')" class="figure" />
    </section>

    <!-- Step 3 -->
    <section class="mb-10">
      <h2 class="text-title-medium mb-2">{{ t('about.methodology.step3.title') }}</h2>
      <p class="text-body-medium mb-2">{{ t('about.methodology.step3.body') }}</p>
      <pre class="formula">{{ t('about.methodology.step3.formula_total') }}</pre>

      <p class="text-body-medium mb-2">{{ t('about.methodology.step3.uncertainty') }}</p>
      <pre class="formula">{{ t('about.methodology.step3.formula_uncertainty') }}</pre>
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
/*
 * Formulas are set as monospace blocks rather than typeset maths.
 *
 * The Jekyll page wrote them as LaTeX between $$ delimiters but never loaded
 * MathJax, so they rendered as raw source. A monospace block is honest about
 * being notation and costs no dependency; adding KaTeX would be the upgrade.
 */
.formula {
  font-family: ui-monospace, 'SFMono-Regular', 'Cascadia Code', Consolas, monospace;
  font-size: 0.85rem;
  line-height: 1.6;
  padding: 0.75rem 1rem;
  margin: 0 0 1rem;
  border-radius: 4px;
  background: rgb(var(--v-theme-surface-light, var(--v-theme-surface)));
  border: 1px solid rgba(var(--v-border-color), 0.16);
  overflow-x: auto;
  white-space: pre;
}

.figure {
  border: 1px solid rgba(var(--v-border-color), 0.16);
  border-radius: 4px;
}
</style>
