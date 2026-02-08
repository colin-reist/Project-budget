// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui'
  ],

  runtimeConfig: {
    // Private keys (only available server-side)
    public: {
      // Public keys that are exposed to the client
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    }
  },

  // App configuration
  app: {
    head: {
      title: 'Budget Tracker',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Application de suivi de budget personnel' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // CSS configuration
  css: [],

  // Vite configuration
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: ''
        }
      }
    }
  },

  // TypeScript configuration
  typescript: {
    strict: true,
    typeCheck: false
  },

  // Nuxt UI configuration
  ui: {
    icons: ['heroicons', 'lucide']
  }
})
