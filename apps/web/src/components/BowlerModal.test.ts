import { afterEach, describe, expect, it } from 'vitest'
import { DOMWrapper, flushPromises, mount } from '@vue/test-utils'
import BowlerModal from './BowlerModal.vue'
import type { Player } from '../types'

const bowlingPlayers: Player[] = [
  { id: 5, name: 'B1', is_wicket_keeper: false, is_captain: false },
  { id: 6, name: 'B2', is_wicket_keeper: false, is_captain: false },
]

async function mountModal() {
  const wrapper = mount(BowlerModal, { props: { bowlingPlayers } })
  await flushPromises() // let Reka teleport the dialog content into <body>
  return wrapper
}

// Reka's Dialog teleports its content to <body>; query there, not on `wrapper`.
function bodyBtn(text: string) {
  const el = [...document.body.querySelectorAll('button')].find((b) =>
    b.textContent?.includes(text),
  )!
  return new DOMWrapper(el)
}
function bodySelect() {
  return new DOMWrapper(document.body.querySelector('select')!)
}

describe('BowlerModal', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('is not ready until a bowler is picked, then emits the chosen id', async () => {
    const wrapper = await mountModal()
    const confirm = bodyBtn('Confirm')
    // Nothing selected yet → confirm disabled, no emit on click.
    expect(confirm.attributes('disabled')).toBeDefined()

    await bodySelect().setValue(6)
    expect(bodyBtn('Confirm').attributes('disabled')).toBeUndefined()

    await bodyBtn('Confirm').trigger('click')
    const events = wrapper.emitted('confirm')
    expect(events).toHaveLength(1)
    expect(events![0][0]).toEqual({ bowler_id: 6 })
  })
})
