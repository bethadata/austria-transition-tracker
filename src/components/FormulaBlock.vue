<script setup lang="ts">
import katex from 'katex'
import 'katex/dist/katex.min.css'
import { computed } from 'vue'

/**
 * One display-mode formula, typeset with KaTeX.
 *
 * The page this replaces wrote its formulas as LaTeX between `$$` delimiters but
 * never loaded MathJax, so the live site rendered them as raw source. KaTeX is
 * synchronous and self-contained, which suits a static build: no network call at
 * render time, and the fonts ship as ordinary assets that Vite rebases.
 *
 * `throwOnError: false` renders a malformed expression in red rather than
 * throwing -- a broken formula should not take the page down with it.
 */
const props = defineProps<{ tex: string }>()

const html = computed(() =>
  katex.renderToString(props.tex, {
    displayMode: true,
    throwOnError: false,
    output: 'html',
  }),
)
</script>

<template>
  <!-- Wide expressions scroll inside their own box; the page body never does. -->
  <div class="formula" v-html="html" />
</template>

<style scoped>
.formula {
  padding: 0.75rem 1rem;
  margin: 0 0 1rem;
  border-radius: 4px;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgba(var(--v-border-color), 0.16);
  overflow-x: auto;
  overflow-y: hidden;
}

/* KaTeX sizes display math generously; at body scale it competes with the prose. */
.formula :deep(.katex-display) {
  margin: 0;
  font-size: 1.02em;
}
</style>
