<script setup lang="ts">
import { computed, onBeforeUnmount, watch } from 'vue'

export type ToastVariant = 'error' | 'success' | 'info' | 'warning'

// Floating notification that sits above every modal (z-50). Auto-dismisses,
// and can be closed. Card style: icon chip + title + description + close.
const props = withDefaults(
  defineProps<{
    message: string | null
    title?: string
    variant?: ToastVariant
    durationMs?: number
  }>(),
  { title: '', variant: 'error', durationMs: 3500 },
)
const emit = defineEmits<{ close: [] }>()

// Per-variant look (Tailwind default palette) + heading fallback + icon path.
const VARIANTS: Record<
  ToastVariant,
  { wrap: string; chip: string; heading: string; icon: string }
> = {
  error: {
    wrap: 'bg-rose-50 border-rose-100',
    chip: 'bg-rose-500',
    heading: 'Error',
    icon: 'M6 18 18 6M6 6l12 12',
  },
  success: {
    wrap: 'bg-emerald-50 border-emerald-100',
    chip: 'bg-emerald-500',
    heading: 'Success',
    icon: 'm4.5 12.75 6 6 9-13.5',
  },
  info: {
    wrap: 'bg-blue-50 border-blue-100',
    chip: 'bg-blue-500',
    heading: 'Heads up',
    icon: 'M11.25 11.25h.75v3.75m-.75 0h1.5M12 8.25h.008v.008H12V8.25Z',
  },
  warning: {
    wrap: 'bg-amber-50 border-amber-100',
    chip: 'bg-amber-500',
    heading: 'Attention',
    icon: 'M12 9v3.75m0 3.008h.008M10.05 3.878 1.98 17.626A1.5 1.5 0 0 0 3.28 19.5h17.44a1.5 1.5 0 0 0 1.3-2.25L13.95 3.878a1.5 1.5 0 0 0-2.6 0Z',
  },
}

const style = computed(() => VARIANTS[props.variant])
const heading = computed(() => props.title || style.value.heading)

let timer: ReturnType<typeof setTimeout> | null = null
function clear() {
  if (timer) clearTimeout(timer)
  timer = null
}

// Restart the auto-dismiss timer whenever a new message appears.
watch(
  () => props.message,
  (msg) => {
    clear()
    if (msg) timer = setTimeout(() => emit('close'), props.durationMs)
  },
  { immediate: true },
)

onBeforeUnmount(clear)
</script>

<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0 -translate-y-2"
    leave-active-class="transition duration-150 ease-in"
    leave-to-class="opacity-0 -translate-y-2"
  >
    <div
      v-if="message"
      class="fixed inset-x-0 top-3 z-50 flex justify-center px-3 pointer-events-none"
      role="alert"
      aria-live="assertive"
    >
      <div
        class="pointer-events-auto flex w-full max-w-md items-start gap-3 rounded-2xl border bg-card p-4 shadow-lg"
        :class="style.wrap"
      >
        <!-- Icon chip -->
        <span
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-white"
          :class="style.chip"
        >
          <svg
            class="h-5 w-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path :d="style.icon" />
          </svg>
        </span>

        <!-- Text -->
        <div class="min-w-0 flex-1 pt-0.5">
          <p class="text-sm font-bold text-slate-800">{{ heading }}</p>
          <p class="mt-0.5 text-sm text-slate-500 break-words">{{ message }}</p>
        </div>

        <!-- Close -->
        <button
          type="button"
          class="shrink-0 text-slate-400 active:scale-90"
          aria-label="Dismiss"
          @click="emit('close')"
        >
          <svg
            class="h-5 w-5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>
