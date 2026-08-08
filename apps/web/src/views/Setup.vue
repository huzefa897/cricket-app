<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'

const router = useRouter()

// Ad-hoc teams (Option A): names + on-the-fly rosters, no permanent directory.
const teams = reactive([
  { name: '', short: '', players: [], newPlayer: '' },
  { name: '', short: '', players: [], newPlayer: '' },
])

const totalOvers = ref(6)
const oversPresets = [2, 5, 6, 10, 20]
const tossWinnerIndex = ref(1) // 1 or 2
const tossDecision = ref('BAT') // BAT | BOWL

const submitting = ref(false)
const error = ref(null)

function addPlayer(team) {
  const name = team.newPlayer.trim()
  if (!name) return
  team.players.push({ name })
  team.newPlayer = ''
}

function removePlayer(team, idx) {
  team.players.splice(idx, 1)
}

const canStart = computed(
  () =>
    teams[0].name.trim() &&
    teams[1].name.trim() &&
    teams[0].players.length >= 2 &&
    teams[1].players.length >= 2,
)

async function startMatch() {
  if (!canStart.value || submitting.value) return
  submitting.value = true
  error.value = null
  try {
    const match = await api.createMatch({
      team_one_name: teams[0].name.trim(),
      team_two_name: teams[1].name.trim(),
      team_one_short: teams[0].short.trim(),
      team_two_short: teams[1].short.trim(),
      team_one_players: teams[0].players,
      team_two_players: teams[1].players,
      total_overs: Number(totalOvers.value),
      toss_winner_index: Number(tossWinnerIndex.value),
      toss_decision: tossDecision.value,
    })
    router.push(`/match/${match.id}/score`)
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="space-y-5">
    <h2 class="text-xl font-bold text-slate-700">Match Setup</h2>

    <!-- Teams + rosters -->
    <div v-for="(team, ti) in teams" :key="ti" class="bg-card rounded-xl shadow-sm p-4 space-y-3">
      <div class="flex gap-2">
        <input
          v-model="team.name"
          :placeholder="`Team ${ti + 1} name`"
          class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-system/40 outline-none"
        />
        <input
          v-model="team.short"
          placeholder="SHORT"
          maxlength="5"
          class="w-24 border rounded-lg px-3 py-2 uppercase focus:ring-2 focus:ring-system/40 outline-none"
        />
      </div>

      <div class="flex gap-2">
        <input
          v-model="team.newPlayer"
          placeholder="Add player to squad…"
          class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-system/40 outline-none"
          @keyup.enter="addPlayer(team)"
        />
        <button
          class="bg-system text-white px-4 rounded-lg font-semibold active:scale-95"
          @click="addPlayer(team)"
        >
          Add
        </button>
      </div>

      <div class="flex flex-wrap gap-2">
        <span
          v-for="(p, pi) in team.players"
          :key="pi"
          class="inline-flex items-center gap-1 bg-canvas border rounded-full pl-3 pr-2 py-1 text-sm"
        >
          {{ p.name }}
          <button class="text-wicket font-bold w-5 h-5" @click="removePlayer(team, pi)">×</button>
        </span>
        <span v-if="!team.players.length" class="text-slate-400 text-sm">No players yet.</span>
      </div>
      <p class="text-xs text-slate-400">{{ team.players.length }} players added</p>
    </div>

    <!-- Overs -->
    <div class="bg-card rounded-xl shadow-sm p-4 space-y-2">
      <label class="text-sm font-semibold text-slate-600">Total overs</label>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="o in oversPresets"
          :key="o"
          class="px-4 py-2 rounded-lg font-semibold border"
          :class="totalOvers === o ? 'bg-system text-white border-system' : 'bg-canvas text-slate-600'"
          @click="totalOvers = o"
        >
          {{ o }}
        </button>
        <input
          v-model.number="totalOvers"
          type="number"
          min="1"
          class="w-20 border rounded-lg px-3 py-2 text-center"
        />
      </div>
    </div>

    <!-- Toss -->
    <div class="bg-card rounded-xl shadow-sm p-4 space-y-3">
      <label class="text-sm font-semibold text-slate-600">Toss winner</label>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="ti in [1, 2]"
          :key="ti"
          class="px-4 py-3 rounded-lg font-semibold border truncate"
          :class="tossWinnerIndex === ti ? 'bg-system text-white border-system' : 'bg-canvas text-slate-600'"
          @click="tossWinnerIndex = ti"
        >
          {{ teams[ti - 1].name || `Team ${ti}` }}
        </button>
      </div>
      <label class="text-sm font-semibold text-slate-600">Decision</label>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="d in ['BAT', 'BOWL']"
          :key="d"
          class="px-4 py-3 rounded-lg font-semibold border"
          :class="tossDecision === d ? 'bg-system text-white border-system' : 'bg-canvas text-slate-600'"
          @click="tossDecision = d"
        >
          {{ d === 'BAT' ? 'Bat first' : 'Bowl first' }}
        </button>
      </div>
    </div>

    <p v-if="error" class="text-wicket text-sm">{{ error }}</p>

    <button
      class="w-full bg-system text-white text-lg font-bold rounded-xl py-5 shadow-sm disabled:opacity-40 active:scale-[0.99] transition-transform"
      :disabled="!canStart || submitting"
      @click="startMatch"
    >
      {{ submitting ? 'Starting…' : 'Start Match & Open Scorer' }}
    </button>
  </div>
</template>
