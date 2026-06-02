<script setup lang="ts">
/**
 * MonthNavigation — reusable month picker component.
 *
 * Emits `update:modelValue` with `{ year, month }` on prev/next click.
 * When `disableFuture` is true (default), the "next" button is disabled
 * while the user is on the current calendar month.
 */

interface MonthValue {
  year: number
  month: number // 1-12
}

const props = withDefaults(defineProps<{
  modelValue: MonthValue
  disableFuture?: boolean
}>(), {
  disableFuture: true,
})

const emit = defineEmits<{
  'update:modelValue': [value: MonthValue]
}>()

/** Human-readable label, e.g. "Juin 2025", capitalised. */
const label = computed(() => {
  const raw = new Date(props.modelValue.year, props.modelValue.month - 1)
    .toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
  return raw.charAt(0).toUpperCase() + raw.slice(1)
})

/** True when the displayed month is the current calendar month. */
const isAtCurrentMonth = computed(() => {
  const now = new Date()
  return props.modelValue.year === now.getFullYear() &&
    props.modelValue.month === now.getMonth() + 1
})

/** Navigate one month back, wrapping December → January with year decrement. */
const prev = () => {
  const { year, month } = props.modelValue
  if (month === 1) {
    emit('update:modelValue', { year: year - 1, month: 12 })
  } else {
    emit('update:modelValue', { year, month: month - 1 })
  }
}

/** Navigate one month forward, wrapping December → January with year increment.
 *  Guarded by `disableFuture` when already on the current month. */
const next = () => {
  if (props.disableFuture && isAtCurrentMonth.value) return
  const { year, month } = props.modelValue
  if (month === 12) {
    emit('update:modelValue', { year: year + 1, month: 1 })
  } else {
    emit('update:modelValue', { year, month: month + 1 })
  }
}
</script>

<template>
  <div class="month-nav">
    <button class="ds-btn-icon" aria-label="Mois précédent" @click="prev">
      <UIcon name="i-heroicons-chevron-left" style="width:15px;height:15px;" />
    </button>
    <span class="month-nav-label">{{ label }}</span>
    <button
      class="ds-btn-icon"
      aria-label="Mois suivant"
      :disabled="disableFuture && isAtCurrentMonth"
      @click="next"
    >
      <UIcon name="i-heroicons-chevron-right" style="width:15px;height:15px;" />
    </button>
  </div>
</template>

<style scoped>
.month-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}
.month-nav-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
  min-width: 130px;
  text-align: center;
  padding: 0 8px;
  text-transform: capitalize;
}
@media (min-width: 640px) {
  .month-nav-label {
    font-size: 14px;
    min-width: 150px;
  }
}
</style>
