<script setup>
// Pre-phase 1 scaffold check: confirms Vue 3 + Vite + Tailwind and the functional
// palette tokens are wired up. Real screens (Setup, Scorer, Viewer, History)
// arrive in Phase 1 — see docs/UI_PLAN.md.
// Full class strings (not interpolated) so Tailwind's JIT scanner can see them.
const swatches = [
  { cls: 'bg-runs', label: 'Runs' },
  { cls: 'bg-boundary', label: 'Boundary' },
  { cls: 'bg-wide', label: 'Wide' },
  { cls: 'bg-noball', label: 'No-Ball' },
  { cls: 'bg-bye', label: 'Bye' },
  { cls: 'bg-wicket', label: 'Wicket' },
  { cls: 'bg-system', label: 'System' },
]
</script>

<template>
  <main class="min-h-full p-6 max-w-md mx-auto">
    <header class="mb-6">
      <h1 class="text-2xl font-bold text-system">🏏 Howzatt</h1>
      <p class="text-sm text-slate-500">Monorepo scaffold is live. Palette tokens:</p>
    </header>

    <div class="grid grid-cols-2 gap-3">
      <div
        v-for="s in swatches"
        :key="s.cls"
        class="rounded-lg p-4 text-white font-semibold shadow-sm"
        :class="s.cls"
      >
        {{ s.label }}
      </div>
    </div>
  </main>
</template>
