import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import BowlerModal from './BowlerModal.vue'
import type { Player } from '../types'

const bowlingPlayers: Player[] = [
  { id: 5, name: 'B1', is_wicket_keeper: false, is_captain: false },
  { id: 6, name: 'B2', is_wicket_keeper: false, is_captain: false },
]

function mountModal() {
  return mount(BowlerModal, { props: { bowlingPlayers } })
}

describe('BowlerModal', () => {
  it('is not ready until a bowler is picked, then emits the chosen id', async () => {
    const wrapper = mountModal()
    const confirm = wrapper.findAll('button').find((b) => b.text().includes('Confirm'))!
    // Nothing selected yet → confirm disabled, no emit on click.
    expect(confirm.attributes('disabled')).toBeDefined()

    await wrapper.find('select').setValue(6)
    expect(confirm.attributes('disabled')).toBeUndefined()

    await confirm.trigger('click')
    const events = wrapper.emitted('confirm')
    expect(events).toHaveLength(1)
    expect(events![0][0]).toEqual({ bowler_id: 6 })
  })
})
