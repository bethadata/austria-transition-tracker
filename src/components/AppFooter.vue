<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { useChartStore } from '@/stores/charts'
import { BLUESKY, REPO } from '@/utils/links'

const { t } = useI18n()
const store = useChartStore()

const generated = computed(() => store.manifest?.generated ?? null)
</script>

<template>
  <v-footer border class="d-flex align-center px-4 py-1">
    <div class="text-body-small text-medium-emphasis">
      <span>{{ t('common.footer.note') }}</span>
      <!-- The disclaimer alone already fills a phone width, so the build date
           joins it only from sm up; the manifest date is on every chart card. -->
      <span v-if="generated" class="d-none d-sm-inline">
        &middot; {{ t('common.footer.last_updated', { date: generated }) }}
      </span>
    </div>

    <v-spacer />

    <v-btn
      icon="mdi-github"
      variant="text"
      density="comfortable"
      size="small"
      :href="REPO"
      target="_blank"
      rel="noopener noreferrer"
      :aria-label="t('common.footer.github')"
    />

    <v-btn
      variant="text"
      density="comfortable"
      size="small"
      :href="BLUESKY"
      target="_blank"
      rel="noopener noreferrer"
      :aria-label="t('common.footer.bluesky')"
    >
      <!-- Inlined rather than loaded from an .svg file: an <img> renders the SVG as
           its own document, where fill="currentColor" resolves to black, so the icon
           vanishes against the dark theme. Inline it inherits the button's colour. -->
      <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
        <path d="M3.468 1.948C5.303 3.325 7.276 6.118 8 7.616c.725-1.498 2.698-4.29 4.532-5.668C13.855.955 16 .186 16 2.632c0 .489-.28 4.105-.444 4.692-.572 2.04-2.653 2.561-4.504 2.246 3.236.551 4.06 2.375 2.281 4.2-3.376 3.464-4.852-.87-5.23-1.98-.07-.204-.103-.3-.103-.218 0-.081-.033.014-.102.218-.379 1.11-1.855 5.444-5.231 1.98-1.778-1.825-.955-3.65 2.28-4.2-1.85.315-3.932-.205-4.503-2.246C.28 6.737 0 3.12 0 2.632 0 .186 2.145.955 3.468 1.948" />
      </svg>
    </v-btn>
  </v-footer>
</template>
