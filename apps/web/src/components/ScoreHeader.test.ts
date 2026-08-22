import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ScoreHeader from './ScoreHeader.vue'
import type { LiveState } from '../types'

function live(overrides: Partial<NonNullable<LiveState['innings']>> = {}): LiveState {
  return {
    match_id: 1,
    status: 'LIVE',
    total_overs: 5,
    innings: {
      innings_number: 2,
      batting_team: 'Bravo',
      bowling_team: 'Alpha',
      total_runs: 40,
      total_wickets: 2,
      overs: '3.2',
      legal_balls_bowled: 20,
      is_completed: false,
      crr: 12,
      rrr: 8,
      target: 61,
      striker: null,
      non_striker: null,
      bowler: null,
      this_over: [],
      last_ball: null,
      dismissed_player_ids: [],
      ...overrides,
    },
  }
}

describe('ScoreHeader', () => {
  it('renders score, overs, CRR and target', () => {
    const wrapper = mount(ScoreHeader, { props: { live: live() } })
    const text = wrapper.text()
    expect(text).toContain('40/2')
    expect(text).toContain('3.2')
    expect(text).toContain('12') // CRR
    expect(text).toContain('61') // target
  })

  it('shows runs still needed when chasing', () => {
    const wrapper = mount(ScoreHeader, { props: { live: live({ total_runs: 50, target: 61 }) } })
    expect(wrapper.text()).toContain('Need 11 runs')
  })

  it('handles a match with no innings yet', () => {
    const wrapper = mount(ScoreHeader, {
      props: { live: { match_id: 1, status: 'LIVE', innings: null } },
    })
    expect(wrapper.text()).toContain('Waiting for the match')
  })
})
