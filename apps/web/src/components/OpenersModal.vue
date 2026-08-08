<script setup>
import { computed, ref } from 'vue'

// Reused for Innings-1 openers and after the innings transition.
const props = defineProps({
  title: { type: String, default: 'Select Opening Players' },
  battingPlayers: { type: Array, required: true },
  bowlingPlayers: { type: Array, required: true },
})
const emit = defineEmits(['confirm'])

const strikerId = ref(null)
const nonStrikerId = ref(null)
const bowlerId = ref(null)

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
    striker_id: strikerId.value,
    non_striker_id: nonStrikerId.value,
    bowler_id: bowlerId.value,
  })
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-20 p-3">
    <div class="bg-card w-full max-w-md rounded-2xl shadow-lg p-5 space-y-4">
      <h3 class="text-lg font-bold text-slate-700">{{ title }}</h3>

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
    </div>
  </div>
</template>
