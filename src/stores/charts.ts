import { defineStore } from 'pinia'
import { computed, ref, shallowRef } from 'vue'

import type { ChartData, ChartSpec, Manifest } from '@/types/data'

// Vite rewrites absolute hrefs in index.html with the configured base, but not
// fetch() calls -- those have to read it themselves or every request 404s on the
// Pages sub-path while working perfectly in dev.
const BASE = import.meta.env.BASE_URL

async function loadJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE}data/${path}`)
  if (!response.ok) throw new Error(`failed to load ${path}: ${response.status}`)
  return (await response.json()) as T
}

export const useChartStore = defineStore('charts', () => {
  const manifest = shallowRef<Manifest | null>(null)
  const specs = shallowRef<Map<string, ChartSpec>>(new Map())
  const data = shallowRef<Map<string, ChartData>>(new Map())

  const ready = ref(false)
  const error = ref<string | null>(null)

  // Per-chart in-flight promises. Two cards mounting at once (a section coming
  // into view) must share one request rather than race and fetch twice.
  const pending = new Map<string, Promise<ChartData | null>>()
  const failed = ref<Set<string>>(new Set())

  async function init() {
    if (ready.value) return
    try {
      const file = await loadJson<Manifest>('manifest.json')
      manifest.value = file
      specs.value = new Map(file.charts.map((c) => [c.id, c]))
      ready.value = true
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
    }
  }

  /** Charts on a page, grouped by section and in the order the page was composed. */
  const pageSections = computed(() => {
    return (page: string) => {
      const charts = (manifest.value?.charts ?? [])
        .filter((c) => c.page === page)
        .sort((a, b) => a.order - b.order)
      const sections: { key: string; charts: ChartSpec[] }[] = []
      for (const chart of charts) {
        const last = sections[sections.length - 1]
        if (last && last.key === chart.section) last.charts.push(chart)
        else sections.push({ key: chart.section, charts: [chart] })
      }
      return sections
    }
  })

  const pages = computed(() => {
    const seen = new Set<string>()
    for (const c of manifest.value?.charts ?? []) seen.add(c.page)
    return seen
  })

  /** Fetch one chart's data, once. Resolves to null if it could not be loaded. */
  async function ensure(id: string): Promise<ChartData | null> {
    const cached = data.value.get(id)
    if (cached) return cached
    const inFlight = pending.get(id)
    if (inFlight) return inFlight

    const request = loadJson<ChartData>(`${id}.json`)
      .then((payload) => {
        // shallowRef holds the Map by identity, so it has to be replaced rather
        // than mutated for anything watching it to re-render.
        data.value = new Map(data.value).set(id, payload)
        return payload
      })
      .catch(() => {
        failed.value = new Set(failed.value).add(id)
        return null
      })
      .finally(() => {
        pending.delete(id)
      })

    pending.set(id, request)
    return request
  }

  return { manifest, specs, data, ready, error, failed, init, ensure, pageSections, pages }
})
