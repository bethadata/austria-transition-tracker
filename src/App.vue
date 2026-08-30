<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDisplay } from 'vuetify'

import AppFooter from '@/components/AppFooter.vue'
import { useAppTheme } from '@/composables/useTheme'
import { setLocale, type Locale } from '@/i18n'
import { SECTORS, TOP_LEVEL } from '@/router'
import { useChartStore } from '@/stores/charts'

const store = useChartStore()
const { mode, toggle, restore } = useAppTheme()
const { t, locale } = useI18n()
const display = useDisplay()

// Open on desktop, closed on phones -- a 240px rail over a 360px viewport is
// the whole screen.
const drawer = ref(!display.mobile.value)

// The sector group replaces the old hover-only dropdown, which had no keyboard
// and no touch path at all. Expanded by default: it is where seven of the ten
// chart pages live, and collapsing it hides most of the site.
const sectorsOpen = ref(true)

function switchLocale(next: unknown) {
  if (next === 'de' || next === 'en') setLocale(next as Locale)
}

onMounted(async () => {
  restore()
  document.documentElement.lang = locale.value
  await store.init()
})
</script>

<template>
  <v-app>
    <v-app-bar flat density="comfortable" border="b">
      <v-app-bar-nav-icon :aria-label="t('common.nav.menu')" @click="drawer = !drawer" />
      <v-app-bar-title class="font-weight-medium">{{ t('common.app.title') }}</v-app-bar-title>

      <v-spacer />

      <v-btn-toggle
        :model-value="locale"
        density="compact"
        variant="outlined"
        divided
        mandatory
        class="mr-2"
        :aria-label="t('common.nav.language')"
        @update:model-value="switchLocale"
      >
        <v-btn value="de" size="small">DE</v-btn>
        <v-btn value="en" size="small">EN</v-btn>
      </v-btn-toggle>

      <v-btn
        :icon="mode === 'dark' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        variant="text"
        :aria-label="t('common.nav.theme')"
        @click="toggle"
      />
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" :width="248">
      <v-list nav density="comfortable">
        <v-list-item
          v-for="item in TOP_LEVEL"
          :key="item.path"
          :to="item.path"
          :prepend-icon="item.icon"
          :title="t(`pages.${item.page}.title`)"
          color="primary"
        />

        <v-list-group v-model="sectorsOpen" value="sectors">
          <template #activator="{ props: activatorProps }">
            <v-list-item
              v-bind="activatorProps"
              prepend-icon="mdi-view-grid-outline"
              :title="t('common.nav.sectors')"
            />
          </template>
          <v-list-item
            v-for="sector in SECTORS"
            :key="sector.slug"
            :to="`/sectors/${sector.slug}`"
            :prepend-icon="sector.icon"
            :title="t(`pages.${sector.page}.title`)"
            color="primary"
          />
        </v-list-group>

        <v-divider class="my-2" />

        <v-list-item
          to="/methodology"
          prepend-icon="mdi-function-variant"
          :title="t('common.nav.methodology')"
          color="primary"
        />
        <v-list-item
          to="/about"
          prepend-icon="mdi-information-outline"
          :title="t('common.nav.about')"
          color="primary"
        />
      </v-list>
    </v-navigation-drawer>

    <!--
      The footer lives inside v-main, not beside it. Vuetify offsets v-main for
      the navigation drawer; a footer outside the layout starts at x=0 instead
      and its first ~250px disappear behind the rail, which clipped the
      disclaimer to its second half on every desktop viewport.
    -->
    <v-main>
      <v-container fluid class="pa-4 pa-md-6">
        <router-view />
      </v-container>

      <AppFooter />
    </v-main>
  </v-app>
</template>
