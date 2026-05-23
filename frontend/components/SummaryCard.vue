<template>
  <UCard>
    <div class="flex items-center">
      <div class="flex-shrink-0">
        <UIcon :name="icon" :class="['h-6 w-6 sm:h-8 sm:w-8', iconColor]" />
      </div>
      <div class="ml-4 flex-1">
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ label }}</p>
        <div class="flex flex-wrap items-baseline gap-2">
          <CurrencyAmount :amount="amount" compact class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white" />
          <UTooltip v-if="futureAmount !== undefined && futureAmount !== 0" :text="tooltipText">
            <p :class="['text-sm cursor-help', futureAmountClass]">
              (<CurrencyAmount :amount="amount + futureAmount" compact />)
            </p>
          </UTooltip>
        </div>
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
defineProps<{
  icon: string;
  iconColor: string;
  label: string;
  amount: number;
  futureAmount?: number;
  tooltipText?: string;
  futureAmountClass?: string;
}>();
</script>
