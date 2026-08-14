import type { LiveState, LiveInnings } from '../types'
import type { ExtrasKind } from '../components/ExtrasModal.vue'

// The contract every dashboard design implements. The container
// (ScorerDashboard.vue) owns all state, modals and networking; a design is
// purely presentational — it renders these props and emits these actions.
export interface DashboardDesignProps {
  live: LiveState
  innings: LiveInnings | null
  busy: boolean
  needsBowler: boolean
  matchCompleted: boolean
}

export interface DashboardDesignEmits {
  runs: [n: number]
  extras: [kind: ExtrasKind]
  wicket: []
  finish: []
  scorecard: []
}
