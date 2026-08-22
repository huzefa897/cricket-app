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
import type { OpenersPayload, Player } from '../types'

// Reused for Innings-1 openers and after the innings transition.
// Wrapped in Reka's Dialog for focus trap, initial focus, scroll-lock and
// dialog semantics. Like BowlerModal this is intentionally NON-dismissible —
// starting an innings without openers would deadlock scoring — so Escape and
// outside-click are prevented and there is no close affordance.
const props = withDefaults(
  defineProps<{
    title?: string
    battingPlayers: Player[]
    bowlingPlayers: Player[]
  }>(),
  { title: 'Select Opening Players' },
)
const emit = defineEmits<{ confirm: [OpenersPayload] }>()

const strikerId = ref<number | null>(null)
const nonStrikerId = ref<number | null>(null)
const bowlerId = ref<number | null>(null)

const nonStrikerOptions = computed(() =>
  props.battingPlayers.filter((p) => p.id !== strikerId.value),
)
const ready = computed(
  () =>
    strikerId.value &&
    nonStrikerId.value &&
    bowlerId.value &&
    strikerId.value !== nonStrikerId.value,
)

function confirm() {
  if (!ready.value) return
  emit('confirm', {
    striker_id: strikerId.value!,
    non_striker_id: nonStrikerId.value!,
    bowler_id: bowlerId.value!,
  })
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
          Choose the two opening batters and the opening bowler to start the innings.
        </DialogDescription>

        <div class="space-y-1">
          <label class="text-sm font-semibold text-slate-600">Striker</label>
          <select v-model="strikerId" class="w-full border rounded-lg px-3 py-2">
            <option :value="null" disabled>Choose striker…</option>
            <option v-for="p in battingPlayers" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="text-sm font-semibold text-slate-600">Non-striker</label>
          <select v-model="nonStrikerId" class="w-full border rounded-lg px-3 py-2">
            <option :value="null" disabled>Choose non-striker…</option>
            <option v-for="p in nonStrikerOptions" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="text-sm font-semibold text-slate-600">Opening bowler</label>
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
          Confirm & Start
        </button>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
