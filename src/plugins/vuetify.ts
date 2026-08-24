import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

import { createVuetify } from 'vuetify'

import { CHROME } from '@/utils/palette'

// Surfaces are taken from the same palette the charts use, so a Plotly panel
// sits flush against the Vuetify card behind it rather than on a near-miss gray.
export const vuetify = createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          background: CHROME.light.plane,
          surface: CHROME.light.surface,
          primary: '#2a78d6',
          secondary: CHROME.light.secondary,
          error: '#d03b3b',
          info: '#2a78d6',
          success: '#0ca30c',
          warning: '#fab219',
        },
      },
      dark: {
        dark: true,
        colors: {
          background: CHROME.dark.plane,
          surface: CHROME.dark.surface,
          primary: '#3987e5',
          secondary: CHROME.dark.secondary,
          error: '#d03b3b',
          info: '#3987e5',
          success: '#0ca30c',
          warning: '#fab219',
        },
      },
    },
  },
})
