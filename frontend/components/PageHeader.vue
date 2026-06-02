<script setup lang="ts">
/**
 * PageHeader — page-level header shared across all app pages.
 *
 * Renders a title, an optional subtitle, and an `#actions` slot
 * for right-side buttons or controls (e.g. month nav + CTAs).
 */
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <div class="page-header">
    <div class="page-header-left">
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="page-header-right">
      <slot name="actions" />
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.page-header-left {
  flex: 1;
  min-width: 0;
}
.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.5px;
  color: var(--ink);
}
@media (min-width: 640px) {
  .page-title { font-size: 22px; }
}
.page-subtitle {
  margin: 2px 0 0;
  font-size: 13px;
  color: var(--ink-3);
}
.page-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
</style>
