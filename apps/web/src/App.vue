<script setup lang="ts">
import { watchEffect } from 'vue'
import { usePreferencesStore } from './stores/preferences'

// App shell: a slim sticky header + the routed view. The chosen theme is
// reflected onto <html data-theme> so global CSS (see style.css) can reskin the
// whole app. Individual screens own their own layout (see docs/UI_PLAN.md).
const prefs = usePreferencesStore()
watchEffect(() => {
  document.documentElement.dataset.theme = prefs.theme
})
</script>

<template>
  <div class="min-h-full">
    <header class="app-header bg-system text-white sticky top-0 z-10 shadow-sm">
      <div class="max-w-5xl mx-auto px-4 py-3 flex items-center gap-2">
        <RouterLink to="/" class="text-lg font-bold">🏏 Howzatt</RouterLink>
        <nav class="ml-auto flex gap-4 text-sm">
          <RouterLink to="/setup" class="hover:underline">New Match</RouterLink>
          <RouterLink to="/history" class="hover:underline">History</RouterLink>
        </nav>
      </div>
    </header>

    <main class="max-w-2xl lg:max-w-5xl mx-auto px-4 py-4">
      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
  </div>
</template>
