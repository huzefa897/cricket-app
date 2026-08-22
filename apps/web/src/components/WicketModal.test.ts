import { afterEach, describe, expect, it } from 'vitest'
import { DOMWrapper, flushPromises, mount } from '@vue/test-utils'
import WicketModal from './WicketModal.vue'
import type { BatterStat, Player } from '../types'

const striker: BatterStat = { id: 1, name: 'A1', runs: 10, balls: 8 }
const nonStriker: BatterStat = { id: 2, name: 'A2', runs: 5, balls: 6 }
const available: Player[] = [{ id: 3, name: 'A3', is_wicket_keeper: false, is_captain: false }]

async function mountModal(isLastWicket = false) {
  const wrapper = mount(WicketModal, {
    props: { striker, nonStriker, availableBatsmen: available, isLastWicket },
  })
  await flushPromises() // let Reka teleport the dialog content into <body>
  return wrapper
}

// Reka's Dialog teleports its content to <body>; query there, not on `wrapper`.
// Click the first button whose text contains `text`.
async function clickBtn(text: string) {
  const btns = [...document.body.querySelectorAll('button')]
  const btn = btns.find((b) => b.textContent?.includes(text))
  if (!btn) throw new Error(`No button matching "${text}". Have: ${btns.map((b) => b.textContent)}`)
  await new DOMWrapper(btn).trigger('click')
}
async function setIncoming(id: number) {
  await new DOMWrapper(document.body.querySelector('select')!).setValue(id)
}

describe('WicketModal', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('walks the 5-step flow and emits a payload with is_wicket=true', async () => {
    const wrapper = await mountModal()
    await clickBtn('BOWLED') // step 1: dismissal type
    await clickBtn('A1') // step 2: striker is out
    await setIncoming(3) // step 3: incoming
    await clickBtn('Next')
    await clickBtn('Incoming') // step 4: incoming takes strike
    await clickBtn('Confirm') // step 5

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
    const wrapper = await mountModal()
    await clickBtn('RUN OUT') // step 1: run-out shows a runs picker in step 2
    await clickBtn('2') // runs completed before the dismissal
    await clickBtn('A1') // striker is out
    await setIncoming(3)
    await clickBtn('Next')
    await clickBtn('Incoming')
    await clickBtn('Confirm')

    const payload = wrapper.emitted('confirm')![0][0] as Record<string, unknown>
    expect(payload.is_wicket).toBe(true)
    expect(payload.wicket_type).toBe('RUN_OUT')
    expect(payload.runs_scored_bat).toBe(2)
  })

  it('keeps the surviving striker on strike when the non-striker is run out', async () => {
    const wrapper = await mountModal()
    await clickBtn('RUN OUT')
    await clickBtn('1') // runs completed
    await clickBtn('A2') // non-striker (id 2) is out
    await setIncoming(3) // incoming batsman
    await clickBtn('Next')
    // The "stays on strike" option must offer the surviving striker (A1), not the incoming.
    await clickBtn('stays on strike')
    await clickBtn('Confirm')

    const payload = wrapper.emitted('confirm')![0][0] as Record<string, unknown>
    expect(payload.player_dismissed_id).toBe(2)
    expect(payload.incoming_batsman_id).toBe(3)
    // Regression: the original striker (A1) must be able to keep strike.
    expect(payload.new_striker_id).toBe(1)
  })

  it('records zero bat runs for a non-run-out dismissal', async () => {
    const wrapper = await mountModal(true)
    await clickBtn('BOWLED')
    await clickBtn('A1')
    await clickBtn('Confirm')
    const payload = wrapper.emitted('confirm')![0][0] as Record<string, unknown>
    expect(payload.runs_scored_bat).toBe(0)
  })

  it('skips incoming-batsman steps on the last wicket', async () => {
    const wrapper = await mountModal(true)
    await clickBtn('BOWLED')
    await clickBtn('A1') // who's out -> jumps straight to summary
    await clickBtn('Confirm')
    const payload = wrapper.emitted('confirm')![0][0] as Record<string, unknown>
    expect(payload.is_wicket).toBe(true)
    expect(payload.incoming_batsman_id).toBeNull()
  })
})
