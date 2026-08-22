import { afterEach, describe, expect, it } from 'vitest'
import { DOMWrapper, flushPromises, mount } from '@vue/test-utils'
import ExtrasModal from './ExtrasModal.vue'
import type { ExtrasKind } from './ExtrasModal.vue'

async function mountModal(kind: ExtrasKind) {
  const wrapper = mount(ExtrasModal, { props: { kind } })
  await flushPromises() // let Reka teleport the dialog content into <body>
  return wrapper
}

// Reka's Dialog teleports its content to <body>; query there, not on `wrapper`.
function bodyBtn(text: string) {
  const el = [...document.body.querySelectorAll('button')].find(
    (b) => b.textContent?.trim() === text,
  )!
  return new DOMWrapper(el)
}
async function clickRun(n: number) {
  await bodyBtn(String(n)).trigger('click')
}
async function send() {
  await bodyBtn('Send').trigger('click')
}

describe('ExtrasModal', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('wide includes the 1-run penalty plus scampered runs', async () => {
    const wrapper = await mountModal('WIDE')
    await clickRun(2) // 2 scampered
    await send()
    expect(wrapper.emitted('confirm')![0][0]).toEqual({ extra_type: 'WIDE', extra_runs: 3 })
  })

  it('no-ball carries runs off the bat + penalty', async () => {
    const wrapper = await mountModal('NO_BALL')
    await clickRun(4)
    await send()
    expect(wrapper.emitted('confirm')![0][0]).toEqual({
      extra_type: 'NO_BALL',
      extra_runs: 1,
      runs_scored_bat: 4,
    })
  })

  it('bye defaults to at least 1 run and BYE type', async () => {
    const wrapper = await mountModal('BYE_LEGBYE')
    await send() // no runs selected -> min 1
    expect(wrapper.emitted('confirm')![0][0]).toEqual({ extra_type: 'BYE', extra_runs: 1 })
  })
})
