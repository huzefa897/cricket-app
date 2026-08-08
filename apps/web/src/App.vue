<script setup>
// App shell: a slim sticky header + the routed view. Individual screens own their
// own layout (see docs/UI_PLAN.md).
</script>

<template>
  <div class="min-h-full">
    <header class="bg-system text-white sticky top-0 z-10 shadow-sm">
      <div class="max-w-2xl mx-auto px-4 py-3 flex items-center gap-2">
        <RouterLink to="/" class="text-lg font-bold">🏏 Howzatt</RouterLink>
        <nav class="ml-auto flex gap-4 text-sm">
          <RouterLink to="/setup" class="hover:underline">New Match</RouterLink>
          <RouterLink to="/history" class="hover:underline">History</RouterLink>
        </nav>
      </div>
    </header>

    <main class="max-w-2xl mx-auto px-4 py-4">
      <RouterView />
    </main>
  </div>
</template>
