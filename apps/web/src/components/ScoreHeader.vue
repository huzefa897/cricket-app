<script setup lang="ts">
import type { LiveState } from '../types'

// Compact live summary shared by the scorer and viewer screens.
withDefaults(defineProps<{ live: LiveState; big?: boolean }>(), { big: false })
</script>

<template>
  <div class="bg-card rounded-xl shadow-sm p-4">
    <div v-if="live.innings" class="space-y-2">
      <div class="flex items-baseline justify-between">
        <span class="font-semibold text-slate-600 truncate">{{ live.innings.batting_team }}</span>
        <span class="text-slate-400 text-sm">Inns {{ live.innings.innings_number }}</span>
      </div>

      <div class="flex items-baseline gap-3">
        <span :class="big ? 'text-5xl' : 'text-4xl'" class="font-extrabold text-slate-800">
          {{ live.innings.total_runs }}/{{ live.innings.total_wickets }}
        </span>
        <span class="text-slate-500 font-medium"
          >({{ live.innings.overs }} / {{ live.total_overs }})</span
        >
      </div>

      <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-500">
        <span
          >CRR <b class="text-slate-700">{{ live.innings.crr }}</b></span
        >
        <span v-if="live.innings.rrr !== null"
          >RRR <b class="text-slate-700">{{ live.innings.rrr }}</b></span
        >
        <span v-if="live.innings.target"
          >Target <b class="text-slate-700">{{ live.innings.target }}</b></span
        >
      </div>

      <div v-if="live.innings.target" class="text-sm text-boundary font-semibold">
        Need {{ Math.max(live.innings.target - live.innings.total_runs, 0) }} runs
      </div>
    </div>
    <p v-else class="text-slate-400">Waiting for the match to start…</p>
  </div>
</template>
