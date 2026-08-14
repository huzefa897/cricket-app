<script setup lang="ts">
// Shared "LIVE" status pill used by the console, Home and History so the badge
// looks identical everywhere. Styled per-theme in style.css (.live-badge).
withDefaults(defineProps<{ label?: string }>(), { label: 'LIVE' })
</script>

<template>
  <span class="live-badge">
    <span class="live-dot" />
    {{ label }}
  </span>
</template>
