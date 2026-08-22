<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useMatchStore } from '../stores/match'
import { usePreferencesStore } from '../stores/preferences'
import { themeById } from '../designs/registry'
import type { BallPayload, OpenersPayload } from '../types'
import type { ExtrasKind } from '../components/ExtrasModal.vue'
import OpenersModal from '../components/OpenersModal.vue'
import WicketModal from '../components/WicketModal.vue'
import ExtrasModal from '../components/ExtrasModal.vue'
import BowlerModal from '../components/BowlerModal.vue'
import SettingsModal from '../components/SettingsModal.vue'
import Toast from '../components/Toast.vue'

const props = defineProps<{ id: string | number }>()
const router = useRouter()

const store = useMatchStore()
const {
  live,
  innings: inns,
  battingPlayers,
  bowlingPlayers,
  availableBatsmen,
  isLastWicket,
} = storeToRefs(store)

// The active theme ships its own dashboard (persisted in localStorage).
const prefs = usePreferencesStore()
const activeDashboard = computed(() => themeById(prefs.theme).dashboard)

const busy = ref(false)
const actionError = ref<string | null>(null)
const extrasKind = ref<ExtrasKind | null>(null)
const showWicket = ref(false)
const showFinishConfirm = ref(false)
const showSettings = ref(false)

onMounted(() => store.open(props.id))
onUnmounted(() => store.stopPolling())

// --- State flags ---
const needsOpeners = computed(() => !!inns.value && !inns.value.striker && !inns.value.is_completed)
// After each over the backend clears the bowler; the scorer must pick who
// bowls next. Cleared the instant changeBowler returns (bowler becomes set).
const needsBowler = computed(
  () => !!inns.value && !!inns.value.striker && !inns.value.is_completed && !inns.value.bowler,
)
const matchCompleted = computed(() => live.value?.status === 'COMPLETED')
const needsTransition = computed(
  () => !!inns.value?.is_completed && inns.value.innings_number === 1 && !matchCompleted.value,
)
const noUndo = computed(() => (inns.value?.legal_balls_bowled ?? 0) === 0)

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
function submitBowler(payload: { bowler_id: number }) {
  run(() => store.changeBowler(payload.bowler_id))
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
function undoLastBall() {
  run(() => store.undoLastBall())
}
</script>

<template>
  <div v-if="live" class="space-y-4 pb-24">
    <!-- Settings: switch dashboard design -->
    <div class="flex justify-end -mb-2">
      <button
        class="p-2 -mr-1 text-slate-400 active:scale-90"
        aria-label="Settings"
        @click="showSettings = true"
      >
        <svg
          class="h-6 w-6"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.7"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path
            d="M9.6 3.9c.09-.54.56-.94 1.11-.94h2.59c.55 0 1.02.4 1.11.94l.21 1.28c.06.37.31.69.65.87.32.2.72.26 1.07.12l1.22-.45c.52-.2 1.1 0 1.37.49l1.3 2.25c.27.47.16 1.08-.26 1.43l-1 .83c-.3.24-.44.61-.43.99v.26c-.01.38.13.75.43.99l1 .83c.42.35.53.96.26 1.43l-1.3 2.25c-.27.48-.85.68-1.37.49l-1.22-.46c-.35-.13-.75-.07-1.07.12-.34.19-.59.5-.65.87l-.21 1.28c-.09.54-.56.94-1.11.94h-2.59c-.55 0-1.02-.4-1.11-.94l-.21-1.28c-.06-.37-.31-.69-.65-.87-.32-.2-.72-.26-1.07-.12l-1.22.45c-.52.2-1.1 0-1.37-.49l-1.3-2.25a1.13 1.13 0 0 1 .26-1.43l1-.83c.3-.24.44-.61.43-.99v-.26c.01-.38-.13-.75-.43-.99l-1-.83a1.13 1.13 0 0 1-.26-1.43l1.3-2.25c.27-.48.85-.68 1.37-.49l1.22.46c.35.13.75.07 1.07-.12.34-.19.59-.5.65-.87l.21-1.28Z"
          />
          <circle cx="12" cy="12" r="3" />
        </svg>
      </button>
    </div>

    <!-- Active theme's dashboard (swappable via Settings) -->
    <Transition name="fade" mode="out-in">
      <component
        :is="activeDashboard"
        :key="prefs.theme"
        :live="live"
        :innings="inns"
        :busy="busy"
        :needs-bowler="needsBowler"
        :no-undo="noUndo"
        :match-completed="matchCompleted"
        @runs="runs"
        @extras="extrasKind = $event"
        @wicket="showWicket = true"
        @undo="undoLastBall"
        @finish="showFinishConfirm = true"
        @scorecard="router.push(`/match/${id}/live`)"
      />
    </Transition>

    <!-- Modals -->
    <Transition name="modal">
      <OpenersModal
        v-if="needsOpeners"
        :batting-players="battingPlayers"
        :bowling-players="bowlingPlayers"
        @confirm="submitOpeners"
      />
    </Transition>

    <Transition name="modal">
      <OpenersModal
        v-if="needsTransition"
        title="Innings Break — Set Openers for 2nd Innings"
        :batting-players="bowlingPlayers"
        :bowling-players="battingPlayers"
        @confirm="submitTransition"
      />
    </Transition>

    <Transition name="modal">
      <BowlerModal v-if="needsBowler" :bowling-players="bowlingPlayers" @confirm="submitBowler" />
    </Transition>

    <Transition name="modal">
      <WicketModal
        v-if="showWicket && inns?.striker && inns?.non_striker"
        :striker="inns.striker"
        :non-striker="inns.non_striker"
        :available-batsmen="availableBatsmen"
        :is-last-wicket="isLastWicket"
        @confirm="onWicket"
        @cancel="showWicket = false"
      />
    </Transition>

    <Transition name="modal">
      <ExtrasModal
        v-if="extrasKind"
        :kind="extrasKind"
        @confirm="onExtras"
        @cancel="extrasKind = null"
      />
    </Transition>

    <!-- Finish confirmation -->
    <Transition name="modal">
      <div
        v-if="showFinishConfirm"
        class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-20 p-3"
      >
        <div class="modal-card bg-card w-full max-w-md rounded-2xl shadow-lg p-5 space-y-4">
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
    </Transition>

    <!-- Settings -->
    <Transition name="modal">
      <SettingsModal
        v-if="showSettings"
        :current="prefs.theme"
        @select="prefs.setTheme($event)"
        @close="showSettings = false"
      />
    </Transition>

    <!-- Action errors float above every modal -->
    <Toast :message="actionError" @close="actionError = null" />
  </div>

  <p v-else class="text-slate-400 pt-10 text-center">Loading match…</p>
</template>
