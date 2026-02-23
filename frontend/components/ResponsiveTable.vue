<template>
  <div>
    <!-- Mobile View: Cards -->
    <div class="block sm:hidden space-y-3">
      <UCard
        v-for="(row, index) in rows"
        :key="index"
        class="card-mobile"
      >
        <div class="space-y-2">
          <div
            v-for="(column, colIndex) in columns"
            :key="colIndex"
            class="flex justify-between items-start gap-4"
          >
            <span class="text-sm font-semibold text-gray-600 dark:text-gray-400 min-w-[100px]">
              {{ column.label }}
            </span>
            <div class="text-right flex-1">
              <slot
                :name="`cell-${column.key}`"
                :row="row"
                :value="row[column.key]"
              >
                <span class="text-base font-medium text-gray-900 dark:text-white">
                  {{ row[column.key] }}
                </span>
              </slot>
            </div>
          </div>

          <!-- Actions slot for mobile -->
          <div v-if="$slots.actions" class="pt-3 mt-3 border-t border-gray-200 dark:border-gray-700 flex gap-2">
            <slot name="actions" :row="row" />
          </div>
        </div>
      </UCard>

      <div v-if="rows.length === 0" class="text-center py-8 text-gray-500">
        <slot name="empty">
          {{ emptyMessage }}
        </slot>
      </div>
    </div>

    <!-- Desktop View: Table -->
    <div class="hidden sm:block overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700">
            <th
              v-for="column in columns"
              :key="column.key"
              class="text-left py-3 px-4 font-semibold text-gray-600 dark:text-gray-400"
              :class="column.class"
            >
              {{ column.label }}
            </th>
            <th v-if="$slots.actions" class="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in rows"
            :key="index"
            class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="py-3 px-4"
              :class="column.class"
            >
              <slot
                :name="`cell-${column.key}`"
                :row="row"
                :value="row[column.key]"
              >
                {{ row[column.key] }}
              </slot>
            </td>
            <td v-if="$slots.actions" class="py-3 px-4 text-right">
              <div class="flex justify-end gap-2">
                <slot name="actions" :row="row" />
              </div>
            </td>
          </tr>

          <tr v-if="rows.length === 0">
            <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="text-center py-8 text-gray-500">
              <slot name="empty">
                {{ emptyMessage }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center py-8">
      <UIcon name="i-heroicons-arrow-path" class="h-8 w-8 animate-spin text-primary-600" />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ResponsiveTable Component
 *
 * Automatically transforms table to cards on mobile for better UX.
 * On desktop, displays a traditional table.
 * On mobile (< 640px), displays cards with labels.
 *
 * @example
 * <ResponsiveTable
 *   :columns="[
 *     { key: 'name', label: 'Nom' },
 *     { key: 'amount', label: 'Montant', class: 'text-right' }
 *   ]"
 *   :rows="transactions"
 * >
 *   <template #cell-amount="{ value }">
 *     <CurrencyAmount :amount="value" />
 *   </template>
 *   <template #actions="{ row }">
 *     <UButton size="sm" @click="edit(row)">Modifier</UButton>
 *   </template>
 * </ResponsiveTable>
 */

interface Column {
  /** Unique key matching row property */
  key: string
  /** Display label for column header */
  label: string
  /** Optional CSS classes for the column */
  class?: string
}

interface Props {
  /** Array of column definitions */
  columns: Column[]
  /** Array of data rows */
  rows: any[]
  /** Loading state */
  loading?: boolean
  /** Empty state message */
  emptyMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  emptyMessage: 'Aucune donnée disponible'
})
</script>

<style scoped>
/* Additional mobile optimizations */
@media (max-width: 640px) {
  /* Ensure cards are easily tappable */
  :deep(.card-mobile) {
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  :deep(.card-mobile:active) {
    transform: scale(0.98);
  }
}
</style>
