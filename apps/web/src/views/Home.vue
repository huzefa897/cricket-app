<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'
import LiveBadge from '../components/LiveBadge.vue'
import type { MatchListItem } from '../types'

const router = useRouter()

const matches = ref<MatchListItem[]>([])
const loaded = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

const liveMatches = computed(() => matches.value.filter((m) => m.status === 'LIVE'))

async function refresh() {
  try {
    matches.value = await api.listMatches()
  } catch {
    // Offline / backend down — keep whatever we last had, try again next tick.
  } finally {
    loaded.value = true
  }
}

onMounted(() => {
  refresh()
  timer = setInterval(refresh, 5000) // keep scores current on the home screen
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function summary(m: MatchListItem): string {
  const s = m.live_summary
  if (!s) return 'Warming up…'
  return `${s.batting_team} ${s.total_runs}/${s.total_wickets} (${s.overs})`
}
</script>

<template>
  <div class="space-y-4 pt-6">
    <div class="hero-glass bg-card rounded-xl shadow-sm p-6 text-center">
      <h1 class="text-2xl font-bold text-system">🏏 Howzatt</h1>
      <p class="text-slate-500 mt-1">Local-first cricket scoring for weekend matches.</p>
    </div>

    <!-- Live now -->
    <section v-if="liveMatches.length" class="space-y-2">
      <div class="flex items-center gap-2 px-1">
        <span class="relative flex h-2.5 w-2.5">
          <span
            class="pulse-dot absolute inline-flex h-full w-full rounded-full opacity-70 animate-ping"
          />
          <span class="pulse-dot relative inline-flex h-2.5 w-2.5 rounded-full" />
        </span>
        <h2 class="text-sm font-bold uppercase tracking-wide text-slate-500">Live now</h2>
      </div>

      <TransitionGroup name="list" tag="div" class="relative space-y-2">
        <button
          v-for="m in liveMatches"
          :key="m.id"
          class="list-card border border-boundary/20"
          @click="router.push(`/match/${m.id}/score`)"
        >
          <div class="min-w-0 flex-1 text-left">
            <span class="font-semibold text-slate-700 truncate block">
              {{ m.team_one }} vs {{ m.team_two }}
            </span>
            <p class="num text-sm text-slate-500 mt-1">{{ summary(m) }}</p>
            <p class="text-xs text-slate-400 mt-0.5">{{ m.total_overs }} overs</p>
          </div>
          <LiveBadge class="shrink-0" />
          <span class="chev">›</span>
        </button>
      </TransitionGroup>
    </section>

    <button class="btn-primary w-full py-5 text-lg" @click="router.push('/setup')">
      + Start a New Match
    </button>

    <button class="btn-secondary w-full py-5 text-lg" @click="router.push('/history')">
      View Match History
    </button>
  </div>
</template>
