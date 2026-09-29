<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useNav } from '@slidev/client'

/**
 * Slidev disables every keyboard shortcut while a <button> or <a> holds focus:
 *
 *   isOnFocus = ['BUTTON','A'].includes(activeElement.tagName)
 *
 * So one click on a ladder control, a map cell, a player card or even a link
 * leaves the arrow keys dead until you happen to click bare background. Mid-talk
 * that reads as the deck having frozen.
 *
 * Two layers of defence:
 *  1. hand focus back after any click, which fixes the cause deck-wide;
 *  2. a hot corner that reveals prev/next, for when something still eats the keys.
 */
const { next, prev } = useNav()

// 1 — release focus after a click anywhere.
// pointerup, not click: it still fires when a handler stops click propagation.
// Deferred with a timeout rather than rAF so it also runs when the tab is not
// painting, and so the element's own focus and handlers go first.
function releaseFocus(e: PointerEvent) {
  const el = e.target as HTMLElement | null
  if (el?.closest('input, textarea, select, [contenteditable]')) return
  setTimeout(() => {
    const active = document.activeElement as HTMLElement | null
    if (active && ['BUTTON', 'A'].includes(active.tagName)) active.blur()
  }, 0)
}

// 2 — reveal only while the pointer is in the bottom-right corner.
// Position-driven rather than on a timer, so by the time the cursor arrives the
// buttons are already interactive; there is no "wake it up first" race.
const ZONE_W = 210
const ZONE_H = 170
const inCorner = ref(false)

function trackCorner(e: MouseEvent) {
  inCorner.value =
    e.clientX > window.innerWidth - ZONE_W &&
    e.clientY > window.innerHeight - ZONE_H
}
// pointer gone (window blur, left the page): don't leave them stranded on screen
function hide() { inCorner.value = false }

onMounted(() => {
  window.addEventListener('pointerup', releaseFocus, true)
  window.addEventListener('mousemove', trackCorner, { passive: true })
  window.addEventListener('blur', hide)
  document.addEventListener('mouseleave', hide)
})
onUnmounted(() => {
  window.removeEventListener('pointerup', releaseFocus, true)
  window.removeEventListener('mousemove', trackCorner)
  window.removeEventListener('blur', hide)
  document.removeEventListener('mouseleave', hide)
})
</script>

<template>
  <div class="navsafe" :class="{ show: inCorner }">
    <button class="ns-btn" title="previous slide" @click="prev()">‹</button>
    <button class="ns-btn" title="next slide" @click="next()">›</button>
  </div>
</template>

<style scoped>
.navsafe {
  position: fixed; right: 14px; bottom: 12px; z-index: 60;
  display: flex; gap: 6px;
  opacity: 0;
  /* not clickable while hidden, so it can never swallow a drag meant for the
     slide (the steering wheel sits in roughly this corner) */
  pointer-events: none;
  transition: opacity 0.18s ease;
}
.navsafe.show { opacity: 1; pointer-events: auto; }

.ns-btn {
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(43, 38, 32, 0.16);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  color: #2B2620; font-size: 1.1rem; line-height: 1;
  cursor: pointer;
  transition: background 0.15s ease;
}
.ns-btn:hover { background: #fff; }
</style>
