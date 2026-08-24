<script setup lang="ts">
import { useI18n } from 'vue-i18n'

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

const SECTIONS = ['motivation', 'stack', 'privacy', 'disclaimer'] as const
</script>

<template>
  <div style="max-width: 82ch">
    <h1 class="text-headline-small mb-6">{{ t('about.title') }}</h1>

    <section class="mb-8">
      <h2 class="text-title-medium mb-2">{{ t('about.motivation.title') }}</h2>
      <p class="text-body-medium">{{ t('about.motivation.body') }}</p>
    </section>

    <section class="mb-8">
      <h2 class="text-title-medium mb-2">{{ t('about.sources.title') }}</h2>
      <p class="text-body-medium mb-4">{{ t('about.sources.intro') }}</p>

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
    </section>

    <section v-for="key in SECTIONS.slice(1)" :key="key" class="mb-8">
      <h2 class="text-title-medium mb-2">{{ t(`about.${key}.title`) }}</h2>
      <p class="text-body-medium">{{ t(`about.${key}.body`) }}</p>
    </section>
  </div>
</template>
