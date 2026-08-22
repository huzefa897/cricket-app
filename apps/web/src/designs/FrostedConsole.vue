<script setup lang="ts">
import { computed } from 'vue'
import LiveBadge from '../components/LiveBadge.vue'
import type { DashboardDesignProps, DashboardDesignEmits } from './contract'

// The "Frosted" scoring console: glass read-panels + solid colour tap-pad.
// Responsive — one column on phones, read-panels beside the pad on laptops.
const props = defineProps<DashboardDesignProps>()
const emit = defineEmits<DashboardDesignEmits>()

const inns = computed(() => props.innings)
const totalOvers = computed(() => props.live.total_overs ?? 0)
const scoring = computed(
  () => !!inns.value && !!inns.value.striker && !inns.value.is_completed && !props.needsBowler,
)

// "Need N runs from M balls" for a chase.
const chase = computed(() => {
  const i = inns.value
  if (!i || i.target == null || i.is_completed) return null
  const runs = Math.max(i.target - i.total_runs, 0)
  const balls = Math.max(totalOvers.value * 6 - i.legal_balls_bowled, 0)
  return { runs, balls }
})

function fig(): string {
  const b = inns.value?.bowler
  return b ? `${b.overs}–${b.runs_conceded}–${b.wickets}` : '0.0–0–0'
}

// Preview chip for the Undo button: the last delivery, colour-coded to match
// the scoring palette. Derived from the backend `last_ball` symbol so it stays
// correct across over boundaries (unlike this_over, which resets each over).
const lastBall = computed<{ label: string; cls: string } | null>(() => {
  const s = inns.value?.last_ball
  if (!s) return null
  if (s === 'W') return { label: 'W', cls: 'bg-wicket' }
  if (s.endsWith('wd')) return { label: 'WD', cls: 'bg-wide' }
  if (s.endsWith('nb')) return { label: 'NB', cls: 'bg-noball' }
  if (s.endsWith('lb')) return { label: 'LB', cls: 'bg-bye' }
  if (s.endsWith('b')) return { label: 'B', cls: 'bg-bye' }
  const n = Number(s)
  if (n === 4 || n === 6) return { label: s, cls: 'bg-boundary' }
  return { label: s === '0' ? '•' : s, cls: 'bg-runs' }
})
</script>

<template>
  <div class="grid gap-3 lg:grid-cols-2 lg:gap-4 lg:items-start">
    <!-- READ PANELS -->
    <div class="space-y-3 lg:space-y-4">
      <!-- Summary -->
      <div class="glass p-5">
        <div class="flex items-center justify-between">
          <span class="text-sm font-semibold text-white/85">{{
            inns ? `${inns.batting_team} batting` : 'Match'
          }}</span>
          <LiveBadge :label="live.status" />
        </div>

        <div class="flex items-baseline gap-3 mt-2 mb-2">
          <span class="font-mono text-5xl font-semibold tracking-tight num text-white">
            {{ inns ? `${inns.total_runs}/${inns.total_wickets}` : '—' }}
          </span>
          <span class="font-mono text-sm text-white/70 num">
            {{ inns?.overs ?? '0.0' }} / {{ totalOvers }} ov
          </span>
        </div>

        <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-white/80">
          <span
            >CRR <b class="font-mono text-white">{{ inns?.crr ?? 0 }}</b></span
          >
          <span v-if="inns?.rrr != null"
            >RRR <b class="font-mono text-white">{{ inns.rrr }}</b></span
          >
          <span v-if="inns?.target != null">
            Target <b class="font-mono text-white">{{ inns.target }}</b>
          </span>
        </div>

        <p v-if="chase" class="mt-2.5 text-sm font-bold text-amber-300">
          Need {{ chase.runs }} runs from {{ chase.balls }} balls
        </p>
      </div>

      <!-- Players -->
      <div v-if="inns && inns.striker" class="glass p-4">
        <div class="flex gap-3">
          <div class="flex-1 min-w-0">
            <p class="text-[10px] uppercase tracking-wide text-white/55">Striker</p>
            <p class="text-sm font-semibold text-white mt-1 flex items-center gap-1.5 truncate">
              <span class="text-emerald-300 text-xs">★</span>{{ inns.striker.name }}
            </p>
            <p class="font-mono text-xs text-white/70 mt-0.5 num">
              {{ inns.striker.runs }} ({{ inns.striker.balls }})
            </p>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-[10px] uppercase tracking-wide text-white/55">Non-striker</p>
            <p class="text-sm font-semibold text-white mt-1 truncate">
              {{ inns.non_striker?.name ?? '—' }}
            </p>
            <p class="font-mono text-xs text-white/70 mt-0.5 num">
              {{ inns.non_striker?.runs ?? 0 }} ({{ inns.non_striker?.balls ?? 0 }})
            </p>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-[10px] uppercase tracking-wide text-white/55">Bowler</p>
            <p class="text-sm font-semibold text-white mt-1 truncate">
              {{ inns.bowler?.name ?? '—' }}
            </p>
            <p class="font-mono text-xs text-white/70 mt-0.5 num">{{ fig() }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2 mt-3 pt-3 border-t border-white/15 flex-wrap">
          <span class="text-[10px] uppercase tracking-wide text-white/55">This over</span>
          <span
            v-for="(s, i) in inns.this_over"
            :key="i"
            class="text-xs font-bold rounded px-1.5 py-0.5 text-white num"
            style="background: rgba(255, 255, 255, 0.14)"
            >{{ s }}</span
          >
          <span v-if="!inns.this_over.length" class="text-xs text-white/45">— new over —</span>

          <!-- Undo: neutral glass so it reads as a correction, not a scoring
               or destructive action. The chip previews the ball that vanishes. -->
          <button
            class="ml-auto inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-bold text-white border border-white/30 bg-white/10 backdrop-blur transition active:scale-95 enabled:hover:bg-white/20 disabled:opacity-40 disabled:cursor-not-allowed disabled:border-white/10"
            :disabled="noUndo || busy"
            @click="emit('undo')"
          >
            <svg
              viewBox="0 0 24 24"
              width="17"
              height="17"
              fill="none"
              stroke="currentColor"
              stroke-width="2.2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M9 6 4 11l5 5" />
              <path d="M4 11h11a5 5 0 0 1 5 5v1" />
            </svg>
            <span class="text-left leading-none">
              Undo
              <span class="block text-[10px] font-semibold text-white/50 mt-0.5">
                {{ noUndo ? '—' : 'last ball' }}
              </span>
            </span>
            <span
              v-if="lastBall && !noUndo"
              class="min-w-[26px] h-[26px] px-1.5 rounded-md grid place-items-center font-mono text-xs font-bold text-white num"
              :class="lastBall.cls"
              >{{ lastBall.label }}</span
            >
          </button>
        </div>
      </div>
    </div>

    <!-- TAP PAD -->
    <div>
      <!-- Match completed -->
      <div v-if="matchCompleted" class="glass p-6 text-center space-y-3">
        <p class="text-xl font-bold text-white">🏆 Match Completed</p>
        <button class="btn-bound w-full py-4 text-base" @click="emit('scorecard')">
          View Final Scorecard
        </button>
      </div>

      <!-- Scoring pad -->
      <div v-else-if="scoring" class="space-y-2.5">
        <div class="grid grid-cols-4 gap-2.5">
          <button
            v-for="n in [0, 1, 2, 3]"
            :key="n"
            class="btn-run text-2xl h-16 grid place-items-center leading-none"
            :disabled="busy"
            @click="emit('runs', n)"
          >
            {{ n }}
            <small v-if="n === 0" class="block text-[9px] font-semibold opacity-60 mt-0.5"
              >DOT</small
            >
          </button>
        </div>
        <div class="grid grid-cols-2 gap-2.5">
          <button
            v-for="n in [4, 6]"
            :key="n"
            class="btn-bound text-2xl h-16 grid place-items-center leading-none"
            :disabled="busy"
            @click="emit('runs', n)"
          >
            {{ n }}
            <small class="block text-[9px] font-semibold opacity-60 mt-0.5">BOUNDARY</small>
          </button>
        </div>
        <div class="grid grid-cols-3 gap-2.5">
          <button class="btn-extra h-14 text-sm" @click="emit('extras', 'WIDE')">Wide</button>
          <button class="btn-extra h-14 text-sm" @click="emit('extras', 'NO_BALL')">No Ball</button>
          <button class="btn-extra h-14 text-sm" @click="emit('extras', 'BYE_LEGBYE')">
            Bye / LB
          </button>
        </div>
        <button class="btn-wkt w-full h-14 text-lg" @click="emit('wicket')">Wicket!</button>
        <button
          class="w-full mt-1 py-3 rounded-2xl text-sm font-semibold text-rose-200 active:scale-[0.99]"
          style="border: 1.5px solid rgba(224, 80, 63, 0.6)"
          @click="emit('finish')"
        >
          Finish Match
        </button>
      </div>
    </div>
  </div>
</template>
