<template>
  <UFormGroup
    :label="label"
    :required="required"
    :error="error"
    :help="help"
    :class="formGroupClass"
  >
    <UInput
      v-bind="$attrs"
      :model-value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :inputmode="inputmode || getInputMode()"
      :autocomplete="autocomplete"
      :class="inputClass"
      :size="size"
      @update:model-value="$emit('update:modelValue', $event)"
      @blur="$emit('blur', $event)"
      @focus="$emit('focus', $event)"
    >
      <template v-if="$slots.leading" #leading>
        <slot name="leading" />
      </template>
      <template v-if="$slots.trailing" #trailing>
        <slot name="trailing" />
      </template>
    </UInput>
  </UFormGroup>
</template>

<script setup lang="ts">
/**
 * MobileInput Component
 *
 * Input component optimized for mobile with:
 * - Proper touch target size (min 48px)
 * - Correct inputmode for mobile keyboards
 * - 16px font-size to prevent iOS zoom
 * - Better spacing and padding
 *
 * @example
 * <MobileInput
 *   v-model="email"
 *   label="Email"
 *   type="email"
 *   required
 * />
 */

interface Props {
  /** v-model value */
  modelValue?: string | number
  /** Input label */
  label: string
  /** Input type */
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'date' | 'time'
  /** Placeholder text */
  placeholder?: string
  /** Required field */
  required?: boolean
  /** Disabled state */
  disabled?: boolean
  /** Error message */
  error?: string
  /** Help text */
  help?: string
  /** Input mode for mobile keyboard */
  inputmode?: 'none' | 'text' | 'decimal' | 'numeric' | 'tel' | 'search' | 'email' | 'url'
  /** Autocomplete attribute */
  autocomplete?: string
  /** Input size */
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'lg' // Larger by default for mobile
})

defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
}>()

// Auto-detect inputmode based on type
const getInputMode = () => {
  switch (props.type) {
    case 'email':
      return 'email'
    case 'tel':
      return 'tel'
    case 'url':
      return 'url'
    case 'number':
      return 'decimal'
    default:
      return 'text'
  }
}

// Computed classes
const formGroupClass = computed(() => {
  return 'mobile-form-group'
})

const inputClass = computed(() => {
  const classes = ['min-h-[48px]']

  // Ensure 16px font-size on mobile to prevent iOS zoom
  if (process.client && window.innerWidth < 640) {
    classes.push('text-base')
  }

  return classes.join(' ')
})
</script>

<style scoped>
/* Additional mobile-specific styles */
.mobile-form-group :deep(label) {
  @apply text-base font-semibold mb-2;
}

.mobile-form-group :deep(input) {
  @apply text-base;
}

/* Prevent zoom on iOS */
@media (max-width: 640px) {
  .mobile-form-group :deep(input) {
    font-size: 16px !important;
  }
}
</style>
