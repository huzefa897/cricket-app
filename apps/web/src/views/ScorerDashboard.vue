<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useMatchStore } from '../stores/match'
import type { BallPayload, OpenersPayload } from '../types'
import type { ExtrasKind } from '../components/ExtrasModal.vue'
import ScoreHeader from '../components/ScoreHeader.vue'
import OpenersModal from '../components/OpenersModal.vue'
import WicketModal from '../components/WicketModal.vue'
import ExtrasModal from '../components/ExtrasModal.vue'

const props = defineProps<{ id: string | number }>()
const router = useRouter()

const store = useMatchStore()
const { live, innings: inns, battingPlayers, bowlingPlayers, availableBatsmen, isLastWicket } =
  storeToRefs(store)

const busy = ref(false)
const actionError = ref<string | null>(null)
const extrasKind = ref<ExtrasKind | null>(null)
const showWicket = ref(false)
const showFinishConfirm = ref(false)

onMounted(() => store.open(props.id))
onUnmounted(() => store.stopPolling())

// --- State flags ---
const needsOpeners = computed(() => !!inns.value && !inns.value.striker && !inns.value.is_completed)
const matchCompleted = computed(() => live.value?.status === 'COMPLETED')
const needsTransition = computed(
  () => !!inns.value?.is_completed && inns.value.innings_number === 1 && !matchCompleted.value,
)

// --- Actions ---
async function run<T>(fn: () => Promise<T>) {
  if (busy.value) return
  busy.value = true
  actionError.value = null
  try {
    await fn()
  } catch (e) {
    actionError.value = (e as Error).message
  } finally {
    busy.value = false
  }
}

function runs(n: number) {
  run(() => store.recordBall({ runs_scored_bat: n }))
}
function submitOpeners(payload: OpenersPayload) {
  run(() => store.setOpeners(payload))
}
function onExtras(payload: BallPayload) {
  extrasKind.value = null
  run(() => store.recordBall(payload))
}
function onWicket(payload: BallPayload) {
  showWicket.value = false
  run(() => store.recordBall(payload))
}
function submitTransition(payload: OpenersPayload) {
  run(() => store.transition(payload))
}
function finishMatch() {
  showFinishConfirm.value = false
  run(() => store.finish())
}
</script>

<template>
  <div v-if="live" class="space-y-4 pb-24">
    <ScoreHeader :live="live" />

    <!-- Active players -->
    <div
      v-if="inns && inns.striker"
      class="bg-card rounded-xl shadow-sm p-4 grid grid-cols-3 gap-2 text-sm"
    >
      <div>
        <p class="text-slate-400">Striker</p>
        <p class="font-semibold">★ {{ inns.striker.name }}</p>
        <p class="text-slate-500">{{ inns.striker.runs }} ({{ inns.striker.balls }})</p>
      </div>
      <div>
        <p class="text-slate-400">Non-striker</p>
        <p class="font-semibold">{{ inns.non_striker?.name ?? '—' }}</p>
        <p class="text-slate-500">
          {{ inns.non_striker?.runs ?? 0 }} ({{ inns.non_striker?.balls ?? 0 }})
        </p>
      </div>
      <div>
        <p class="text-slate-400">Bowler</p>
        <p class="font-semibold">{{ inns.bowler?.name ?? '—' }}</p>
        <p class="text-slate-500">
          {{ inns.bowler?.overs ?? '0.0' }}–{{ inns.bowler?.runs_conceded ?? 0 }}–{{
            inns.bowler?.wickets ?? 0
          }}
        </p>
      </div>
      <div class="col-span-3 flex gap-1 flex-wrap pt-2 border-t">
        <span class="text-slate-400 text-xs mr-1">This over:</span>
        <span
          v-for="(s, i) in inns.this_over"
          :key="i"
          class="text-xs font-bold bg-canvas border rounded px-1.5 py-0.5"
          >{{ s }}</span
        >
        <span v-if="!inns.this_over.length" class="text-xs text-slate-300">—</span>
      </div>
    </div>

    <p v-if="actionError" class="text-wicket text-sm">{{ actionError }}</p>

    <!-- Match completed -->
    <div v-if="matchCompleted" class="bg-card rounded-xl shadow-sm p-6 text-center space-y-3">
      <p class="text-xl font-bold text-system">🏆 Match Completed</p>
      <button
        class="w-full bg-system text-white font-semibold rounded-xl py-4"
        @click="router.push(`/match/${id}/live`)"
      >
        View Final Scorecard
      </button>
    </div>

    <!-- Scoring matrix -->
    <div v-else-if="inns && inns.striker && !inns.is_completed" class="space-y-2">
      <div class="grid grid-cols-4 gap-2">
        <button
          v-for="n in [0, 1, 2, 3]"
          :key="n"
          class="bg-runs text-white text-2xl font-bold rounded-xl py-6 active:scale-95 disabled:opacity-40"
          :disabled="busy"
          @click="runs(n)"
        >
          {{ n }}
        </button>
      </div>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="n in [4, 6]"
          :key="n"
          class="bg-boundary text-white text-2xl font-bold rounded-xl py-6 active:scale-95 disabled:opacity-40"
          :disabled="busy"
          @click="runs(n)"
        >
          {{ n }}
        </button>
      </div>
      <div class="grid grid-cols-3 gap-2">
        <button
          class="bg-wide text-white font-bold rounded-xl py-5 active:scale-95"
          @click="extrasKind = 'WIDE'"
        >
          Wide
        </button>
        <button
          class="bg-noball text-white font-bold rounded-xl py-5 active:scale-95"
          @click="extrasKind = 'NO_BALL'"
        >
          No Ball
        </button>
        <button
          class="bg-bye text-white font-bold rounded-xl py-5 active:scale-95"
          @click="extrasKind = 'BYE_LEGBYE'"
        >
          Bye / LB
        </button>
      </div>
      <button
        class="w-full bg-wicket text-white text-xl font-bold rounded-xl py-6 active:scale-95"
        @click="showWicket = true"
      >
        Wicket!
      </button>

      <!-- Bottom control: end the match manually and lock scoring -->
      <button
        class="w-full mt-2 border-2 border-wicket text-wicket font-semibold rounded-xl py-3 active:scale-[0.99]"
        @click="showFinishConfirm = true"
      >
        Finish Match
      </button>
    </div>

    <!-- Modals -->
    <OpenersModal
      v-if="needsOpeners"
      :batting-players="battingPlayers"
      :bowling-players="bowlingPlayers"
      @confirm="submitOpeners"
    />

    <OpenersModal
      v-if="needsTransition"
      title="Innings Break — Set Openers for 2nd Innings"
      :batting-players="bowlingPlayers"
      :bowling-players="battingPlayers"
      @confirm="submitTransition"
    />

    <WicketModal
      v-if="showWicket && inns?.striker && inns?.non_striker"
      :striker="inns.striker"
      :non-striker="inns.non_striker"
      :available-batsmen="availableBatsmen"
      :is-last-wicket="isLastWicket"
      @confirm="onWicket"
      @cancel="showWicket = false"
    />

    <ExtrasModal v-if="extrasKind" :kind="extrasKind" @confirm="onExtras" @cancel="extrasKind = null" />

    <!-- Finish confirmation -->
    <div
      v-if="showFinishConfirm"
      class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-20 p-3"
    >
      <div class="bg-card w-full max-w-md rounded-2xl shadow-lg p-5 space-y-4">
        <h3 class="text-lg font-bold text-wicket">Finish this match?</h3>
        <p class="text-sm text-slate-500">
          This ends the match now and <b>locks the score</b>. No more balls can be recorded. This
          cannot be undone.
        </p>
        <div class="flex gap-2">
          <button
            class="flex-1 border rounded-xl py-3 font-semibold text-slate-600"
            @click="showFinishConfirm = false"
          >
            Cancel
          </button>
          <button
            class="flex-1 bg-wicket text-white rounded-xl py-3 font-bold active:scale-95"
            @click="finishMatch"
          >
            Finish &amp; Lock
          </button>
        </div>
      </div>
    </div>
  </div>

  <p v-else class="text-slate-400 pt-10 text-center">Loading match…</p>
</template>
