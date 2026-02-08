<template>
  <div>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Dashboard
      </h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">
        Vue d'ensemble de vos finances
      </p>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
      <UCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UIcon name="i-heroicons-arrow-trending-up" class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
              Revenus ce mois
            </p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ formatCurrency(monthlyIncome) }}
            </p>
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UIcon name="i-heroicons-arrow-trending-down" class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
              Dépenses ce mois
            </p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ formatCurrency(monthlyExpenses) }}
            </p>
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UIcon name="i-heroicons-chart-bar" class="h-8 w-8 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
              Économies
            </p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ formatCurrency(savings) }}
            </p>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Accounts Section -->
    <div class="mb-8">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Mes comptes</h2>
        <NuxtLink to="/accounts" class="text-sm text-primary-600 hover:text-primary-500">
          Gérer les comptes
        </NuxtLink>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <UCard v-for="account in accounts" :key="account.id" class="hover:shadow-md transition-shadow">
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <h3 class="font-semibold text-gray-900 dark:text-white">{{ account.name }}</h3>
              <UBadge :color="account.account_type === 'checking' ? 'blue' : account.account_type === 'savings' ? 'green' : account.account_type === 'credit_card' ? 'orange' : 'gray'" variant="subtle" size="xs">
                {{ account.account_type_display }}
              </UBadge>
            </div>
            <div class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ formatCurrency(parseFloat(account.current_balance || 0)) }}
            </div>
            <div class="text-xs text-gray-500">
              {{ account.currency }}
            </div>
          </div>
        </UCard>

        <UCard v-if="accounts.length === 0" class="col-span-full">
          <div class="text-center py-8">
            <UIcon name="i-heroicons-banknotes" class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium">Aucun compte</h3>
            <p class="mt-1 text-sm text-gray-500">
              Créez votre premier compte pour commencer
            </p>
            <div class="mt-6">
              <NuxtLink to="/accounts">
                <UButton>Créer un compte</UButton>
              </NuxtLink>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Total Balance -->
      <div v-if="accounts.length > 0" class="mt-4 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <UIcon name="i-heroicons-banknotes" class="h-6 w-6 text-primary-600 mr-2" />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Solde total</span>
          </div>
          <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {{ formatCurrency(totalBalance) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Charts and Recent Transactions -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Expenses Chart Placeholder -->
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Dépenses par catégorie
          </h3>
        </template>
        <div class="h-64 flex items-center justify-center text-gray-500">
          Graphique des dépenses (D3.js)
        </div>
      </UCard>

      <!-- Recent Transactions -->
      <UCard>
        <template #header>
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Transactions récentes
            </h3>
            <NuxtLink to="/transactions" class="text-sm text-primary-600 hover:text-primary-500">
              Voir tout
            </NuxtLink>
          </div>
        </template>
        <div class="space-y-4">
          <div v-if="recentTransactions.length === 0" class="text-center py-8 text-gray-500">
            Aucune transaction récente
          </div>
          <div
            v-for="transaction in recentTransactions"
            :key="transaction.id"
            class="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700 last:border-0"
          >
            <div class="flex items-center">
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ transaction.description }}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  {{ formatDate(transaction.date) }}
                </p>
              </div>
            </div>
            <div :class="[
              'text-sm font-semibold',
              transaction.type === 'income' ? 'text-green-600' : 'text-red-600'
            ]">
              {{ transaction.type === 'income' ? '+' : '-' }}{{ formatCurrency(Math.abs(parseFloat(transaction.amount))) }}
            </div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Transaction } from '~/types';

definePageMeta({
  middleware: 'auth'
});

const { getAccountsSummary, getAccounts } = useAccounts();
const { getTransactions, getStatistics } = useTransactions();

// Reactive state
const totalBalance = ref(0);
const accounts = ref<any[]>([]);
const monthlyIncome = ref(0);
const monthlyExpenses = ref(0);
const savings = ref(0);
const recentTransactions = ref<Transaction[]>([]);

// Get current month date range
const getCurrentMonthRange = () => {
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);

  const formatDate = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  return {
    start_date: formatDate(startOfMonth),
    end_date: formatDate(endOfMonth)
  };
};

// Fetch dashboard data
const fetchDashboardData = async () => {
  try {
    // Fetch all accounts to display individually
    const accountsResponse = await getAccounts({ is_active: true });
    if (accountsResponse.success && accountsResponse.data) {
      accounts.value = accountsResponse.data.results;
      // Calculate total balance from current balances (excluant les transactions futures)
      totalBalance.value = accounts.value.reduce((sum, account) => {
        return sum + parseFloat(account.current_balance || 0);
      }, 0);
    }

    // Fetch recent transactions
    const transactionsResponse = await getTransactions({ ordering: '-date' });
    if (transactionsResponse.success && transactionsResponse.data) {
      recentTransactions.value = transactionsResponse.data.results.slice(0, 5);
    }

    // Fetch monthly statistics
    const monthRange = getCurrentMonthRange();
    const statsResponse = await getStatistics(monthRange);
    if (statsResponse.success && statsResponse.data) {
      monthlyIncome.value = statsResponse.data.income.total;
      monthlyExpenses.value = statsResponse.data.expense.total;
      savings.value = statsResponse.data.net;
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
  }
};

// Utility functions
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-CH', {
    style: 'currency',
    currency: 'CHF',
  }).format(amount);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
};

// Load data on mount
onMounted(() => {
  fetchDashboardData();
});
</script>
