<script setup lang="ts">
import { computed } from 'vue'
import qrcode from 'qrcode-generator'

// Rendered from the module matrix rather than an image, so it stays crisp at any
// projector resolution and follows the URL if that changes.
//
// Deliberately plain: square modules, ink on white, and the full 4-module quiet
// zone. Rounding or tinting the modules costs scan reliability, and these get
// photographed off a screen at the back of a room.
const props = withDefaults(defineProps<{
  url: string
  size?: number       // rendered edge length in slide px
  caption?: string
}>(), { size: 132 })

const QUIET = 4
const INK = '#2B2620'

const qr = computed(() => {
  const c = qrcode(0, 'M')     // auto version, ~15% error correction
  c.addData(props.url)
  c.make()
  return c
})

const count = computed(() => qr.value.getModuleCount())
const span = computed(() => count.value + QUIET * 2)

/** one path string for every dark module — a single node instead of ~400 rects */
const path = computed(() => {
  const c = qr.value, n = count.value
  let d = ''
  for (let r = 0; r < n; r++) {
    for (let col = 0; col < n; col++) {
      if (c.isDark(r, col)) d += `M${col + QUIET} ${r + QUIET}h1v1h-1z`
    }
  }
  return d
})
</script>

<template>
  <div class="qr">
    <svg :viewBox="`0 0 ${span} ${span}`" :width="size" :height="size" shape-rendering="crispEdges">
      <rect :width="span" :height="span" fill="#fff" />
      <path :d="path" :fill="INK" />
    </svg>
    <span v-if="caption" class="qr-cap">{{ caption }}</span>
  </div>
</template>

<style scoped>
.qr { display: inline-flex; flex-direction: column; align-items: center; gap: 0.45rem; }
.qr svg {
  display: block; border-radius: 8px;
  border: 1px solid var(--border);
  background: #fff;
}
.qr-cap {
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.09em; color: var(--ink-dim);
}
</style>
