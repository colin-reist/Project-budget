<template>
  <div class="text-center py-12 px-4">
    <!-- Icon/Illustration -->
    <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full mb-4" :class="iconBgClass">
      <UIcon :name="icon" class="h-10 w-10" :class="iconColorClass" />
    </div>

    <!-- Title -->
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
      {{ title }}
    </h3>

    <!-- Description -->
    <p class="text-sm text-gray-600 dark:text-gray-400 max-w-md mx-auto mb-6">
      {{ description }}
    </p>

    <!-- CTA Button -->
    <slot name="action">
      <UButton
        v-if="buttonText"
        :icon="buttonIcon"
        size="lg"
        @click="$emit('action')"
      >
        {{ buttonText }}
      </UButton>
    </slot>
  </div>
</template>

<script setup lang="ts">
/**
 * EmptyState Component
 *
 * Composant réutilisable pour afficher un état vide engageant avec:
 * - Icône colorée dans un cercle
 * - Titre et description motivants
 * - Call-to-action clair
 *
 * @example
 * <EmptyState
 *   icon="i-heroicons-banknotes"
 *   title="Aucun compte pour le moment"
 *   description="Créez votre premier compte pour commencer à suivre vos finances!"
 *   button-text="Créer mon premier compte"
 *   @action="openModal"
 * />
 */

interface Props {
  /** Nom de l'icône Heroicons */
  icon: string
  /** Titre principal de l'empty state */
  title: string
  /** Description détaillée et engageante */
  description: string
  /** Texte du bouton CTA (optionnel) */
  buttonText?: string
  /** Icône du bouton (optionnel) */
  buttonIcon?: string
  /** Couleur du thème (primary, green, blue, etc.) */
  color?: 'primary' | 'green' | 'blue' | 'purple' | 'orange' | 'red' | 'gray'
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary',
  buttonIcon: 'i-heroicons-plus'
})

defineEmits<{
  action: []
}>()

// Computed classes basées sur la couleur
const iconBgClass = computed(() => {
  const colorMap = {
    primary: 'bg-primary-100 dark:bg-primary-900/20',
    green: 'bg-green-100 dark:bg-green-900/20',
    blue: 'bg-blue-100 dark:bg-blue-900/20',
    purple: 'bg-purple-100 dark:bg-purple-900/20',
    orange: 'bg-orange-100 dark:bg-orange-900/20',
    red: 'bg-red-100 dark:bg-red-900/20',
    gray: 'bg-gray-100 dark:bg-gray-800'
  }
  return colorMap[props.color]
})

const iconColorClass = computed(() => {
  const colorMap = {
    primary: 'text-primary-600 dark:text-primary-400',
    green: 'text-green-600 dark:text-green-400',
    blue: 'text-blue-600 dark:text-blue-400',
    purple: 'text-purple-600 dark:text-purple-400',
    orange: 'text-orange-600 dark:text-orange-400',
    red: 'text-red-600 dark:text-red-400',
    gray: 'text-gray-600 dark:text-gray-400'
  }
  return colorMap[props.color]
})
</script>
