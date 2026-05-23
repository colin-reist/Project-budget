<template>
  <div class="flex items-center gap-3 py-2.5 border-b border-gray-200 dark:border-gray-700 last:border-0">
    <div :class="[
      'flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center',
      bgClass
    ]">
      <UIcon :name="iconName" :class="['h-4 w-4', textClass]" />
    </div>
    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ transaction.description }}</p>
      <p class="text-xs text-gray-500 dark:text-gray-400">{{ formattedDate }}</p>
    </div>
    <div :class="['text-sm font-semibold flex-shrink-0', textClass]">
      {{ prefix }}{{ formatCurrency(Math.abs(parseFloat(transaction.amount))) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Transaction } from '~/types';

const props = defineProps<{ transaction: Transaction }>();

const isIncome = computed(() => props.transaction.type === 'income');
const isExpense = computed(() => props.transaction.type === 'expense');

const bgClass = computed(() => isIncome.value
  ? 'bg-green-100 dark:bg-green-900/30'
  : isExpense.value
    ? 'bg-red-100 dark:bg-red-900/30'
    : 'bg-blue-100 dark:bg-blue-900/30'
);

const textClass = computed(() => isIncome.value
  ? 'text-green-600'
  : isExpense.value
    ? 'text-red-600'
    : 'text-blue-600'
);

const iconName = computed(() => isIncome.value
  ? 'i-heroicons-arrow-down-circle'
  : isExpense.value
    ? 'i-heroicons-arrow-up-circle'
    : 'i-heroicons-arrow-right-circle'
);

const prefix = computed(() => isIncome.value ? '+' : isExpense.value ? '-' : '');

const formattedDate = computed(() =>
  new Date(props.transaction.date).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'short', year: 'numeric',
  })
);
</script>
