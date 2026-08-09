import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import WicketModal from './WicketModal.vue'
import type { BatterStat, Player } from '../types'

const striker: BatterStat = { id: 1, name: 'A1', runs: 10, balls: 8 }
const nonStriker: BatterStat = { id: 2, name: 'A2', runs: 5, balls: 6 }
const available: Player[] = [{ id: 3, name: 'A3', is_wicket_keeper: false, is_captain: false }]

function mountModal(isLastWicket = false) {
  return mount(WicketModal, {
    props: { striker, nonStriker, availableBatsmen: available, isLastWicket },
  })
}

type Wrapper = ReturnType<typeof mountModal>

// Click the first button whose text contains `text` (avoids the header Cancel btn).
async function clickBtn(wrapper: Wrapper, text: string) {
  const btn = wrapper.findAll('button').find((b) => b.text().includes(text))
  if (!btn) throw new Error(`No button matching "${text}". Have: ${wrapper.findAll('button').map((b) => b.text())}`)
  await btn.trigger('click')
}

describe('WicketModal', () => {
  it('walks the 5-step flow and emits a payload with is_wicket=true', async () => {
    const wrapper = mountModal()
    await clickBtn(wrapper, 'BOWLED') // step 1: dismissal type
    await clickBtn(wrapper, 'A1') // step 2: striker is out
    await wrapper.find('select').setValue(3) // step 3: incoming
    await clickBtn(wrapper, 'Next')
    await clickBtn(wrapper, 'Incoming') // step 4: incoming takes strike
    await clickBtn(wrapper, 'Confirm') // step 5

    const events = wrapper.emitted('confirm')
    expect(events).toHaveLength(1)
    const payload = events![0][0] as Record<string, unknown>
    // Regression guard: a wicket recorded via the wizard MUST set is_wicket.
    expect(payload.is_wicket).toBe(true)
    expect(payload.wicket_type).toBe('BOWLED')
    expect(payload.player_dismissed_id).toBe(1)
    expect(payload.incoming_batsman_id).toBe(3)
    expect(payload.new_striker_id).toBe(3)
  })

  it('captures completed runs on a run-out', async () => {
    const wrapper = mountModal()
    await clickBtn(wrapper, 'RUN OUT') // step 1: run-out shows a runs picker in step 2
    await clickBtn(wrapper, '2') // runs completed before the dismissal
    await clickBtn(wrapper, 'A1') // striker is out
    await wrapper.find('select').setValue(3)
    await clickBtn(wrapper, 'Next')
    await clickBtn(wrapper, 'Incoming')
    await clickBtn(wrapper, 'Confirm')

    const payload = wrapper.emitted('confirm')![0][0] as Record<string, unknown>
    expect(payload.is_wicket).toBe(true)
    expect(payload.wicket_type).toBe('RUN_OUT')
    expect(payload.runs_scored_bat).toBe(2)
  })

  it('records zero bat runs for a non-run-out dismissal', async () => {
    const wrapper = mountModal(true)
    await clickBtn(wrapper, 'BOWLED')
    await clickBtn(wrapper, 'A1')
    await clickBtn(wrapper, 'Confirm')
    const payload = wrapper.emitted('confirm')![0][0] as Record<string, unknown>
    expect(payload.runs_scored_bat).toBe(0)
  })

  it('skips incoming-batsman steps on the last wicket', async () => {
    const wrapper = mountModal(true)
    await clickBtn(wrapper, 'BOWLED')
    await clickBtn(wrapper, 'A1') // who's out -> jumps straight to summary
    await clickBtn(wrapper, 'Confirm')
    const payload = wrapper.emitted('confirm')![0][0] as Record<string, unknown>
    expect(payload.is_wicket).toBe(true)
    expect(payload.incoming_batsman_id).toBeNull()
  })
})
