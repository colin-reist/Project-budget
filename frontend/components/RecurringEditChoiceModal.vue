<script setup lang="ts">
/**
 * Modal de choix affiché lorsque l'utilisateur tente d'éditer une transaction
 * appartenant à une série récurrente.
 *
 * Émet :
 * - "edit-single"  : l'utilisateur veut modifier uniquement cette occurrence
 * - "edit-series"  : l'utilisateur veut modifier toute la série (instances futures)
 * - "update:modelValue" : pour fermer le modal via v-model
 */
defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  /** Modifier uniquement cette occurrence */
  (e: 'edit-single'): void
  /** Modifier toute la série (instances futures) */
  (e: 'edit-series'): void
}>()

const close = () => emit('update:modelValue', false)

const chooseSingle = () => {
  emit('edit-single')
  close()
}

const chooseSeries = () => {
  emit('edit-series')
  close()
}
</script>

<template>
  <UModal :model-value="modelValue" @update:model-value="emit('update:modelValue', $event)">
    <UCard>
      <template #header>
        <div class="flex items-center gap-3">
          <div class="flex-shrink-0 w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
            <UIcon name="i-heroicons-arrow-path" class="text-amber-600 text-xl" />
          </div>
          <h3 class="text-lg font-semibold">Transaction récurrente</h3>
        </div>
      </template>

      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Cette transaction fait partie d'une <strong>série récurrente</strong>.
        Souhaitez-vous modifier uniquement cette occurrence ou toute la série ?
      </p>

      <div class="flex flex-col sm:flex-row gap-3">
        <UButton
          color="gray"
          variant="outline"
          class="flex-1 justify-center"
          icon="i-heroicons-pencil-square"
          @click="chooseSingle"
        >
          Cette occurrence seulement
        </UButton>
        <UButton
          class="flex-1 justify-center"
          icon="i-heroicons-arrow-path"
          @click="chooseSeries"
        >
          Toute la série
        </UButton>
      </div>

      <template #footer>
        <div class="flex justify-end">
          <UButton color="gray" variant="ghost" @click="close">
            Annuler
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>
