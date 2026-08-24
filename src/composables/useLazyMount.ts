import { onBeforeUnmount, onMounted, ref, type Ref } from 'vue'

/**
 * Mount a chart only once it is near the viewport.
 *
 * The pages this replaces inlined every chart at load: the Transport page
 * initialised 22 Plotly instances and roughly a megabyte of markup before the
 * reader had scrolled anywhere. Plotly's cost is per-instance and paid at mount,
 * so deferring it is the difference between a page that opens and one that
 * stalls.
 *
 * `rootMargin` is generous on purpose -- the chart should already be drawn by
 * the time it scrolls into view, not start drawing then.
 *
 * Once visible, it stays visible: unmounting a chart that scrolled past would
 * make scrolling back up pay the cost again, and would throw away any zoom or
 * view the reader had set.
 */
export function useLazyMount(target: Ref<HTMLElement | null>, rootMargin = '300px') {
  const visible = ref(false)
  let observer: IntersectionObserver | null = null

  onMounted(() => {
    // No IntersectionObserver (or a test environment without one) must not mean
    // no charts: fall back to mounting everything.
    if (typeof IntersectionObserver === 'undefined') {
      visible.value = true
      return
    }
    if (!target.value) return
    observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          visible.value = true
          observer?.disconnect()
          observer = null
        }
      },
      { rootMargin },
    )
    observer.observe(target.value)
  })

  onBeforeUnmount(() => {
    observer?.disconnect()
    observer = null
  })

  return { visible }
}
