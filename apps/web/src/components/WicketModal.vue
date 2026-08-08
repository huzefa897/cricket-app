<script setup>
import { computed, ref } from 'vue'

// 5-step guided Wicket Wizard (docs/UI_PLAN.md §3). Back buttons at every stage;
// a final confirmation summary before the delivery is sent.
const props = defineProps({
  striker: { type: Object, required: true }, // {id, name}
  nonStriker: { type: Object, required: true },
  availableBatsmen: { type: Array, required: true }, // not currently on strike/non-strike
  isLastWicket: { type: Boolean, default: false },
})
const emit = defineEmits(['confirm', 'cancel'])

const DISMISSALS = ['BOWLED', 'CAUGHT', 'RUN_OUT', 'STUMPED', 'LBW']
const step = ref(1)
const wicketType = ref(null)
const dismissedId = ref(null)
const incomingId = ref(null)
const newStrikerId = ref(null)

function pickType(t) {
  wicketType.value = t
  step.value = 2
}
function pickDismissed(id) {
  dismissedId.value = id
  step.value = props.isLastWicket ? 5 : 3
}
function pickIncoming(id) {
  incomingId.value = id
  step.value = 4
}
function pickStrike(id) {
  newStrikerId.value = id
  step.value = 5
}

const dismissedName = computed(() =>
  dismissedId.value === props.striker.id ? props.striker.name : props.nonStriker.name,
)
const incomingName = computed(
  () => props.availableBatsmen.find((p) => p.id === incomingId.value)?.name ?? '—',
)
const newStrikerName = computed(() => {
  if (props.isLastWicket) return '—'
  return newStrikerId.value === incomingId.value ? incomingName.value : 'Non-striker stays'
})

function confirm() {
  emit('confirm', {
    wicket_type: wicketType.value,
    player_dismissed_id: dismissedId.value,
    incoming_batsman_id: props.isLastWicket ? null : incomingId.value,
    new_striker_id: props.isLastWicket ? null : newStrikerId.value,
  })
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-20 p-3">
    <div class="bg-card w-full max-w-md rounded-2xl shadow-lg p-5 space-y-4">
      <div class="flex items-center">
        <h3 class="text-lg font-bold text-wicket">Wicket! — Step {{ step }}/5</h3>
        <button class="ml-auto text-slate-400" @click="emit('cancel')">Cancel</button>
      </div>

      <!-- Step 1: dismissal type -->
      <div v-if="step === 1" class="grid grid-cols-2 gap-2">
        <button
          v-for="t in DISMISSALS"
          :key="t"
          class="bg-wicket text-white font-semibold rounded-lg py-4 active:scale-95"
          @click="pickType(t)"
        >
          {{ t.replace('_', ' ') }}
        </button>
      </div>

      <!-- Step 2: who got out -->
      <div v-else-if="step === 2" class="space-y-2">
        <p class="text-sm text-slate-500">Who got out?</p>
        <div class="grid grid-cols-2 gap-2">
          <button
            class="bg-runs text-white font-semibold rounded-lg py-5 active:scale-95"
            @click="pickDismissed(striker.id)"
          >
            {{ striker.name }}<br /><span class="text-xs opacity-80">(Striker)</span>
          </button>
          <button
            class="bg-runs text-white font-semibold rounded-lg py-5 active:scale-95"
            @click="pickDismissed(nonStriker.id)"
          >
            {{ nonStriker.name }}<br /><span class="text-xs opacity-80">(Non-striker)</span>
          </button>
        </div>
        <button class="text-slate-400 text-sm" @click="step = 1">← Back</button>
      </div>

      <!-- Step 3: incoming batsman -->
      <div v-else-if="step === 3" class="space-y-2">
        <p class="text-sm text-slate-500">Incoming batsman</p>
        <select v-model="incomingId" class="w-full border rounded-lg px-3 py-2">
          <option :value="null" disabled>Choose batsman…</option>
          <option v-for="p in availableBatsmen" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
        <div class="flex gap-2">
          <button class="text-slate-400 text-sm flex-1 text-left" @click="step = 2">← Back</button>
          <button
            class="bg-system text-white px-5 py-2 rounded-lg font-semibold disabled:opacity-40"
            :disabled="!incomingId"
            @click="pickIncoming(incomingId)"
          >
            Next
          </button>
        </div>
      </div>

      <!-- Step 4: next strike decider -->
      <div v-else-if="step === 4" class="space-y-2">
        <p class="text-sm text-slate-500">Who is on strike for the next ball?</p>
        <div class="grid gap-2">
          <button
            class="bg-runs text-white font-semibold rounded-lg py-4 active:scale-95"
            @click="pickStrike(incomingId)"
          >
            Incoming batsman takes strike
          </button>
          <button
            class="bg-runs text-white font-semibold rounded-lg py-4 active:scale-95"
            @click="pickStrike(nonStriker.id === dismissedId ? incomingId : nonStriker.id)"
          >
            Non-striker stays on strike
          </button>
        </div>
        <button class="text-slate-400 text-sm" @click="step = 3">← Back</button>
      </div>

      <!-- Step 5: overview + confirm -->
      <div v-else class="space-y-3">
        <div class="bg-canvas rounded-lg p-4 space-y-1 text-sm">
          <div class="flex justify-between">
            <span class="text-slate-500">Dismissal</span
            ><span class="font-semibold">{{ wicketType.replace('_', ' ') }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">Out</span><span class="font-semibold">{{ dismissedName }}</span>
          </div>
          <div v-if="!isLastWicket" class="flex justify-between">
            <span class="text-slate-500">Incoming</span
            ><span class="font-semibold">{{ incomingName }}</span>
          </div>
          <div v-if="!isLastWicket" class="flex justify-between">
            <span class="text-slate-500">On strike</span
            ><span class="font-semibold">{{ newStrikerName }}</span>
          </div>
          <p v-else class="text-wicket font-semibold">All out — innings ends.</p>
        </div>
        <div class="flex gap-2">
          <button
            class="text-slate-400 text-sm flex-1 text-left"
            @click="step = isLastWicket ? 2 : 4"
          >
            ← Back
          </button>
          <button
            class="bg-wicket text-white px-6 py-3 rounded-xl font-bold active:scale-95"
            @click="confirm"
          >
            Confirm & Send
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
