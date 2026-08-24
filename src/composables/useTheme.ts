import { computed } from 'vue'
import { useTheme as useVuetifyTheme } from 'vuetify'

import type { Mode } from '@/utils/palette'

const STORAGE_KEY = 'att-theme'

/** Wraps Vuetify's theme so charts can read the current mode as a palette key. */
export function useAppTheme() {
  const theme = useVuetifyTheme()

  function apply(mode: Mode) {
    theme.change(mode)
    localStorage.setItem(STORAGE_KEY, mode)
  }

  function restore() {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') {
      theme.change(stored)
      return
    }
    theme.change(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  }

  const mode = computed<Mode>(() => (theme.current.value.dark ? 'dark' : 'light'))

  function toggle() {
    apply(mode.value === 'dark' ? 'light' : 'dark')
  }

  return { mode, apply, toggle, restore }
}
