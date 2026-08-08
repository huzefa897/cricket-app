<script setup>
import { computed, onMounted } from 'vue'
import { useLiveMatch } from '../composables/useLiveMatch'
import ScoreHeader from '../components/ScoreHeader.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const { live, start } = useLiveMatch(props.id, { intervalMs: 3000 })
onMounted(start)

const inns = computed(() => live.value?.innings ?? null)
</script>

<template>
  <div v-if="live" class="space-y-4">
    <ScoreHeader :live="live" big />

    <div v-if="live.status === 'COMPLETED'" class="bg-system text-white rounded-xl p-4 text-center font-bold">
      🏆 Match Completed
    </div>

    <!-- Over ticker -->
    <div v-if="inns" class="bg-card rounded-xl shadow-sm p-4">
      <p class="text-slate-400 text-sm mb-2">This over</p>
      <div class="flex gap-2 overflow-x-auto pb-1">
        <span
          v-for="(s, i) in inns.this_over"
          :key="i"
          class="shrink-0 min-w-9 h-9 px-2 grid place-items-center rounded-full font-bold text-white"
          :class="s === 'W' ? 'bg-wicket' : s.includes('wd') || s.includes('nb') ? 'bg-wide' : 'bg-runs'"
          >{{ s }}</span
        >
        <span v-if="!inns.this_over.length" class="text-slate-300">No balls yet this over.</span>
      </div>
    </div>

    <!-- Current players -->
    <div v-if="inns?.striker" class="bg-card rounded-xl shadow-sm p-4 space-y-2">
      <div class="flex justify-between">
        <span class="font-semibold">★ {{ inns.striker.name }}</span>
        <span class="text-slate-500">{{ inns.striker.runs }} ({{ inns.striker.balls }})</span>
      </div>
      <div v-if="inns.non_striker" class="flex justify-between">
        <span>{{ inns.non_striker.name }}</span>
        <span class="text-slate-500">{{ inns.non_striker.runs }} ({{ inns.non_striker.balls }})</span>
      </div>
      <div v-if="inns.bowler" class="flex justify-between border-t pt-2 text-sm text-slate-500">
        <span>{{ inns.bowler.name }}</span>
        <span>{{ inns.bowler.overs }}–{{ inns.bowler.runs_conceded }}–{{ inns.bowler.wickets }}</span>
      </div>
    </div>
  </div>
  <p v-else class="text-slate-400 pt-10 text-center">Connecting to live match…</p>
</template>
