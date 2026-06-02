// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui'
  ],

  runtimeConfig: {
    // Private keys (only available server-side)
    apiBaseServer: process.env.NUXT_API_BASE_SERVER || process.env.NUXT_PUBLIC_API_BASE || 'http://backend:8000',
    public: {
      // Public keys that are exposed to the client
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000',
      appVersion: '1.0.0',
      buildDate: new Date().toISOString(),
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
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap' }
      ]
    }
  },

  // CSS configuration
  css: [
    '~/assets/css/design-system.css',
    '~/assets/css/mobile-improvements.css'
  ],

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
  },

  // Dev server configuration (pour Docker)
  devServer: {
    host: '0.0.0.0',
    port: 3000
  },

  // Proxy dev : redirige /api/* vers le backend Django (seulement en `nuxt dev`)
  nitro: {
    devProxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
