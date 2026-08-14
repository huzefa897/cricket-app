// Shared domain types mirroring the backend API (docs/SCHEMA.md).

export type MatchStatus = 'UPCOMING' | 'LIVE' | 'COMPLETED'
export type TossDecision = 'BAT' | 'BOWL'
export type ExtraType = 'NONE' | 'WIDE' | 'NO_BALL' | 'BYE' | 'LEG_BYE'
export type WicketType = 'NONE' | 'BOWLED' | 'CAUGHT' | 'RUN_OUT' | 'STUMPED' | 'LBW'

export interface Player {
  id: number
  name: string
  is_wicket_keeper: boolean
  is_captain: boolean
}

export interface Team {
  id: number
  name: string
  short_code: string
  players: Player[]
}

export interface LiveSummary {
  innings_number: number
  batting_team: string
  total_runs: number
  total_wickets: number
  overs: string
}

export interface MatchListItem {
  id: number
  team_one: string
  team_two: string
  total_overs: number
  status: MatchStatus
  created_at: string
  live_summary: LiveSummary | null
}

export interface InningsSummary {
  id: number
  innings_number: number
  batting_team: string
  bowling_team: string
  total_runs: number
  total_wickets: number
  overs: string
  crr: number
  is_completed: boolean
}

export interface MatchDetail {
  id: number
  team_one: Team
  team_two: Team
  toss_winner: string | null
  toss_decision: TossDecision
  status: MatchStatus
  created_at: string
  innings: InningsSummary[]
}

export interface BatterStat {
  id: number
  name: string
  runs: number
  balls: number
}

export interface BowlerStat {
  id: number
  name: string
  overs: string
  runs_conceded: number
  wickets: number
}

export interface LiveInnings {
  innings_number: number
  batting_team: string
  bowling_team: string
  total_runs: number
  total_wickets: number
  overs: string
  legal_balls_bowled: number
  is_completed: boolean
  crr: number
  rrr: number | null
  target: number | null
  striker: BatterStat | null
  non_striker: BatterStat | null
  bowler: BowlerStat | null
  this_over: string[]
  dismissed_player_ids: number[]
}

export interface LiveState {
  match_id: number
  status: MatchStatus
  total_overs?: number
  innings: LiveInnings | null
}

// --- Request payloads ---
export interface PlayerInput {
  name: string
  is_wicket_keeper?: boolean
  is_captain?: boolean
}

export interface CreateMatchPayload {
  team_one_name: string
  team_two_name: string
  team_one_short?: string
  team_two_short?: string
  team_one_players: PlayerInput[]
  team_two_players: PlayerInput[]
  total_overs: number
  toss_winner_index: 1 | 2
  toss_decision: TossDecision
}

export interface OpenersPayload {
  striker_id: number
  non_striker_id: number
  bowler_id: number
}

export interface BallPayload {
  runs_scored_bat?: number
  extra_type?: ExtraType
  extra_runs?: number
  is_wicket?: boolean
  wicket_type?: WicketType
  player_dismissed_id?: number | null
  incoming_batsman_id?: number | null
  new_striker_id?: number | null
}
