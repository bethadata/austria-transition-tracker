<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { useChartStore } from '@/stores/charts'

const { t } = useI18n()
const store = useChartStore()

const REPO = 'https://github.com/bethadata/austria-transition-tracker-v2'

const generated = computed(() => store.manifest?.generated ?? null)
</script>

<template>
  <v-footer border class="d-flex flex-wrap align-center ga-4 px-4 py-3">
    <span class="text-body-small text-medium-emphasis">
      {{ t('common.footer.note') }}
    </span>

    <v-spacer />

    <span v-if="generated" class="text-body-small text-medium-emphasis">
      {{ t('common.chart.updated') }}: {{ generated }}
    </span>

    <a :href="REPO" target="_blank" rel="noopener noreferrer" class="text-body-small">
      {{ t('common.footer.source_code') }}
    </a>
  </v-footer>
</template>
