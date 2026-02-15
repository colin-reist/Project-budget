<template>
  <UCard>
    <div class="space-y-4">
      <!-- Header skeleton -->
      <div v-if="showHeader" class="flex items-center justify-between">
        <div class="space-y-2 flex-1">
          <USkeleton class="h-5 w-32" />
          <USkeleton class="h-4 w-24" />
        </div>
        <USkeleton class="h-6 w-16 rounded-full" />
      </div>

      <!-- Content skeleton -->
      <div class="space-y-3">
        <USkeleton v-for="i in lines" :key="i" :class="getLineClass(i)" />
      </div>

      <!-- Footer skeleton (actions) -->
      <div v-if="showFooter" class="flex gap-2 pt-2">
        <USkeleton class="h-8 w-20 rounded-md" />
        <USkeleton class="h-8 w-20 rounded-md" />
      </div>
    </div>
  </UCard>
</template>

<script setup lang="ts">
/**
 * SkeletonCard Component
 *
 * Composant réutilisable pour afficher un skeleton loader pendant le chargement.
 * Simule la structure d'une carte typique de l'application.
 *
 * @example
 * <SkeletonCard :lines="3" show-header show-footer />
 */

interface Props {
  /** Nombre de lignes de contenu à afficher */
  lines?: number
  /** Afficher le header (titre + badge) */
  showHeader?: boolean
  /** Afficher le footer (boutons d'action) */
  showFooter?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  lines: 3,
  showHeader: true,
  showFooter: false
})

/**
 * Génère des classes de largeur variées pour un effet plus réaliste
 */
const getLineClass = (index: number) => {
  const widths = ['w-full', 'w-5/6', 'w-4/5', 'w-3/4', 'w-2/3']
  return `h-4 ${widths[index % widths.length]}`
}
</script>
