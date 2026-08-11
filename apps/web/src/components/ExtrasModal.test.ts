import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import ExtrasModal from './ExtrasModal.vue'
import type { ExtrasKind } from './ExtrasModal.vue'

function mountModal(kind: ExtrasKind) {
  return mount(ExtrasModal, { props: { kind } })
}

async function clickRun(wrapper: ReturnType<typeof mountModal>, n: number) {
  await wrapper
    .findAll('button')
    .find((b) => b.text() === String(n))!
    .trigger('click')
}
async function send(wrapper: ReturnType<typeof mountModal>) {
  await wrapper
    .findAll('button')
    .find((b) => b.text() === 'Send')!
    .trigger('click')
}

describe('ExtrasModal', () => {
  it('wide includes the 1-run penalty plus scampered runs', async () => {
    const wrapper = mountModal('WIDE')
    await clickRun(wrapper, 2) // 2 scampered
    await send(wrapper)
    expect(wrapper.emitted('confirm')![0][0]).toEqual({ extra_type: 'WIDE', extra_runs: 3 })
  })

  it('no-ball carries runs off the bat + penalty', async () => {
    const wrapper = mountModal('NO_BALL')
    await clickRun(wrapper, 4)
    await send(wrapper)
    expect(wrapper.emitted('confirm')![0][0]).toEqual({
      extra_type: 'NO_BALL',
      extra_runs: 1,
      runs_scored_bat: 4,
    })
  })

  it('bye defaults to at least 1 run and BYE type', async () => {
    const wrapper = mountModal('BYE_LEGBYE')
    await send(wrapper) // no runs selected -> min 1
    expect(wrapper.emitted('confirm')![0][0]).toEqual({ extra_type: 'BYE', extra_runs: 1 })
  })
})
