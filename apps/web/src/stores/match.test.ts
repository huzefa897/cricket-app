import { beforeEach, describe, expect, it, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMatchStore } from './match'
import { api } from '../api/client'
import type { LiveState, MatchDetail } from '../types'

vi.mock('../api/client', () => ({
  api: {
    getMatch: vi.fn(),
    getLive: vi.fn(),
    setOpeners: vi.fn(),
    recordBall: vi.fn(),
    transitionInnings: vi.fn(),
    finishMatch: vi.fn(),
  },
}))

const mockedApi = vi.mocked(api)

function liveFixture(overrides: Partial<LiveState['innings'] & object> = {}): LiveState {
  return {
    match_id: 1,
    status: 'LIVE',
    total_overs: 2,
    innings: {
      innings_number: 1,
      batting_team: 'Alpha',
      bowling_team: 'Bravo',
      total_runs: 0,
      total_wickets: 0,
      overs: '0.0',
      legal_balls_bowled: 0,
      is_completed: false,
      crr: 0,
      rrr: null,
      target: null,
      striker: { id: 1, name: 'A1', runs: 0, balls: 0 },
      non_striker: { id: 2, name: 'A2', runs: 0, balls: 0 },
      bowler: { id: 5, name: 'B1', overs: '0.0', runs_conceded: 0, wickets: 0 },
      this_over: [],
      dismissed_player_ids: [],
      ...overrides,
    },
  }
}

const detailFixture: MatchDetail = {
  id: 1,
  team_one: {
    id: 1,
    name: 'Alpha',
    short_code: '',
    players: [
      { id: 1, name: 'A1', is_wicket_keeper: false, is_captain: false },
      { id: 2, name: 'A2', is_wicket_keeper: false, is_captain: false },
      { id: 3, name: 'A3', is_wicket_keeper: false, is_captain: false },
      { id: 4, name: 'A4', is_wicket_keeper: false, is_captain: false },
    ],
  },
  team_two: {
    id: 2,
    name: 'Bravo',
    short_code: '',
    players: [{ id: 5, name: 'B1', is_wicket_keeper: false, is_captain: false }],
  },
  toss_winner: 'Alpha',
  toss_decision: 'BAT',
  status: 'LIVE',
  created_at: '',
  innings: [],
}

describe('match store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('open() loads detail + live and fills state', async () => {
    mockedApi.getMatch.mockResolvedValue(detailFixture)
    mockedApi.getLive.mockResolvedValue(liveFixture())
    const store = useMatchStore()
    await store.open(1, { poll: false })
    expect(store.detail).toEqual(detailFixture)
    expect(store.innings?.batting_team).toBe('Alpha')
  })

  it('battingPlayers/bowlingPlayers resolve from the batting team name', async () => {
    mockedApi.getMatch.mockResolvedValue(detailFixture)
    mockedApi.getLive.mockResolvedValue(liveFixture())
    const store = useMatchStore()
    await store.open(1, { poll: false })
    expect(store.battingPlayers.map((p) => p.name)).toEqual(['A1', 'A2', 'A3', 'A4'])
    expect(store.bowlingPlayers.map((p) => p.name)).toEqual(['B1'])
  })

  it('availableBatsmen excludes on-field and dismissed players', async () => {
    mockedApi.getMatch.mockResolvedValue(detailFixture)
    mockedApi.getLive.mockResolvedValue(liveFixture({ dismissed_player_ids: [3] }))
    const store = useMatchStore()
    await store.open(1, { poll: false })
    // A1 (striker), A2 (non-striker) on field; A3 dismissed => only A4 available.
    expect(store.availableBatsmen.map((p) => p.name)).toEqual(['A4'])
  })

  it('recordBall sends the payload and updates live state', async () => {
    mockedApi.getMatch.mockResolvedValue(detailFixture)
    mockedApi.getLive.mockResolvedValue(liveFixture())
    mockedApi.recordBall.mockResolvedValue(liveFixture({ total_runs: 4, this_over: ['4'] }))
    const store = useMatchStore()
    await store.open(1, { poll: false })
    await store.recordBall({ runs_scored_bat: 4 })
    expect(mockedApi.recordBall).toHaveBeenCalledWith(1, { runs_scored_bat: 4 })
    expect(store.innings?.total_runs).toBe(4)
  })

  it('finish() marks the match completed', async () => {
    mockedApi.getMatch.mockResolvedValue(detailFixture)
    mockedApi.getLive.mockResolvedValue(liveFixture())
    mockedApi.finishMatch.mockResolvedValue({ ...liveFixture(), status: 'COMPLETED' })
    const store = useMatchStore()
    await store.open(1, { poll: false })
    await store.finish()
    expect(store.isCompleted).toBe(true)
  })

  it('isLastWicket is true when only two batters remain', async () => {
    mockedApi.getMatch.mockResolvedValue(detailFixture)
    // 4 batters, 2 already out => next wicket is the last.
    mockedApi.getLive.mockResolvedValue(liveFixture({ total_wickets: 2 }))
    const store = useMatchStore()
    await store.open(1, { poll: false })
    expect(store.isLastWicket).toBe(true)
  })
})
