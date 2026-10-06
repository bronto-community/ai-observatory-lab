<script setup lang="ts">
import { ref } from 'vue'

// A shell command with a copy button, for the docker lines.
const props = defineProps<{ run: string }>()
const copied = ref(false)
async function copy() {
  await navigator.clipboard.writeText(props.run)
  copied.value = true
  setTimeout(() => (copied.value = false), 1200)
}
</script>

<template>
  <pre class="cmdbox"><code>{{ run }}</code><button class="cp" :title="copied ? 'copied' : 'copy'" @click="copy">{{ copied ? '✓' : '⧉' }}</button></pre>
</template>

<style scoped>
.cmdbox {
  position: relative; margin: 0;
  background: var(--slidev-code-background, #f5f5f5);
  border-radius: var(--slidev-code-radius, 4px);
  padding: 0.55rem 2.4rem 0.55rem 0.8rem;
  font-family: 'Geist Mono', monospace; font-size: 0.74em; line-height: 1.5;
  white-space: pre-wrap; overflow-wrap: anywhere; color: var(--ink);
}
.cp {
  position: absolute; top: 0.4rem; right: 0.5rem;
  border: none; background: none; cursor: pointer;
  color: var(--ink-dim); font-size: 1rem; opacity: 0.6;
}
.cp:hover { opacity: 1; }
</style>
