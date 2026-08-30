<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { POPULATION_TRACKER, POWER_SIM, REPO } from '@/utils/links'

const { t, tm, rt } = useI18n()

interface SourceRow {
  name: string
  url: string
  examples: string
  access: string
}

/**
 * `tm` returns the raw message tree rather than a formatted string, which is
 * what array and object content needs; `rt` then resolves each leaf. Reading
 * these as plain `t()` calls would yield the object's toString.
 */
function sourceRows(): SourceRow[] {
  const rows = tm('about.sources.rows') as unknown[]
  return (rows ?? []).map((row) => {
    const r = row as Record<string, unknown>
    return {
      name: rt(r.name as string),
      url: rt(r.url as string),
      examples: rt(r.examples as string),
      access: rt(r.access as string),
    }
  })
}

function columns(): string[] {
  return ((tm('about.sources.columns') as unknown[]) ?? []).map((c) => rt(c as string))
}
</script>

<!--
  The About page of all three sites shares one skeleton: a full-width lead card,
  then the site-specific content cards, then privacy, disclaimer and the AI note
  as a row of three. The sections used to be bare `<section>` blocks, which made
  this the only page of the site not built from cards.

  There is no `v-container` here -- App.vue already wraps every route in a fluid
  one, and a second would double the page padding.
-->
<template>
  <div class="about-page">
    <h1 class="text-headline-small mb-4">{{ t('about.title') }}</h1>

    <!-- MOTIVATION -->
    <v-card flat border class="mb-4">
      <v-card-title tag="h2" class="text-title-medium pt-4">
        {{ t('about.motivation.title') }}
      </v-card-title>

      <v-card-text class="prose text-body-medium">
        <p>{{ t('about.motivation.body') }}</p>

        <!-- One alert, not two: the repository and the sibling projects are the
             same kind of pointer, and stacking two tonal blocks would make the
             card read as mostly callout. -->
        <v-alert type="info" variant="tonal" class="mt-4">
          <i18n-t keypath="about.motivation.links_text" scope="global">
            <template #repo>
              <a
                :href="REPO"
                target="_blank"
                rel="noopener noreferrer"
                class="text-primary font-weight-medium"
              >
                {{ t('about.motivation.repo_link') }}
              </a>
            </template>
            <template #population>
              <a
                :href="POPULATION_TRACKER"
                target="_blank"
                rel="noopener noreferrer"
                class="text-primary font-weight-medium"
              >
                {{ t('about.motivation.population_link') }}
              </a>
            </template>
            <template #power>
              <a
                :href="POWER_SIM"
                target="_blank"
                rel="noopener noreferrer"
                class="text-primary font-weight-medium"
              >
                {{ t('about.motivation.power_link') }}
              </a>
            </template>
          </i18n-t>
        </v-alert>
      </v-card-text>
    </v-card>

    <!-- SOURCES + STACK -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card flat border class="h-100">
          <v-card-title tag="h2" class="text-title-medium pt-4">
            {{ t('about.sources.title') }}
          </v-card-title>

          <v-card-text class="prose text-body-medium">
            <p>{{ t('about.sources.intro') }}</p>

            <!-- Wide content scrolls inside its own box rather than widening the page. -->
            <div style="overflow-x: auto">
              <v-table density="comfortable">
                <thead>
                  <tr>
                    <th v-for="col in columns()" :key="col" class="text-label-large">{{ col }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in sourceRows()" :key="row.name">
                    <td class="text-body-small">
                      <a :href="row.url" target="_blank" rel="noopener noreferrer">{{ row.name }}</a>
                    </td>
                    <td class="text-body-small">{{ row.examples }}</td>
                    <td class="text-body-small">{{ row.access }}</td>
                  </tr>
                </tbody>
              </v-table>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card flat border class="h-100">
          <v-card-title tag="h2" class="text-title-medium pt-4">
            {{ t('about.stack.title') }}
          </v-card-title>

          <v-card-text class="prose text-body-medium">
            <p>{{ t('about.stack.body') }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!--
      Privacy, disclaimer and the AI note are short and of equal standing, so
      they sit side by side rather than as three more full-width bands. `h-100`
      is what makes the three cards in a row end at the same edge.
    -->
    <v-row>
      <v-col cols="12" md="4">
        <v-card flat border class="h-100">
          <v-card-title tag="h2" class="text-title-medium pt-4">
            {{ t('about.privacy.title') }}
          </v-card-title>

          <v-card-text class="prose text-body-medium">
            <i18n-t keypath="about.privacy.body" tag="p" scope="global">
              <template #link1>
                <a
                  href="https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#data-collection"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ t('about.privacy.link1') }}
                </a>
              </template>
              <template #link2>
                <a
                  href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {{ t('about.privacy.link2') }}
                </a>
              </template>
            </i18n-t>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card flat border class="h-100">
          <v-card-title tag="h2" class="text-title-medium pt-4">
            {{ t('about.disclaimer.title') }}
          </v-card-title>

          <v-card-text class="prose text-body-medium">
            <p>{{ t('about.disclaimer.body') }}</p>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card flat border class="h-100">
          <v-card-title tag="h2" class="text-title-medium pt-4">
            {{ t('about.ai.title') }}
          </v-card-title>

          <v-card-text class="prose text-body-medium">
            <p>{{ t('about.ai.body') }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
