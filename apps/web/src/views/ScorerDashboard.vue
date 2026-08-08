<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import { useLiveMatch } from '../composables/useLiveMatch'
import ScoreHeader from '../components/ScoreHeader.vue'
import OpenersModal from '../components/OpenersModal.vue'
import WicketModal from '../components/WicketModal.vue'
import ExtrasModal from '../components/ExtrasModal.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const router = useRouter()

const { live, refresh, start } = useLiveMatch(props.id)
const detail = ref(null) // rosters
const dismissed = ref(new Set()) // player ids already out (this innings)
const busy = ref(false)
const actionError = ref(null)

const extrasKind = ref(null) // 'WIDE' | 'NO_BALL' | 'BYE_LEGBYE' | null
const showWicket = ref(false)
const showTransition = ref(false)

onMounted(async () => {
  detail.value = await api.getMatch(props.id)
  start()
})

// --- Roster helpers -------------------------------------------------------
function playersOfTeam(name) {
  if (!detail.value) return []
  for (const t of [detail.value.team_one, detail.value.team_two]) {
    if (t.name === name) return t.players
  }
  return []
}
const battingPlayers = computed(() => playersOfTeam(live.value?.innings?.batting_team))
const bowlingPlayers = computed(() => playersOfTeam(live.value?.innings?.bowling_team))

// --- Match state flags -----------------------------------------------------
const inns = computed(() => live.value?.innings ?? null)
const needsOpeners = computed(() => inns.value && !inns.value.striker && !inns.value.is_completed)
const matchCompleted = computed(() => live.value?.status === 'COMPLETED')
const needsTransition = computed(
  () => inns.value?.is_completed && inns.value.innings_number === 1 && !matchCompleted.value,
)

const isLastWicket = computed(() => {
  const total = battingPlayers.value.length
  return total > 0 && inns.value && inns.value.total_wickets >= total - 2
})
const availableBatsmen = computed(() =>
  battingPlayers.value.filter(
    (p) =>
      p.id !== inns.value?.striker?.id &&
      p.id !== inns.value?.non_striker?.id &&
      !dismissed.value.has(p.id),
  ),
)

// --- Actions ---------------------------------------------------------------
async function send(payload) {
  if (busy.value) return
  busy.value = true
  actionError.value = null
  try {
    await api.recordBall(props.id, payload)
    await refresh()
  } catch (e) {
    actionError.value = e.message
  } finally {
    busy.value = false
  }
}

function runs(n) {
  send({ runs_scored_bat: n })
}

async function submitOpeners(payload) {
  await api.setOpeners(props.id, payload)
  await refresh()
}

function onExtras(payload) {
  extrasKind.value = null
  send(payload)
}

function onWicket(payload) {
  showWicket.value = false
  if (payload.player_dismissed_id) dismissed.value.add(payload.player_dismissed_id)
  send(payload)
}

async function submitTransition(payload) {
  await api.transitionInnings(props.id, payload)
  dismissed.value = new Set()
  await refresh()
}
</script>

<template>
  <div v-if="live" class="space-y-4 pb-24">
    <ScoreHeader :live="live" />

    <!-- Active players -->
    <div v-if="inns && inns.striker" class="bg-card rounded-xl shadow-sm p-4 grid grid-cols-3 gap-2 text-sm">
      <div>
        <p class="text-slate-400">Striker</p>
        <p class="font-semibold">★ {{ inns.striker.name }}</p>
        <p class="text-slate-500">{{ inns.striker.runs }} ({{ inns.striker.balls }})</p>
      </div>
      <div>
        <p class="text-slate-400">Non-striker</p>
        <p class="font-semibold">{{ inns.non_striker?.name ?? '—' }}</p>
        <p class="text-slate-500">{{ inns.non_striker?.runs ?? 0 }} ({{ inns.non_striker?.balls ?? 0 }})</p>
      </div>
      <div>
        <p class="text-slate-400">Bowler</p>
        <p class="font-semibold">{{ inns.bowler?.name ?? '—' }}</p>
        <p class="text-slate-500">
          {{ inns.bowler?.overs ?? '0.0' }}–{{ inns.bowler?.runs_conceded ?? 0 }}–{{ inns.bowler?.wickets ?? 0 }}
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
    </div>

    <!-- Modals -->
    <OpenersModal
      v-if="needsOpeners"
      :battingPlayers="battingPlayers"
      :bowlingPlayers="bowlingPlayers"
      @confirm="submitOpeners"
    />

    <OpenersModal
      v-if="needsTransition"
      title="Innings Break — Set Openers for 2nd Innings"
      :battingPlayers="bowlingPlayers"
      :bowlingPlayers="battingPlayers"
      @confirm="submitTransition"
    />

    <WicketModal
      v-if="showWicket && inns?.striker"
      :striker="inns.striker"
      :nonStriker="inns.non_striker"
      :availableBatsmen="availableBatsmen"
      :isLastWicket="isLastWicket"
      @confirm="onWicket"
      @cancel="showWicket = false"
    />

    <ExtrasModal
      v-if="extrasKind"
      :kind="extrasKind"
      @confirm="onExtras"
      @cancel="extrasKind = null"
    />
  </div>

  <p v-else class="text-slate-400 pt-10 text-center">Loading match…</p>
</template>
