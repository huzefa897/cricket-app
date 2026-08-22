import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '../api/client'
import type { BallPayload, LiveState, MatchDetail, OpenersPayload, Player } from '../types'

// Central store for the match currently being scored/viewed: live snapshot,
// rosters, polling, and every mutating action. Phase 1 uses polling for live
// updates (no WebSockets — see docs/NETWORK.md).
export const useMatchStore = defineStore('match', () => {
  const live = ref<LiveState | null>(null)
  const detail = ref<MatchDetail | null>(null)
  const error = ref<string | null>(null)

  let timer: ReturnType<typeof setInterval> | null = null
  let currentId: number | string | null = null

  // --- Getters ---
  const innings = computed(() => live.value?.innings ?? null)
  const isCompleted = computed(() => live.value?.status === 'COMPLETED')

  function playersOfTeam(name: string | undefined): Player[] {
    if (!detail.value || !name) return []
    for (const t of [detail.value.team_one, detail.value.team_two]) {
      if (t.name === name) return t.players
    }
    return []
  }
  const battingPlayers = computed(() => playersOfTeam(innings.value?.batting_team))
  const bowlingPlayers = computed(() => playersOfTeam(innings.value?.bowling_team))
  const dismissedIds = computed(() => new Set(innings.value?.dismissed_player_ids ?? []))

  // Batters eligible to come in: not on strike/non-strike and not already out.
  const availableBatsmen = computed(() =>
    battingPlayers.value.filter(
      (p) =>
        p.id !== innings.value?.striker?.id &&
        p.id !== innings.value?.non_striker?.id &&
        !dismissedIds.value.has(p.id),
    ),
  )

  // Next wicket is the last one when only two un-dismissed batters remain.
  const isLastWicket = computed(() => {
    const total = battingPlayers.value.length
    return total > 0 && !!innings.value && innings.value.total_wickets >= total - 2
  })

  // --- Actions ---
  async function refresh() {
    if (currentId == null) return
    try {
      live.value = await api.getLive(currentId)
      error.value = null
    } catch (e) {
      error.value = (e as Error).message
    }
  }

  function stopPolling() {
    if (timer) clearInterval(timer)
    timer = null
  }

  async function open(id: number | string, { poll = true, intervalMs = 3000 } = {}) {
    stopPolling()
    currentId = id
    live.value = null
    detail.value = await api.getMatch(id)
    await refresh()
    if (poll) timer = setInterval(refresh, intervalMs)
  }

  async function setOpeners(payload: OpenersPayload) {
    if (currentId == null) return
    live.value = await api.setOpeners(currentId, payload)
  }
  async function changeBowler(bowlerId: number) {
    if (currentId == null) return
    live.value = await api.changeBowler(currentId, bowlerId)
  }

  async function undoLastBall() {
    if (currentId == null) return
    live.value = await api.undoLastBall(currentId)
  }

  async function recordBall(payload: BallPayload) {
    if (currentId == null) return
    live.value = await api.recordBall(currentId, payload)
  }

  async function transition(payload: OpenersPayload) {
    if (currentId == null) return
    live.value = await api.transitionInnings(currentId, payload)
  }

  async function finish() {
    if (currentId == null) return
    live.value = await api.finishMatch(currentId)
  }

  function reset() {
    stopPolling()
    live.value = null
    detail.value = null
    error.value = null
    currentId = null
  }

  return {
    live,
    detail,
    error,
    innings,
    isCompleted,
    battingPlayers,
    bowlingPlayers,
    availableBatsmen,
    isLastWicket,
    changeBowler,
    undoLastBall,
    refresh,
    stopPolling,
    open,
    setOpeners,
    recordBall,
    transition,
    finish,
    reset,
  }
})
