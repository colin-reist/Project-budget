<template>
  <div class="mt-2 text-sm text-gray-500 dark:text-gray-400 flex items-start gap-2">
    <UIcon v-if="icon" :name="icon" class="h-4 w-4 mt-0.5 flex-shrink-0" :class="iconClass" />
    <span><slot /></span>
  </div>
</template>

<script setup lang="ts">
/**
 * FormHint Component
 *
 * Affiche une note d'aide sous un champ de formulaire avec une icône optionnelle.
 * Utile pour donner du contexte ou des instructions à l'utilisateur.
 *
 * @example
 * <FormHint icon="i-heroicons-information-circle">
 *   Saisissez votre revenu mensuel net
 * </FormHint>
 */

interface Props {
  /** Icône à afficher (optionnel) */
  icon?: string
  /** Type de hint (info, warning, success) */
  type?: 'info' | 'warning' | 'success'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info'
})

const iconClass = computed(() => {
  const typeMap = {
    info: 'text-blue-600 dark:text-blue-400',
    warning: 'text-orange-600 dark:text-orange-400',
    success: 'text-green-600 dark:text-green-400'
  }
  return typeMap[props.type]
})
</script>
