<script setup lang="ts">
import {
  DialogRoot,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from 'reka-ui'
import { THEMES } from '../designs/registry'

// Lets the user pick an app theme. Selection is applied immediately
// (the parent persists it via the preferences store). Dismissible — Escape,
// outside-click and the ✕ all close it via the `close` emit.
defineProps<{ current: string }>()
const emit = defineEmits<{ select: [id: string]; close: [] }>()
</script>

<template>
  <DialogRoot :open="true" @update:open="(o) => !o && emit('close')">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-20 bg-black/40" />
      <DialogContent
        class="modal-card bg-card fixed z-20 inset-x-3 bottom-3 mx-auto w-auto max-w-md rounded-2xl p-5 shadow-lg space-y-4 sm:inset-x-auto sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:w-full sm:-translate-x-1/2 sm:-translate-y-1/2"
      >
        <div class="flex items-center justify-between">
          <DialogTitle class="text-lg font-bold text-slate-700">Theme</DialogTitle>
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

        <DialogDescription class="text-sm text-slate-500">
          Changes the look across the whole app. Saved on this device.
        </DialogDescription>

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
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
