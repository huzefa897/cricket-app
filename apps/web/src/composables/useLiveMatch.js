import { onUnmounted, ref } from 'vue'
import { api } from '../api/client'

// Polls GET /live on an interval (Phase 1 has no WebSockets — see docs/NETWORK.md).
// Returns reactive state plus a manual refresh() the scorer can call after an action.
export function useLiveMatch(matchId, { intervalMs = 3000 } = {}) {
  const live = ref(null)
  const error = ref(null)
  let timer = null

  async function refresh() {
    try {
      live.value = await api.getLive(matchId)
      error.value = null
    } catch (e) {
      error.value = e.message
    }
  }

  function start() {
    refresh()
    timer = setInterval(refresh, intervalMs)
  }

  function stop() {
    if (timer) clearInterval(timer)
    timer = null
  }

  onUnmounted(stop)

  return { live, error, refresh, start, stop }
}
