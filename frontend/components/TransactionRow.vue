<template>
  <div class="tx-row">
    <div class="tx-icon" :style="{ background: iconBg, color: iconColor }">
      <UIcon :name="iconName" style="width:15px;height:15px;" />
    </div>
    <div class="tx-info">
      <p class="tx-desc">{{ transaction.description || '(sans description)' }}</p>
      <p class="tx-meta">
        {{ formattedDate }}
        <span v-if="transaction.category_name" class="tx-cat">· {{ transaction.category_name }}</span>
      </p>
    </div>
    <div class="tx-amount mono" :style="{ color: amountColor }">
      {{ prefix }}{{ formatCurrency(Math.abs(parseFloat(transaction.amount))) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Transaction } from '~/types';

const props = defineProps<{ transaction: Transaction }>();

const { currency } = useUserProfile();

const isIncome   = computed(() => props.transaction.type === 'income');
const isExpense  = computed(() => props.transaction.type === 'expense');

const iconBg = computed(() => {
  if (isIncome.value)  return 'color-mix(in oklab, var(--success) 12%, var(--surface))'
  if (isExpense.value) return 'color-mix(in oklab, var(--danger)  12%, var(--surface))'
  return 'color-mix(in oklab, var(--accent) 12%, var(--surface))'
})
const iconColor = computed(() => {
  if (isIncome.value)  return 'var(--success)'
  if (isExpense.value) return 'var(--danger)'
  return 'var(--accent)'
})
const iconName = computed(() => {
  if (isIncome.value)  return 'i-heroicons-arrow-down-circle'
  if (isExpense.value) return 'i-heroicons-arrow-up-circle'
  return 'i-heroicons-arrow-right-circle'
})
const amountColor = computed(() => {
  if (isIncome.value)  return 'var(--success)'
  if (isExpense.value) return 'var(--ink)'
  return 'var(--accent)'
})
const prefix = computed(() => isIncome.value ? '+' : isExpense.value ? '−' : '')

const formattedDate = computed(() =>
  new Date(props.transaction.date).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'short',
  })
)

const formatCurrency = (val: number) =>
  `${val.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency.value}`
</script>

<style scoped>
.tx-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 0;
  border-bottom: 1px solid var(--line);
}
.tx-row:last-child { border-bottom: none; }

.tx-icon {
  width: 34px; height: 34px; border-radius: 9px;
  display: grid; place-items: center; flex-shrink: 0;
}

.tx-info {
  flex: 1;
  min-width: 0;
}
.tx-desc {
  margin: 0;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tx-meta {
  margin: 2px 0 0;
  font-size: 11.5px;
  color: var(--ink-3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tx-cat { color: var(--ink-4); }

.tx-amount {
  font-size: 13.5px;
  font-weight: 500;
  flex-shrink: 0;
  white-space: nowrap;
}
</style>
