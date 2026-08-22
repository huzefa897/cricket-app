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
import type { BallPayload, BatterStat, Player, WicketType } from '../types'

// 5-step guided Wicket Wizard (docs/UI_PLAN.md §3). Back buttons at every stage;
// a final confirmation summary before the delivery is sent.
const props = withDefaults(
  defineProps<{
    striker: BatterStat
    nonStriker: BatterStat
    availableBatsmen: Player[] // not currently on strike/non-strike
    isLastWicket?: boolean
  }>(),
  { isLastWicket: false },
)
const emit = defineEmits<{ confirm: [BallPayload]; cancel: [] }>()

const DISMISSALS: WicketType[] = ['BOWLED', 'CAUGHT', 'RUN_OUT', 'STUMPED', 'LBW']
const step = ref(1)
const wicketType = ref<WicketType | null>(null)
const dismissedId = ref<number | null>(null)
const incomingId = ref<number | null>(null)
const newStrikerId = ref<number | null>(null)
// Runs completed before the dismissal — only run-outs can score off the delivery.
const runsCompleted = ref(0)

const isRunOut = computed(() => wicketType.value === 'RUN_OUT')

function pickType(t: WicketType) {
  wicketType.value = t
  if (t !== 'RUN_OUT') runsCompleted.value = 0
  step.value = 2
}
function pickDismissed(id: number) {
  dismissedId.value = id
  step.value = props.isLastWicket ? 5 : 3
}
function pickIncoming(id: number | null) {
  incomingId.value = id
  step.value = 4
}
function pickStrike(id: number | null) {
  newStrikerId.value = id
  step.value = 5
}

const dismissedName = computed(() =>
  dismissedId.value === props.striker.id ? props.striker.name : props.nonStriker.name,
)
// The batter who was NOT dismissed and stays at the crease alongside the incoming one.
const survivor = computed(() =>
  dismissedId.value === props.striker.id ? props.nonStriker : props.striker,
)
const incomingName = computed(
  () => props.availableBatsmen.find((p) => p.id === incomingId.value)?.name ?? '—',
)
const newStrikerName = computed(() => {
  if (props.isLastWicket) return '—'
  return newStrikerId.value === incomingId.value ? incomingName.value : survivor.value.name
})

function confirm() {
  emit('confirm', {
    is_wicket: true,
    wicket_type: wicketType.value ?? 'NONE',
    runs_scored_bat: runsCompleted.value,
    player_dismissed_id: dismissedId.value,
    incoming_batsman_id: props.isLastWicket ? null : incomingId.value,
    new_striker_id: props.isLastWicket ? null : newStrikerId.value,
  })
}
</script>

<template>
  <DialogRoot :open="true" @update:open="(o) => !o && emit('cancel')">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-20 bg-black/40" />
      <DialogContent
        class="modal-card bg-card fixed z-20 inset-x-3 bottom-3 mx-auto w-auto max-w-md rounded-2xl p-5 shadow-lg space-y-4 sm:inset-x-auto sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:w-full sm:-translate-x-1/2 sm:-translate-y-1/2"
      >
        <div class="flex items-center">
          <DialogTitle class="text-lg font-bold text-wicket"
            >Wicket! — Step {{ step }}/5</DialogTitle
          >
          <button class="ml-auto text-slate-400" @click="emit('cancel')">Cancel</button>
        </div>
        <DialogDescription class="sr-only">
          Guided steps to record a dismissal: type, who is out, the incoming batter and who takes
          strike.
        </DialogDescription>

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
          <!-- Run-outs can complete runs before the dismissal -->
          <div v-if="isRunOut" class="space-y-1">
            <p class="text-sm text-slate-500">Runs completed before the run-out</p>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="n in [0, 1, 2, 3]"
                :key="n"
                class="font-bold rounded-lg py-3 active:scale-95"
                :class="
                  runsCompleted === n ? 'bg-runs text-white' : 'bg-canvas border text-slate-600'
                "
                @click="runsCompleted = n"
              >
                {{ n }}
              </button>
            </div>
          </div>
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
            <button class="text-slate-400 text-sm flex-1 text-left" @click="step = 2">
              ← Back
            </button>
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
              @click="pickStrike(survivor.id)"
            >
              {{ survivor.name }} stays on strike
            </button>
          </div>
          <button class="text-slate-400 text-sm" @click="step = 3">← Back</button>
        </div>

        <!-- Step 5: overview + confirm -->
        <div v-else class="space-y-3">
          <div class="bg-canvas rounded-lg p-4 space-y-1 text-sm">
            <div class="flex justify-between">
              <span class="text-slate-500">Dismissal</span
              ><span class="font-semibold">{{ wicketType?.replace('_', ' ') }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Out</span
              ><span class="font-semibold">{{ dismissedName }}</span>
            </div>
            <div v-if="isRunOut" class="flex justify-between">
              <span class="text-slate-500">Runs</span
              ><span class="font-semibold">{{ runsCompleted }}</span>
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
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
