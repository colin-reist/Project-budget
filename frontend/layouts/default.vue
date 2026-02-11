<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Navigation -->
    <nav class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <!-- Logo -->
            <div class="flex-shrink-0 flex items-center">
              <NuxtLink to="/" class="text-xl font-bold text-primary-600">
                Budget Tracker
              </NuxtLink>
            </div>

            <!-- Navigation Links -->
            <div v-if="isAuthenticated" class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <NuxtLink
                to="/"
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-primary-500 text-gray-900 dark:text-white"
                inactive-class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                Dashboard
              </NuxtLink>
              <NuxtLink
                to="/accounts"
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-primary-500 text-gray-900 dark:text-white"
                inactive-class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                Comptes
              </NuxtLink>
              <NuxtLink
                to="/categories"
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-primary-500 text-gray-900 dark:text-white"
                inactive-class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                Catégories
              </NuxtLink>
              <NuxtLink
                to="/transactions"
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-primary-500 text-gray-900 dark:text-white"
                inactive-class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                Transactions
              </NuxtLink>
              <NuxtLink
                to="/budgets"
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-primary-500 text-gray-900 dark:text-white"
                inactive-class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                Budgets
              </NuxtLink>
              <NuxtLink
                to="/tools/savings-goal"
                class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                active-class="border-primary-500 text-gray-900 dark:text-white"
                inactive-class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              >
                Épargne
              </NuxtLink>
            </div>
          </div>

          <!-- User Menu -->
          <div v-if="isAuthenticated" class="flex items-center gap-3">
            <!-- Theme Toggle Button -->
            <UButton
              :icon="isDark ? 'i-heroicons-moon-20-solid' : 'i-heroicons-sun-20-solid'"
              color="gray"
              variant="ghost"
              aria-label="Changer le thème"
              @click="toggleTheme"
            />

            <UDropdown :items="userMenuItems" :popper="{ placement: 'bottom-end' }">
              <UButton
                color="white"
                :label="user?.username || 'User'"
                trailing-icon="i-heroicons-chevron-down-20-solid"
                class="hidden sm:inline-flex"
              />
            </UDropdown>

            <!-- Mobile hamburger -->
            <UButton
              icon="i-heroicons-bars-3"
              color="gray"
              variant="ghost"
              class="sm:hidden"
              aria-label="Ouvrir le menu"
              @click="mobileMenuOpen = true"
            />
          </div>
        </div>
      </div>
    </nav>

    <!-- Mobile menu slideover -->
    <USlideover v-model="mobileMenuOpen" side="right">
      <div class="p-4 space-y-1">
        <div class="flex items-center justify-between mb-4">
          <span class="text-lg font-bold text-primary-600">Menu</span>
          <UButton
            icon="i-heroicons-x-mark"
            color="gray"
            variant="ghost"
            aria-label="Fermer le menu"
            @click="mobileMenuOpen = false"
          />
        </div>

        <div v-if="user" class="pb-3 mb-3 border-b border-gray-200 dark:border-gray-700">
          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ user.username }}</p>
          <p class="text-xs text-gray-500">{{ user.email }}</p>
        </div>

        <NuxtLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
          active-class="bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400"
          @click="mobileMenuOpen = false"
        >
          <UIcon :name="link.icon" class="h-5 w-5" />
          {{ link.label }}
        </NuxtLink>

        <div class="pt-3 mt-3 border-t border-gray-200 dark:border-gray-700 space-y-1">
          <NuxtLink
            to="/profile"
            class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            @click="mobileMenuOpen = false"
          >
            <UIcon name="i-heroicons-user-circle" class="h-5 w-5" />
            Profil
          </NuxtLink>
          <NuxtLink
            to="/settings"
            class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            @click="mobileMenuOpen = false"
          >
            <UIcon name="i-heroicons-cog-6-tooth" class="h-5 w-5" />
            Paramètres
          </NuxtLink>
          <button
            class="flex items-center gap-3 w-full px-3 py-2 rounded-md text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
            @click="mobileMenuOpen = false; logout()"
          >
            <UIcon name="i-heroicons-arrow-right-on-rectangle" class="h-5 w-5" />
            Déconnexion
          </button>
        </div>
      </div>
    </USlideover>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const { user, isAuthenticated, logout } = useAuth();

// Mobile menu
const mobileMenuOpen = ref(false);

const navLinks = [
  { to: '/', label: 'Dashboard', icon: 'i-heroicons-home' },
  { to: '/accounts', label: 'Comptes', icon: 'i-heroicons-building-library' },
  { to: '/categories', label: 'Catégories', icon: 'i-heroicons-tag' },
  { to: '/transactions', label: 'Transactions', icon: 'i-heroicons-arrows-right-left' },
  { to: '/budgets', label: 'Budgets', icon: 'i-heroicons-chart-bar' },
  { to: '/tools/savings-goal', label: 'Épargne', icon: 'i-heroicons-banknotes' },
];

// Theme management
const colorMode = useColorMode();
const isDark = computed({
  get() {
    return colorMode.value === 'dark';
  },
  set() {
    colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark';
  }
});

const toggleTheme = () => {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark';
};

const userMenuItems = [
  [
    {
      label: user.value?.email || '',
      slot: 'account',
      disabled: true,
    },
  ],
  [
    {
      label: 'Profil',
      icon: 'i-heroicons-user-circle',
      click: () => navigateTo('/profile'),
    },
    {
      label: 'Paramètres',
      icon: 'i-heroicons-cog-6-tooth',
      click: () => navigateTo('/settings'),
    },
  ],
  [
    {
      label: 'Déconnexion',
      icon: 'i-heroicons-arrow-right-on-rectangle',
      click: () => logout(),
    },
  ],
];
</script>
