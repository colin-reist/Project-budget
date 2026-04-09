<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col justify-start sm:justify-center overflow-y-auto px-4 py-6 sm:py-12 sm:px-6 lg:px-8">
    <div class="w-full sm:mx-auto sm:w-full sm:max-w-md">
      <h1 class="text-center text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-6 sm:mb-8">
        Budget Tracker
      </h1>

      <div class="bg-white dark:bg-gray-800 py-6 px-5 shadow sm:rounded-lg sm:py-8 sm:px-10">
        <slot />
      </div>
    </div>
  </div>
</template>
