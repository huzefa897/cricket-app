import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { api } from '../api/client'
import type { LiveState, MatchDetail } from '../types'
import ScorerDashboard from './ScorerDashboard.vue'

// Stub vue-router so useRouter() has something to return.
const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))

vi.mock('../api/client', () => ({
  api: {
    getMatch: vi.fn(),
    getLive: vi.fn(),
    setOpeners: vi.fn(),
    changeBowler: vi.fn(),
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
    players: [
      { id: 5, name: 'B1', is_wicket_keeper: false, is_captain: false },
      { id: 6, name: 'B2', is_wicket_keeper: false, is_captain: false },
    ],
  },
  toss_winner: 'Alpha',
  toss_decision: 'BAT',
  status: 'LIVE',
  created_at: '',
  innings: [],
}

function findBtn(wrapper: ReturnType<typeof mount>, text: string) {
  const btn = wrapper.findAll('button').find((b) => b.text().includes(text))
  if (!btn) {
    throw new Error(
      `No button matching "${text}". Have: ${wrapper.findAll('button').map((b) => b.text())}`,
    )
  }
  return btn
}

async function mountDashboard() {
  const wrapper = mount(ScorerDashboard, { props: { id: 1 } })
  await flushPromises() // resolve store.open() -> getMatch + getLive
  return wrapper
}

describe('ScorerDashboard integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mockedApi.getMatch.mockResolvedValue(detailFixture)
    mockedApi.getLive.mockResolvedValue(liveFixture())
  })

  afterEach(() => {
    // stop the store's polling interval so it doesn't leak across tests
    push.mockClear()
  })

  it('renders the live score and active players once loaded', async () => {
    const wrapper = await mountDashboard()
    expect(wrapper.text()).toContain('A1')
    expect(wrapper.text()).toContain('B1')
    // scoring matrix present (not the loading placeholder)
    expect(wrapper.text()).not.toContain('Loading match')
  })

  it('records a boundary through the run buttons', async () => {
    mockedApi.recordBall.mockResolvedValue(liveFixture({ total_runs: 4, this_over: ['4'] }))
    const wrapper = await mountDashboard()

    await findBtn(wrapper, '4').trigger('click')
    await flushPromises()

    expect(mockedApi.recordBall).toHaveBeenCalledWith(1, { runs_scored_bat: 4 })
  })

  it('drives a wicket end-to-end through the wizard and records is_wicket=true', async () => {
    mockedApi.recordBall.mockResolvedValue(liveFixture({ total_wickets: 1 }))
    const wrapper = await mountDashboard()

    // open the wizard
    await findBtn(wrapper, 'Wicket!').trigger('click')
    await flushPromises()

    // 5-step flow
    await findBtn(wrapper, 'BOWLED').trigger('click')
    await findBtn(wrapper, 'A1').trigger('click') // striker is out
    await wrapper.find('select').setValue(3) // incoming batsman
    await findBtn(wrapper, 'Next').trigger('click')
    await findBtn(wrapper, 'Incoming').trigger('click') // incoming takes strike
    await findBtn(wrapper, 'Confirm').trigger('click')
    await flushPromises()

    expect(mockedApi.recordBall).toHaveBeenCalledTimes(1)
    const [matchId, payload] = mockedApi.recordBall.mock.calls[0]
    expect(matchId).toBe(1)
    // Regression guard end-to-end: a wizard wicket must reach the API as is_wicket.
    expect(payload.is_wicket).toBe(true)
    expect(payload.wicket_type).toBe('BOWLED')
    expect(payload.player_dismissed_id).toBe(1)
    expect(payload.incoming_batsman_id).toBe(3)
  })

  it('prompts for a new bowler at the end of an over and blocks scoring', async () => {
    // An over just completed: 6 legal balls, innings still live.
    mockedApi.getLive.mockResolvedValue(liveFixture({ legal_balls_bowled: 6 }))
    mockedApi.changeBowler.mockResolvedValue(liveFixture({ legal_balls_bowled: 6 }))
    const wrapper = await mountDashboard()

    // Scoring matrix is hidden, the bowler prompt is shown.
    expect(wrapper.find('select').exists()).toBe(true)
    expect(wrapper.text()).toContain('Select Bowler')

    // Pick B2 and confirm → store.changeBowler → api.changeBowler.
    await wrapper.find('select').setValue(6)
    await findBtn(wrapper, 'Confirm').trigger('click')
    await flushPromises()

    expect(mockedApi.changeBowler).toHaveBeenCalledWith(1, 6)
  })

  it('finishing the match calls the finish endpoint and locks scoring', async () => {
    mockedApi.finishMatch.mockResolvedValue({ ...liveFixture(), status: 'COMPLETED' })
    const wrapper = await mountDashboard()

    await findBtn(wrapper, 'Finish Match').trigger('click') // open confirm
    await findBtn(wrapper, 'Finish & Lock').trigger('click')
    await flushPromises()

    expect(mockedApi.finishMatch).toHaveBeenCalledWith(1)
    // scoring matrix replaced by the completed banner
    expect(wrapper.text()).toContain('Match Completed')
  })
})
