<template>
  <UModal
    v-model="isOpen"
    :fullscreen="isMobile"
    :ui="{
      width: isMobile ? 'w-full' : 'sm:max-w-lg',
      height: isMobile ? 'h-full' : 'auto',
      container: isMobile ? 'items-end sm:items-center' : 'items-center'
    }"
  >
    <UCard :class="cardClass">
      <!-- Header with close button -->
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">
            {{ title }}
          </h3>
          <UButton
            icon="i-heroicons-x-mark"
            color="gray"
            variant="ghost"
            size="lg"
            class="btn-touch-target modal-close-mobile"
            aria-label="Fermer"
            @click="close"
          />
        </div>
      </template>

      <!-- Content -->
      <div :class="contentClass">
        <slot />
      </div>

      <!-- Footer -->
      <template v-if="$slots.footer" #footer>
        <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end">
          <slot name="footer" :close="close" />
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
/**
 * MobileModal Component
 *
 * Modal component optimized for mobile:
 * - Full-screen on mobile devices
 * - Slide-up animation on mobile
 * - Large close button (44x44px)
 * - Better spacing and padding
 * - Optional swipe to close
 *
 * @example
 * <MobileModal v-model="isOpen" title="Nouvelle transaction">
 *   <form>...</form>
 *   <template #footer="{ close }">
 *     <UButton @click="close">Annuler</UButton>
 *     <UButton @click="submit">Enregistrer</UButton>
 *   </template>
 * </MobileModal>
 */

interface Props {
  /** v-model for modal visibility */
  modelValue: boolean
  /** Modal title */
  title: string
  /** Disable swipe to close on mobile */
  noSwipe?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  close: []
}>()

// Detect mobile
const { isMobile } = useScreenSize()

// Internal state
const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Close function
const close = () => {
  isOpen.value = false
  emit('close')
}

// Computed classes
const cardClass = computed(() => {
  const classes = []

  if (isMobile.value) {
    classes.push('h-full', 'flex', 'flex-col', 'rounded-t-xl', 'sm:rounded-xl')
  }

  return classes.join(' ')
})

const contentClass = computed(() => {
  const classes = ['space-y-4']

  if (isMobile.value) {
    classes.push('flex-1', 'overflow-y-auto', 'p-4', 'sm:p-6')
  }

  return classes.join(' ')
})

// Swipe to close on mobile (optional feature)
const startY = ref(0)
const currentY = ref(0)

if (!props.noSwipe && process.client) {
  const handleTouchStart = (e: TouchEvent) => {
    startY.value = e.touches[0].clientY
  }

  const handleTouchMove = (e: TouchEvent) => {
    currentY.value = e.touches[0].clientY
    const diff = currentY.value - startY.value

    // If swiping down more than 100px, close
    if (diff > 100) {
      close()
    }
  }

  onMounted(() => {
    if (isMobile.value) {
      document.addEventListener('touchstart', handleTouchStart, { passive: true })
      document.addEventListener('touchmove', handleTouchMove, { passive: true })
    }
  })

  onUnmounted(() => {
    if (isMobile.value) {
      document.removeEventListener('touchstart', handleTouchStart)
      document.removeEventListener('touchmove', handleTouchMove)
    }
  })
}
</script>

<style scoped>
/* Slide-up animation for mobile */
@media (max-width: 640px) {
  :deep(.modal-mobile) {
    animation: slide-up 0.3s ease-out;
  }

  @keyframes slide-up {
    from {
      transform: translateY(100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
}
</style>
