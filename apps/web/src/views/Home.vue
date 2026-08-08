<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="space-y-4 pt-6">
    <div class="bg-card rounded-xl shadow-sm p-6 text-center">
      <h1 class="text-2xl font-bold text-system">🏏 Howzatt</h1>
      <p class="text-slate-500 mt-1">Local-first cricket scoring for weekend matches.</p>
    </div>

    <button
      class="w-full bg-system text-white text-lg font-semibold rounded-xl py-5 shadow-sm active:scale-[0.99] transition-transform"
      @click="router.push('/setup')"
    >
      + Start a New Match
    </button>

    <button
      class="w-full bg-card text-system border border-system/20 text-lg font-semibold rounded-xl py-5 shadow-sm active:scale-[0.99] transition-transform"
      @click="router.push('/history')"
    >
      View Match History
    </button>
  </div>
</template>
