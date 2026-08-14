<script setup lang="ts">
import ScoreHeader from '../components/ScoreHeader.vue'
import type { DashboardDesignProps, DashboardDesignEmits } from './contract'

defineProps<DashboardDesignProps>()
const emit = defineEmits<DashboardDesignEmits>()
</script>

<template>
  <div class="space-y-4">
    <ScoreHeader :live="live" />

    <!-- Active players -->
    <div
      v-if="innings && innings.striker"
      class="bg-card rounded-xl shadow-sm p-4 grid grid-cols-3 gap-2 text-sm"
    >
      <div>
        <p class="text-slate-400">Striker</p>
        <p class="font-semibold">★ {{ innings.striker.name }}</p>
        <p class="text-slate-500">{{ innings.striker.runs }} ({{ innings.striker.balls }})</p>
      </div>
      <div>
        <p class="text-slate-400">Non-striker</p>
        <p class="font-semibold">{{ innings.non_striker?.name ?? '—' }}</p>
        <p class="text-slate-500">
          {{ innings.non_striker?.runs ?? 0 }} ({{ innings.non_striker?.balls ?? 0 }})
        </p>
      </div>
      <div>
        <p class="text-slate-400">Bowler</p>
        <p class="font-semibold">{{ innings.bowler?.name ?? '—' }}</p>
        <p class="text-slate-500">
          {{ innings.bowler?.overs ?? '0.0' }}–{{ innings.bowler?.runs_conceded ?? 0 }}–{{
            innings.bowler?.wickets ?? 0
          }}
        </p>
      </div>
      <div class="col-span-3 flex gap-1 flex-wrap pt-2 border-t">
        <span class="text-slate-400 text-xs mr-1">This over:</span>
        <span
          v-for="(s, i) in innings.this_over"
          :key="i"
          class="text-xs font-bold bg-canvas border rounded px-1.5 py-0.5"
          >{{ s }}</span
        >
        <span v-if="!innings.this_over.length" class="text-xs text-slate-300">—</span>
      </div>
    </div>

    <!-- Match completed -->
    <div v-if="matchCompleted" class="bg-card rounded-xl shadow-sm p-6 text-center space-y-3">
      <p class="text-xl font-bold text-system">🏆 Match Completed</p>
      <button
        class="w-full bg-system text-white font-semibold rounded-xl py-4"
        @click="emit('scorecard')"
      >
        View Final Scorecard
      </button>
    </div>

    <!-- Scoring matrix -->
    <div
      v-else-if="innings && innings.striker && !innings.is_completed && !needsBowler"
      class="space-y-2"
    >
      <div class="grid grid-cols-4 gap-2">
        <button
          v-for="n in [0, 1, 2, 3]"
          :key="n"
          class="bg-runs text-white text-2xl font-bold rounded-xl py-6 active:scale-95 disabled:opacity-40"
          :disabled="busy"
          @click="emit('runs', n)"
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
          @click="emit('runs', n)"
        >
          {{ n }}
        </button>
      </div>
      <div class="grid grid-cols-3 gap-2">
        <button
          class="bg-wide text-white font-bold rounded-xl py-5 active:scale-95"
          @click="emit('extras', 'WIDE')"
        >
          Wide
        </button>
        <button
          class="bg-noball text-white font-bold rounded-xl py-5 active:scale-95"
          @click="emit('extras', 'NO_BALL')"
        >
          No Ball
        </button>
        <button
          class="bg-bye text-white font-bold rounded-xl py-5 active:scale-95"
          @click="emit('extras', 'BYE_LEGBYE')"
        >
          Bye / LB
        </button>
      </div>
      <button
        class="w-full bg-wicket text-white text-xl font-bold rounded-xl py-6 active:scale-95"
        @click="emit('wicket')"
      >
        Wicket!
      </button>

      <!-- Bottom control: end the match manually and lock scoring -->
      <button
        class="w-full mt-2 border-2 border-wicket text-wicket font-semibold rounded-xl py-3 active:scale-[0.99]"
        @click="emit('finish')"
      >
        Finish Match
      </button>
    </div>
  </div>
</template>
