<template>
  <UModal
    v-model="showWarning"
    :prevent-close="true"
    :ui="{ width: 'sm:max-w-md' }"
  >
    <UCard>
      <template #header>
        <div class="flex items-center gap-3">
          <UIcon name="i-heroicons-exclamation-triangle" class="h-6 w-6 text-amber-500" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Session inactive
          </h3>
        </div>
      </template>

      <div class="flex flex-col items-center gap-6 py-4">
        <p class="text-center text-gray-600 dark:text-gray-400">
          Vous êtes inactif depuis un moment. Vous serez déconnecté dans&nbsp;:
        </p>

        <!-- Countdown ring -->
        <div class="relative flex items-center justify-center w-32 h-32">
          <svg class="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 120 120">
            <circle
              cx="60" cy="60" r="54"
              fill="none"
              stroke="currentColor"
              stroke-width="8"
              class="text-gray-200 dark:text-gray-700"
            />
            <circle
              cx="60" cy="60" r="54"
              fill="none"
              stroke="currentColor"
              stroke-width="8"
              stroke-linecap="round"
              class="text-amber-500 transition-all duration-1000"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="dashOffset"
            />
          </svg>
          <div class="flex flex-col items-center">
            <span class="text-4xl font-bold text-gray-900 dark:text-white">{{ countdown }}</span>
            <span class="text-xs text-gray-500 dark:text-gray-400">secondes</span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex flex-col sm:flex-row gap-3 justify-end">
          <UButton
            color="red"
            variant="ghost"
            @click="forceLogout"
          >
            Se déconnecter
          </UButton>
          <UButton
            color="green"
            @click="stayConnected"
          >
            Rester connecté
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
const { showWarning, countdown, stayConnected, forceLogout } = useSessionTimeout();

const circumference = 2 * Math.PI * 54; // 2πr where r=54

const dashOffset = computed(() => {
  const progress = countdown.value / 60;
  return circumference * (1 - progress);
});
</script>
