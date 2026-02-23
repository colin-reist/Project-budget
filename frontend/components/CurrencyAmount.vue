<template>
  <span :class="amountClass" :title="fullAmount">
    {{ displayAmount }}
  </span>
</template>

<script setup lang="ts">
/**
 * CurrencyAmount Component
 *
 * Responsive currency display component optimized for mobile.
 * Automatically uses compact notation (1K, 1M) on small screens for large amounts.
 *
 * @example
 * <CurrencyAmount :amount="1234.56" /> → "1 234,56 CHF"
 * <CurrencyAmount :amount="12345" compact /> → "12K CHF" (on mobile)
 * <CurrencyAmount :amount="1234567" compact /> → "1,2M CHF" (on mobile)
 */

interface Props {
  /** Amount to display */
  amount: number
  /** Currency code (CHF, EUR, USD, GBP). Uses user profile currency if not provided */
  currency?: string
  /** Enable compact notation on mobile for large amounts */
  compact?: boolean
  /** Force compact notation regardless of screen size */
  forceCompact?: boolean
  /** Additional CSS classes */
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  compact: false,
  forceCompact: false
})

// Use screen size composable for reactive mobile detection
const { isMobile } = useScreenSize()

// Display amount with appropriate formatting
const displayAmount = computed(() => {
  const useCompact = props.forceCompact || (props.compact && isMobile.value)
  return formatCurrency(props.amount, props.currency, {
    compact: useCompact,
    forceCompact: props.forceCompact
  })
})

// Full amount for tooltip (always full precision)
const fullAmount = computed(() => {
  return formatCurrency(props.amount, props.currency)
})

// Computed class with props.class
const amountClass = computed(() => {
  const classes = ['inline-block', 'font-medium', 'tabular-nums']
  if (props.class) {
    classes.push(props.class)
  }
  return classes.join(' ')
})
</script>

<style scoped>
/* Ensure amounts don't break layout on mobile */
span {
  overflow-wrap: break-word;
  word-break: keep-all;
}
</style>
