import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import vuetify from 'vite-plugin-vuetify'

// Deployed as a GitHub Pages project site, so every asset is served from a
// sub-path rather than the domain root. Vite rewrites absolute hrefs in
// index.html with this, but not site.webmanifest and not fetch() calls -- those
// use install_favicon.py --base and import.meta.env.BASE_URL respectively.
const BASE = '/austria-transition-tracker-v2/'

export default defineConfig({
  base: BASE,
  plugins: [vue(), vuetify({ autoImport: true })],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        // Plotly dwarfs the rest of the bundle and is only needed once a chart
        // page mounts, so it is split out rather than carried by the shell.
        manualChunks(id: string) {
          if (id.includes('plotly.js')) return 'plotly'
          return undefined
        },
      },
    },
  },
})
