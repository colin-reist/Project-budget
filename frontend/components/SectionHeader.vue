<script setup lang="ts">
/**
 * SectionHeader — card section header with an optional "Voir tout" link.
 *
 * When `link` is provided a NuxtLink is rendered on the right side.
 * `linkLabel` defaults to 'Voir tout' if omitted.
 */
defineProps<{
  title: string
  subtitle?: string
  link?: string
  linkLabel?: string
}>()
</script>

<template>
  <div class="section-header">
    <div>
      <div class="section-title">{{ title }}</div>
      <div v-if="subtitle" class="section-sub">{{ subtitle }}</div>
    </div>
    <NuxtLink v-if="link" :to="link" class="section-link">
      {{ linkLabel ?? 'Voir tout' }}
      <UIcon name="i-heroicons-chevron-right" style="width:12px;height:12px;" />
    </NuxtLink>
  </div>
</template>

<style scoped>
.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.2px;
}
.section-sub {
  font-size: 12px;
  color: var(--ink-3);
  margin-top: 2px;
}
.section-link {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 13px;
  color: var(--accent);
  font-weight: 500;
  flex-shrink: 0;
  margin-top: 2px;
  text-decoration: none;
}
.section-link:hover {
  text-decoration: underline;
}
</style>
