<template>
  <UModal v-model="isOpen">
    <UCard>
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon
            :name="iconName"
            :class="['h-6 w-6', iconColorClass]"
          />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ title }}</h3>
        </div>
      </template>

      <p class="text-sm text-gray-600 dark:text-gray-400">{{ message }}</p>

      <div v-if="requireInput" class="mt-4">
        <UFormGroup :label="inputLabel">
          <UInput
            v-model="inputValue"
            :type="inputType"
            :placeholder="inputPlaceholder"
            @keyup.enter="handleConfirm"
          />
        </UFormGroup>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton
            color="gray"
            variant="soft"
            label="Annuler"
            @click="handleCancel"
          />
          <UButton
            :color="confirmColor"
            :label="confirmLabel"
            :disabled="requireInput && !inputValue"
            @click="handleConfirm"
          />
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  title?: string
  message?: string
  confirmLabel?: string
  confirmColor?: string
  icon?: string
  requireInput?: boolean
  inputLabel?: string
  inputType?: string
  inputPlaceholder?: string
  expectedInput?: string
}>(), {
  title: 'Confirmer',
  message: 'Êtes-vous sûr ?',
  confirmLabel: 'Confirmer',
  confirmColor: 'red',
  icon: 'i-heroicons-exclamation-triangle',
  requireInput: false,
  inputLabel: '',
  inputType: 'text',
  inputPlaceholder: '',
  expectedInput: '',
})

const emit = defineEmits<{
  confirm: [inputValue?: string]
  cancel: []
}>()

const isOpen = defineModel<boolean>({ default: false })
const inputValue = ref('')

const iconName = computed(() => props.icon)
const iconColorClass = computed(() => {
  const map: Record<string, string> = {
    red: 'text-red-500',
    orange: 'text-orange-500',
    primary: 'text-primary-500',
    green: 'text-green-500',
  }
  return map[props.confirmColor] || 'text-red-500'
})

const handleConfirm = () => {
  if (props.requireInput && props.expectedInput && inputValue.value !== props.expectedInput) {
    return
  }
  emit('confirm', inputValue.value)
  isOpen.value = false
  inputValue.value = ''
}

const handleCancel = () => {
  emit('cancel')
  isOpen.value = false
  inputValue.value = ''
}
</script>
