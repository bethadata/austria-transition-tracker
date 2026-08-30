<script setup lang="ts">
import { computed } from 'vue'
import { I18nT, useI18n } from 'vue-i18n'

/**
 * The prose block that sits beside a chart.
 *
 * The Jekyll site put an explanatory column next to the emissions projection --
 * what the model does, how far to trust it, where the method is written down --
 * and the chart is close to unreadable without it: a projection with an error
 * bar and no explanation invites being read as a forecast.
 *
 * Paragraphs are `charts.<id>.note.p1`, `p2`, ... and stop at the first key that
 * is missing, so a chart gains or loses a paragraph in the locale files alone.
 * They may name `{methodology}`, `{energy}`, `{fossil_fuels}` or `{about}`,
 * which resolve to real router links rather than to text -- the reason this is
 * `I18nT` and not `t()`. A paragraph naming none of them simply leaves the
 * slots unused.
 */
const props = defineProps<{ id: string }>()

const { t, te } = useI18n()

const MAX_PARAGRAPHS = 6

const paragraphs = computed(() => {
  const keys: string[] = []
  for (let n = 1; n <= MAX_PARAGRAPHS; n += 1) {
    const key = `charts.${props.id}.note.p${n}`
    if (!te(key)) break
    keys.push(key)
  }
  return keys
})
</script>

<template>
  <div class="pa-1 pa-lg-4">
    <I18nT
      v-for="key in paragraphs"
      :key="key"
      :keypath="key"
      tag="p"
      scope="global"
      class="text-body-medium text-medium-emphasis mb-4"
    >
      <template #methodology>
        <RouterLink to="/methodology">{{ t('common.nav.methodology') }}</RouterLink>
      </template>
      <template #energy>
        <RouterLink to="/energy">{{ t('pages.energy.title') }}</RouterLink>
      </template>
      <template #fossil_fuels>
        <RouterLink to="/fossil-fuels">{{ t('pages.fossil-fuels.title') }}</RouterLink>
      </template>
      <template #about>
        <RouterLink to="/about">{{ t('common.nav.about') }}</RouterLink>
      </template>
    </I18nT>
  </div>
</template>
