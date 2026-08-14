<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import LiveBadge from '../components/LiveBadge.vue'
import type { MatchListItem } from '../types'

const router = useRouter()
const matches = ref<MatchListItem[]>([])
const loading = ref(true)

onMounted(async () => {
  matches.value = await api.listMatches()
  loading.value = false
})

// Non-live statuses use calm neutral pills; LIVE uses the shared LiveBadge.
const STATUS_STYLE: Record<'COMPLETED' | 'UPCOMING', string> = {
  COMPLETED: 'badge-done',
  UPCOMING: 'badge-upcoming',
}

function open(m: MatchListItem) {
  // Resume scoring for a live match; completed matches open the read-only scorecard.
  if (m.status === 'COMPLETED') router.push(`/match/${m.id}/live`)
  else router.push(`/match/${m.id}/score`)
}
</script>

<template>
  <div class="space-y-3">
    <h2 class="text-xl font-bold text-slate-700">Match History</h2>

    <p v-if="loading" class="text-slate-400">Loading…</p>
    <p v-else-if="!matches.length" class="text-slate-400">
      No matches yet. Start one from “New Match”.
    </p>

    <button v-for="m in matches" :key="m.id" class="list-card" @click="open(m)">
      <div class="min-w-0 flex-1 text-left">
        <span class="font-semibold text-slate-700 truncate block"
          >{{ m.team_one }} vs {{ m.team_two }}</span
        >
        <p class="text-sm text-slate-400 mt-1">
          {{ m.total_overs }} overs · {{ new Date(m.created_at).toLocaleString() }}
        </p>
      </div>
      <LiveBadge v-if="m.status === 'LIVE'" class="shrink-0" />
      <span v-else class="shrink-0" :class="STATUS_STYLE[m.status]">{{ m.status }}</span>
      <span class="chev">›</span>
    </button>
  </div>
</template>
