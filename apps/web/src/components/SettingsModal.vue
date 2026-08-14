<script setup lang="ts">
import { THEMES } from '../designs/registry'

// Lets the user pick an app theme. Selection is applied immediately
// (the parent persists it via the preferences store).
defineProps<{ current: string }>()
const emit = defineEmits<{ select: [id: string]; close: [] }>()
</script>

<template>
  <div
    class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-20 p-3"
    @click.self="emit('close')"
  >
    <div class="modal-card bg-card w-full max-w-md rounded-2xl shadow-lg p-5 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-bold text-slate-700">Theme</h3>
        <button class="text-slate-400 active:scale-90" aria-label="Close" @click="emit('close')">
          <svg
            class="h-5 w-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <p class="text-sm text-slate-500">
        Changes the look across the whole app. Saved on this device.
      </p>

      <div class="space-y-2">
        <button
          v-for="t in THEMES"
          :key="t.id"
          class="w-full text-left rounded-xl border p-3 active:scale-[0.99] flex items-center gap-3"
          :class="
            t.id === current
              ? 'border-system bg-system/5 ring-1 ring-system'
              : 'border-slate-200 bg-card'
          "
          @click="emit('select', t.id)"
        >
          <!-- Tiny live swatch of the theme's world -->
          <span
            class="h-10 w-10 shrink-0 rounded-lg border border-white/20"
            :style="
              t.id === 'frosted'
                ? 'background: radial-gradient(120% 80% at 10% 0%, #ff7a45 0%, transparent 50%), radial-gradient(120% 90% at 100% 10%, #b23cff 0%, transparent 55%), linear-gradient(165deg,#3a1d8a,#150e30)'
                : 'background: #F8F9FA'
            "
          />
          <span class="min-w-0 flex-1">
            <span class="flex items-center justify-between">
              <span class="font-semibold text-slate-700">{{ t.name }}</span>
              <span v-if="t.id === current" class="text-system text-sm font-bold">✓ Active</span>
            </span>
            <span class="block text-sm text-slate-500 mt-0.5">{{ t.description }}</span>
          </span>
        </button>
      </div>
    </div>
  </div>
</template>
