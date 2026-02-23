<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
        📱 Test Currency Mobile
      </h1>
      <p class="text-gray-600 dark:text-gray-400">
        Page de test pour valider l'affichage responsive des devises
      </p>
    </div>

    <!-- Screen Info -->
    <UCard class="mb-6">
      <template #header>
        <h2 class="text-xl font-semibold">Informations d'écran</h2>
      </template>
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div>
          <p class="text-sm text-gray-500">Largeur</p>
          <p class="font-bold">{{ screenWidth }}px</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Type</p>
          <p class="font-bold">
            {{ isMobile ? '📱 Mobile' : isTablet ? '📱 Tablette' : '💻 Desktop' }}
          </p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Devise</p>
          <p class="font-bold flex items-center gap-2">
            <span class="text-lg">{{ getCurrencyFlag(currency) }}</span>
            {{ currency }}
          </p>
        </div>
      </div>
    </UCard>

    <!-- Currency Selector Test -->
    <UCard class="mb-6">
      <template #header>
        <h2 class="text-xl font-semibold">Sélecteur de Devise</h2>
      </template>
      <UFormGroup label="Changer la devise de test">
        <USelectMenu
          v-model="testCurrency"
          :options="currencyOptions"
          option-attribute="label"
          value-attribute="value"
        >
          <template #label>
            <span class="flex items-center gap-2">
              <span class="text-lg">{{ getCurrencyFlag(testCurrency) }}</span>
              <span>{{ getCurrencyLabel(testCurrency) }}</span>
            </span>
          </template>
          <template #option="{ option }">
            <span class="flex items-center gap-2">
              <span class="text-lg">{{ option.flag }}</span>
              <span>{{ option.label }}</span>
            </span>
          </template>
        </USelectMenu>
      </UFormGroup>
    </UCard>

    <!-- Amount Display Tests -->
    <UCard class="mb-6">
      <template #header>
        <h2 class="text-xl font-semibold">Test des Montants</h2>
      </template>

      <div class="space-y-6">
        <!-- Small amounts -->
        <div>
          <h3 class="text-lg font-semibold mb-3">Petits montants</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <TestAmountCard :amount="100" :currency="testCurrency" label="100" />
            <TestAmountCard :amount="1234.56" :currency="testCurrency" label="1 234,56" />
            <TestAmountCard :amount="9999.99" :currency="testCurrency" label="9 999,99" />
          </div>
        </div>

        <!-- Medium amounts -->
        <div>
          <h3 class="text-lg font-semibold mb-3">Montants moyens</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <TestAmountCard :amount="12345" :currency="testCurrency" label="12 345" compact />
            <TestAmountCard :amount="123456" :currency="testCurrency" label="123 456" compact />
            <TestAmountCard :amount="999999" :currency="testCurrency" label="999 999" compact />
          </div>
        </div>

        <!-- Large amounts -->
        <div>
          <h3 class="text-lg font-semibold mb-3">Grands montants</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <TestAmountCard :amount="1234567" :currency="testCurrency" label="1,2M" compact />
            <TestAmountCard :amount="12345678" :currency="testCurrency" label="12,3M" compact />
            <TestAmountCard :amount="123456789" :currency="testCurrency" label="123M" compact />
          </div>
        </div>
      </div>
    </UCard>

    <!-- Component Comparison -->
    <UCard class="mb-6">
      <template #header>
        <h2 class="text-xl font-semibold">Comparaison : Normal vs Compact</h2>
      </template>

      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700">
              <th class="text-left py-2 px-3">Montant</th>
              <th class="text-left py-2 px-3">Normal</th>
              <th class="text-left py-2 px-3">Compact</th>
              <th class="text-left py-2 px-3">Force Compact</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="amount in testAmounts" :key="amount" class="border-b border-gray-100 dark:border-gray-800">
              <td class="py-2 px-3 font-mono">{{ amount.toLocaleString() }}</td>
              <td class="py-2 px-3">
                <CurrencyAmount :amount="amount" :currency="testCurrency" />
              </td>
              <td class="py-2 px-3">
                <CurrencyAmount :amount="amount" :currency="testCurrency" compact />
              </td>
              <td class="py-2 px-3">
                <CurrencyAmount :amount="amount" :currency="testCurrency" forceCompact />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </UCard>

    <!-- Real-world Examples -->
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">Exemples Réels</h2>
      </template>

      <div class="space-y-4">
        <!-- Budget Card Example -->
        <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <h4 class="font-semibold mb-2">Budget Alimentation</h4>
          <div class="flex items-baseline justify-between">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Dépensé</p>
              <CurrencyAmount :amount="1234.56" :currency="testCurrency" compact class="text-2xl font-bold text-red-600" />
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Budget</p>
              <CurrencyAmount :amount="1500" :currency="testCurrency" compact class="text-2xl font-bold text-gray-900 dark:text-white" />
            </div>
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">Restant</p>
              <CurrencyAmount :amount="265.44" :currency="testCurrency" compact class="text-2xl font-bold text-green-600" />
            </div>
          </div>
        </div>

        <!-- Account Card Example -->
        <div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <h4 class="font-semibold mb-2">Compte Courant</h4>
          <CurrencyAmount :amount="123456.78" :currency="testCurrency" compact class="text-3xl font-bold text-gray-900 dark:text-white" />
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">Solde actuel</p>
        </div>

        <!-- Transaction List Example -->
        <div class="p-4 bg-gray-50 dark:bg-gray-900/20 rounded-lg">
          <h4 class="font-semibold mb-3">Transactions Récentes</h4>
          <div class="space-y-2">
            <div v-for="(transaction, index) in sampleTransactions" :key="index" class="flex justify-between items-center">
              <div>
                <p class="font-medium">{{ transaction.label }}</p>
                <p class="text-xs text-gray-500">{{ transaction.date }}</p>
              </div>
              <CurrencyAmount
                :amount="transaction.amount"
                :currency="testCurrency"
                :class="transaction.amount > 0 ? 'text-green-600' : 'text-red-600'"
                class="font-semibold"
              />
            </div>
          </div>
        </div>
      </div>
    </UCard>

    <!-- Back Button -->
    <div class="mt-8 text-center">
      <UButton to="/" size="lg">
        Retour au Dashboard
      </UButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CURRENCY_FLAGS } from '~/utils/currency'

definePageMeta({
  middleware: 'auth'
})

// Screen size detection
const { screenWidth, isMobile, isTablet, isDesktop } = useScreenSize()
const { currency } = useUserProfile()

// Test currency (independent from user profile)
const testCurrency = ref('CHF')

// Currency options
const currencyOptions = [
  { label: 'Franc Suisse (CHF)', value: 'CHF', flag: '🇨🇭' },
  { label: 'Euro (EUR)', value: 'EUR', flag: '🇪🇺' },
  { label: 'Dollar US (USD)', value: 'USD', flag: '🇺🇸' },
  { label: 'Livre Sterling (GBP)', value: 'GBP', flag: '🇬🇧' }
]

const getCurrencyFlag = (code: string) => {
  return CURRENCY_FLAGS[code] || '🌍'
}

const getCurrencyLabel = (code: string) => {
  return currencyOptions.find(c => c.value === code)?.label || code
}

// Test amounts
const testAmounts = [
  100,
  1234.56,
  12345,
  123456,
  1234567,
  12345678
]

// Sample transactions
const sampleTransactions = [
  { label: 'Courses Migros', amount: -123.45, date: '2026-02-23' },
  { label: 'Salaire', amount: 5000, date: '2026-02-20' },
  { label: 'Restaurant', amount: -45.80, date: '2026-02-22' },
  { label: 'Remboursement', amount: 234.56, date: '2026-02-21' }
]
</script>

<!-- Test Amount Card Component -->
<template>
  <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
    <p class="text-sm text-gray-500 mb-1">{{ label }}</p>
    <CurrencyAmount
      :amount="amount"
      :currency="currency"
      :compact="compact"
      :forceCompact="forceCompact"
      class="text-xl font-bold"
    />
    <p class="text-xs text-gray-400 mt-1">
      {{ isMobile ? '📱 Mobile' : '💻 Desktop' }}
    </p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  amount: number
  currency: string
  label: string
  compact?: boolean
  forceCompact?: boolean
}

defineProps<Props>()

const { isMobile } = useScreenSize()
</script>
