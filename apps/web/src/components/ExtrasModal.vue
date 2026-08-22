<script setup lang="ts">
import { ref } from 'vue'
import {
  DialogRoot,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from 'reka-ui'
import type { BallPayload, ExtraType } from '../types'

export type ExtrasKind = 'WIDE' | 'NO_BALL' | 'BYE_LEGBYE'

// Captures the runs attached to an extra before sending the delivery.
//  - WIDE:  runs scampered beyond the 1-run penalty
//  - NO_BALL: runs scored off the bat (penalty added by backend intent)
//  - BYE_LEGBYE: runs run, plus bye vs leg-bye choice
const props = defineProps<{ kind: ExtrasKind }>()
const emit = defineEmits<{ confirm: [BallPayload]; cancel: [] }>()

const runs = ref(0)
const byeType = ref<ExtraType>('BYE')

const TITLES: Record<ExtrasKind, string> = {
  WIDE: 'Wide',
  NO_BALL: 'No Ball',
  BYE_LEGBYE: 'Bye / Leg Bye',
}
const byeOptions: [ExtraType, string][] = [
  ['BYE', 'Bye'],
  ['LEG_BYE', 'Leg Bye'],
]

function confirm() {
  if (props.kind === 'WIDE') {
    emit('confirm', { extra_type: 'WIDE', extra_runs: 1 + runs.value })
  } else if (props.kind === 'NO_BALL') {
    emit('confirm', { extra_type: 'NO_BALL', extra_runs: 1, runs_scored_bat: runs.value })
  } else {
    emit('confirm', { extra_type: byeType.value, extra_runs: Math.max(runs.value, 1) })
  }
}
</script>

<template>
  <DialogRoot :open="true" @update:open="(o) => !o && emit('cancel')">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-20 bg-black/40" />
      <DialogContent
        class="modal-card bg-card fixed z-20 inset-x-3 bottom-3 mx-auto w-auto max-w-md rounded-2xl p-5 shadow-lg space-y-4 sm:inset-x-auto sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:w-full sm:-translate-x-1/2 sm:-translate-y-1/2"
      >
        <DialogTitle class="text-lg font-bold text-slate-700">{{ TITLES[kind] }}</DialogTitle>
        <DialogDescription class="sr-only">
          Enter the runs attached to this extra, then send the delivery.
        </DialogDescription>

        <div v-if="kind === 'BYE_LEGBYE'" class="grid grid-cols-2 gap-2">
          <button
            v-for="t in byeOptions"
            :key="t[0]"
            class="py-2 rounded-lg font-semibold border"
            :class="byeType === t[0] ? 'bg-bye text-white border-bye' : 'bg-canvas text-slate-600'"
            @click="byeType = t[0]"
          >
            {{ t[1] }}
          </button>
        </div>

        <div>
          <p class="text-sm text-slate-500 mb-1">
            {{
              kind === 'WIDE'
                ? 'Extra runs run'
                : kind === 'NO_BALL'
                  ? 'Runs off the bat'
                  : 'Runs run'
            }}
          </p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="n in kind === 'NO_BALL' ? [0, 1, 2, 3, 4, 6] : [0, 1, 2, 3, 4]"
              :key="n"
              class="w-12 h-12 rounded-lg font-bold border"
              :class="
                runs === n ? 'bg-system text-white border-system' : 'bg-canvas text-slate-600'
              "
              @click="runs = n"
            >
              {{ n }}
            </button>
          </div>
        </div>

        <div class="flex gap-2">
          <button class="text-slate-400 flex-1 text-left" @click="emit('cancel')">Cancel</button>
          <button
            class="bg-system text-white px-6 py-3 rounded-xl font-bold active:scale-95"
            @click="confirm"
          >
            Send
          </button>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
