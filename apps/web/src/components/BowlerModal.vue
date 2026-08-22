<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  DialogRoot,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from 'reka-ui'
import type { Player } from '../types'

// Shown at the end of an over to pick the next bowler (docs/UI_PLAN.md).
// Wrapped in Reka's Dialog for focus trap, initial focus, scroll-lock and
// dialog semantics. This modal is intentionally NON-dismissible — leaving
// without a bowler would deadlock scoring — so Escape and outside-click are
// prevented and there is no close affordance.
withDefaults(
  defineProps<{
    title?: string
    bowlingPlayers: Player[]
  }>(),
  { title: 'Select Bowler' },
)
const emit = defineEmits<{ confirm: [{ bowler_id: number }] }>()

const bowlerId = ref<number | null>(null)

const ready = computed(() => bowlerId.value !== null)

function confirm() {
  if (!ready.value) return
  emit('confirm', { bowler_id: bowlerId.value! })
}
</script>

<template>
  <DialogRoot :open="true">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-20 bg-black/40" />
      <DialogContent
        class="modal-card bg-card fixed z-20 inset-x-3 bottom-3 mx-auto w-auto max-w-md rounded-2xl p-5 shadow-lg space-y-4 sm:inset-x-auto sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:w-full sm:-translate-x-1/2 sm:-translate-y-1/2"
        @escape-key-down.prevent
        @pointer-down-outside.prevent
        @interact-outside.prevent
      >
        <DialogTitle class="text-lg font-bold text-slate-700">{{ title }}</DialogTitle>
        <DialogDescription class="sr-only">
          Choose the bowler for the next over to continue scoring.
        </DialogDescription>

        <div class="space-y-1">
          <label class="text-sm font-semibold text-slate-600">New bowler</label>
          <select v-model="bowlerId" class="w-full border rounded-lg px-3 py-2">
            <option :value="null" disabled>Choose bowler…</option>
            <option v-for="p in bowlingPlayers" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <button
          class="w-full bg-system text-white font-bold rounded-xl py-4 disabled:opacity-40 active:scale-[0.99]"
          :disabled="!ready"
          @click="confirm"
        >
          Confirm
        </button>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
