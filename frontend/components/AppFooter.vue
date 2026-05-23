<template>
  <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="grid grid-cols-2 md:grid-cols-3 gap-6">

        <!-- Navigation rapide -->
        <div>
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Navigation</h3>
          <ul class="space-y-2">
            <li v-for="link in quickLinks" :key="link.to">
              <NuxtLink
                :to="link.to"
                class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                <UIcon :name="link.icon" class="h-3.5 w-3.5 shrink-0" />
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Raccourcis -->
        <div>
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Raccourcis</h3>
          <ul class="space-y-2">
            <li v-for="shortcut in shortcuts" :key="shortcut.key" class="flex items-center gap-2">
              <kbd class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-mono bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600">
                {{ shortcut.key }}
              </kbd>
              <span class="text-sm text-gray-600 dark:text-gray-400">{{ shortcut.label }}</span>
            </li>
          </ul>
        </div>

        <!-- Compte & Paramètres -->
        <div>
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Mon compte</h3>
          <ul class="space-y-2">
            <li v-for="link in accountLinks" :key="link.to">
              <NuxtLink
                :to="link.to"
                class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                <UIcon :name="link.icon" class="h-3.5 w-3.5 shrink-0" />
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

      </div>

      <!-- Bas du footer : version + build date -->
      <div class="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between">
        <span class="text-xs font-semibold text-gray-400 dark:text-gray-500">Budget Tracker</span>
        <span class="text-xs text-gray-300 dark:text-gray-600 tabular-nums" :title="`Build: ${buildDateFull}`">
          v{{ version }} &middot; {{ buildDateShort }}
        </span>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const config = useRuntimeConfig();

const version = config.public.appVersion;
const buildDateFull = config.public.buildDate;
const buildDateShort = computed(() => {
  const d = new Date(buildDateFull);
  return d.toLocaleDateString('fr-CH', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
});

const quickLinks = [
  { to: '/', label: 'Dashboard', icon: 'i-heroicons-home' },
  { to: '/transactions', label: 'Transactions', icon: 'i-heroicons-arrows-right-left' },
  { to: '/accounts', label: 'Comptes', icon: 'i-heroicons-building-library' },
  { to: '/tools/savings-goal', label: 'Épargne', icon: 'i-heroicons-banknotes' },
  { to: '/budgets', label: 'Budgets', icon: 'i-heroicons-chart-bar' },
];

const accountLinks = [
  { to: '/profile', label: 'Profil', icon: 'i-heroicons-user-circle' },
  { to: '/settings', label: 'Paramètres', icon: 'i-heroicons-cog-6-tooth' },
  { to: '/categories', label: 'Catégories', icon: 'i-heroicons-tag' },
  { to: '/tools/monthly-wrap', label: 'Review mensuel', icon: 'i-heroicons-calendar' },
  { to: '/tools/annual-wrap', label: 'Bilan annuel', icon: 'i-heroicons-chart-bar-square' },
];

const shortcuts = [
  { key: 'Ctrl+N', label: 'Nouvelle transaction' },
  { key: '?', label: 'Aide raccourcis' },
];
</script>
