<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'

const router = useRouter()
const matches = ref([])
const loading = ref(true)

onMounted(async () => {
  matches.value = await api.listMatches()
  loading.value = false
})

const STATUS_STYLE = {
  LIVE: 'bg-boundary text-white',
  COMPLETED: 'bg-system text-white',
  UPCOMING: 'bg-slate-200 text-slate-600',
}

function open(m) {
  // Live matches go to the scorer's live viewer; completed go there too (scorecard).
  router.push(`/match/${m.id}/live`)
}
</script>

<template>
  <div class="space-y-3">
    <h2 class="text-xl font-bold text-slate-700">Match History</h2>

    <p v-if="loading" class="text-slate-400">Loading…</p>
    <p v-else-if="!matches.length" class="text-slate-400">
      No matches yet. Start one from “New Match”.
    </p>

    <button
      v-for="m in matches"
      :key="m.id"
      class="w-full text-left bg-card rounded-xl shadow-sm p-4 active:scale-[0.99] transition-transform"
      @click="open(m)"
    >
      <div class="flex items-center justify-between">
        <span class="font-semibold text-slate-700">{{ m.team_one }} vs {{ m.team_two }}</span>
        <span class="text-xs font-bold px-2 py-1 rounded-full" :class="STATUS_STYLE[m.status]">
          {{ m.status }}
        </span>
      </div>
      <p class="text-sm text-slate-400 mt-1">
        {{ m.total_overs }} overs · {{ new Date(m.created_at).toLocaleString() }}
      </p>
    </button>
  </div>
</template>
