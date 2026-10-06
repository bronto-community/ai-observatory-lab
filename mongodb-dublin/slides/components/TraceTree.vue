<script setup lang="ts">
// One real step-3 trace from the lab (trace f6e549c5…, 2026-09-28), drawn as the span tree Bronto shows.
// `upto` reveals rows progressively (bind it to $clicks).
const props = withDefaults(defineProps<{ upto?: number }>(), { upto: 99 })

const ROWS = [
  { d: 0, name: 'invoke_agent storefront_assistant', ms: 6615, tag: 'agent', note: '1,898 in / 178 out: excludes the sub-agent' },
  { d: 1, name: 'execute_event_loop_cycle', ms: 5030, tag: 'loop', note: '' },
  { d: 2, name: 'chat', ms: 1406, tag: 'model', note: 'haiku 4.5 · 866 in / 62 out · TTFT 1,235 ms' },
  { d: 3, name: 'chat us.anthropic.claude-haiku-4-5…', ms: 1403, tag: 'aws', note: 'botocore: same call · finish: tool_use' },
  { d: 2, name: 'execute_tool product_researcher', ms: 3622, tag: 'tool', note: 'the sub-agent, called as a tool' },
  { d: 3, name: 'invoke_agent product_researcher', ms: 3577, tag: 'agent', note: '+1,650 in / 278 out, its own loop' },
  { d: 4, name: 'chat', ms: 1757, tag: 'model', note: '646 in / 184 out' },
  { d: 4, name: 'execute_tool check_inventory', ms: 146, tag: 'tool', note: '×4: four lookups for one question' },
  { d: 4, name: 'chat', ms: 1669, tag: 'model', note: '1,004 in / 94 out · finish: end_turn' },
  { d: 1, name: 'execute_event_loop_cycle', ms: 1584, tag: 'loop', note: '' },
  { d: 2, name: 'chat', ms: 1583, tag: 'model', note: '1,032 in / 116 out · finish: end_turn' },
]
const MAX = 6615
</script>

<template>
  <div class="tt">
    <div v-for="(r, i) in ROWS" :key="i" class="row" :class="[r.tag, { err: r.err, hide: i >= props.upto }]">
      <div class="label" :style="{ paddingLeft: r.d * 1.1 + 'rem' }">
        <span class="dot" />{{ r.name }}
      </div>
      <div class="bar-wrap"><div class="bar" :style="{ width: (r.ms / MAX) * 100 + '%' }" /></div>
      <div class="ms">{{ r.ms.toLocaleString() }} ms</div>
      <div class="note">{{ r.note }}</div>
    </div>
  </div>
</template>

<style scoped>
.tt { display: flex; flex-direction: column; gap: 0.22rem; font-size: 0.74rem; }
.row {
  display: grid; grid-template-columns: 18rem 7rem 4.4rem 1fr; align-items: center; gap: 0.5rem; line-height: 1.35;
  transition: opacity 0.25s ease;
}
.row.hide { opacity: 0.08; }
.label { font-family: 'Geist Mono', monospace; white-space: nowrap; display: flex; align-items: center; gap: 0.45rem; }
.dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; background: var(--ink-dim); }
.agent .dot { background: var(--sapphire); }
.model .dot { background: var(--mint); }
.tool .dot { background: #E0A100; }
.aws .dot { background: #FF9900; }
.err .dot { background: var(--claim); }
.bar-wrap { height: 9px; background: var(--border); border-radius: 5px; overflow: hidden; }
.bar { height: 100%; border-radius: 5px; background: var(--sapphire-soft); }
.model .bar { background: var(--mint); }
.tool .bar { background: #F5D37A; }
.aws .bar { background: #FFD08A; }
.err .bar { background: var(--claim); }
.ms { font-family: 'Geist Mono', monospace; color: var(--ink-dim); text-align: right; white-space: nowrap; }
.label { overflow: hidden; text-overflow: ellipsis; }
.note { color: var(--ink-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.err .note { color: var(--claim); font-weight: 600; }
.aws .label, .aws .note { opacity: 0.75; }
</style>
