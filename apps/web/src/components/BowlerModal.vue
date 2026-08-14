<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Player } from '../types'

// Shown at the end of an over to pick the next bowler (docs/UI_PLAN.md).
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
  <div class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-20 p-3">
    <div class="modal-card bg-card w-full max-w-md rounded-2xl shadow-lg p-5 space-y-4">
      <h3 class="text-lg font-bold text-slate-700">{{ title }}</h3>

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
    </div>
  </div>
</template>
