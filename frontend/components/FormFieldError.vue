<template>
  <div v-if="error" class="mt-1 text-sm text-red-500">
    {{ error }}
  </div>
</template>

<script setup lang="ts">
/**
 * Composant pour afficher une erreur au niveau d'un champ de formulaire.
 */
defineProps<{
  error?: string | null
}>()
</script>
