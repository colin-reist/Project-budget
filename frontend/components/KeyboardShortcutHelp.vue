<template>
  <UModal v-model="isOpen">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <UIcon name="i-heroicons-command-line" class="h-5 w-5 text-primary-600" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Raccourcis clavier
            </h3>
          </div>
          <UButton
            icon="i-heroicons-x-mark"
            color="gray"
            variant="ghost"
            size="sm"
            @click="isOpen = false"
          />
        </div>
      </template>

      <div class="space-y-6">
        <!-- Actions principales -->
        <div>
          <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
            Actions principales
          </h4>
          <div class="space-y-2">
            <div class="flex items-center justify-between py-2 px-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span class="text-sm text-gray-700 dark:text-gray-300">Nouvelle transaction</span>
              <div class="flex items-center gap-1">
                <UKbd>{{ isMac ? '⌘' : 'Ctrl' }}</UKbd>
                <span class="text-gray-400">+</span>
                <UKbd>N</UKbd>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <div>
          <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
            Navigation
          </h4>
          <div class="space-y-2">
            <div class="flex items-center justify-between py-2 px-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span class="text-sm text-gray-700 dark:text-gray-300">Fermer les modals</span>
              <UKbd>Esc</UKbd>
            </div>
          </div>
        </div>

        <!-- Info -->
        <div class="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div class="flex items-start gap-2">
            <UIcon name="i-heroicons-information-circle" class="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div class="text-sm text-blue-700 dark:text-blue-400">
              <p class="font-medium mb-1">Astuce</p>
              <p>Utilisez ces raccourcis pour naviguer plus rapidement dans l'application.</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end">
          <UButton @click="isOpen = false">
            Fermer
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
/**
 * KeyboardShortcutHelp Component
 *
 * Affiche une modal avec tous les raccourcis clavier disponibles dans l'application.
 * Détecte automatiquement Mac vs Windows pour afficher les bons symboles.
 *
 * @example
 * <KeyboardShortcutHelp v-model="showHelp" />
 */

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isMac = process.client && navigator.platform.toUpperCase().indexOf('MAC') >= 0
</script>
