<template>
  <div>
    <div class="mb-8 flex justify-between items-start">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Vue d'ensemble de vos finances
        </p>
      </div>
      <UButton
        icon="i-heroicons-plus"
        size="lg"
        color="primary"
        @click="showTransactionModal = true"
      >
        Nouvelle transaction
      </UButton>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
      <UCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UIcon name="i-heroicons-arrow-trending-up" class="h-8 w-8 text-blue-600" />
          </div>
          <div class="ml-4 flex-1">
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
              Revenus ce mois
            </p>
            <div class="flex flex-wrap items-baseline gap-2">
              <p class="text-2xl font-bold text-gray-900 dark:text-white">
                {{ formatCurrency(monthlyIncome) }}
              </p>
              <p v-if="futureIncome !== 0" class="text-sm text-blue-600 dark:text-blue-400 font-medium">
                ({{ formatCurrency(monthlyIncome + futureIncome) }})
              </p>
            </div>
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UIcon name="i-heroicons-arrow-trending-down" class="h-8 w-8 text-red-600" />
          </div>
          <div class="ml-4 flex-1">
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
              Dépenses ce mois
            </p>
            <div class="flex flex-wrap items-baseline gap-2">
              <p class="text-2xl font-bold text-gray-900 dark:text-white">
                {{ formatCurrency(monthlyExpenses) }}
              </p>
              <p v-if="futureExpenses !== 0" class="text-sm text-red-600 dark:text-red-400 font-medium">
                ({{ formatCurrency(monthlyExpenses + futureExpenses) }})
              </p>
            </div>
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <UIcon name="i-heroicons-chart-bar" class="h-8 w-8 text-purple-600" />
          </div>
          <div class="ml-4 flex-1">
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
              Économies
            </p>
            <div class="flex flex-wrap items-baseline gap-2">
              <p class="text-2xl font-bold text-gray-900 dark:text-white">
                {{ formatCurrency(savings) }}
              </p>
              <p v-if="futureSavings !== 0" :class="[
                'text-sm font-medium',
                (savings + futureSavings) > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              ]">
                ({{ formatCurrency(savings + futureSavings) }})
              </p>
            </div>
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
        <UCard v-for="account in accounts" :key="account.id" class="hover:shadow-md transition-shadow cursor-pointer" @click="openTransactionWithAccount(account.id)">
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

    <!-- Quick Transaction Modal -->
    <UModal v-model="showTransactionModal" :ui="{ width: 'sm:max-w-lg' }">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">Nouvelle transaction</h3>
        </template>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Type -->
          <UFormGroup label="Type" required :error="formErrors.type">
            <USelectMenu
              v-model="transactionForm.type"
              :options="[
                { label: 'Revenu', value: 'income', icon: 'i-heroicons-arrow-trending-up' },
                { label: 'Dépense', value: 'expense', icon: 'i-heroicons-arrow-trending-down' },
                { label: 'Transfert', value: 'transfer', icon: 'i-heroicons-arrow-path' }
              ]"
              option-attribute="label"
              value-attribute="value"
            />
          </UFormGroup>

          <!-- Amount -->
          <UFormGroup label="Montant (CHF)" required :error="formErrors.amount">
            <UInput
              v-model="transactionForm.amount"
              type="number"
              step="0.01"
              placeholder="0.00"
              required
            />
          </UFormGroup>

          <!-- Account -->
          <UFormGroup label="Compte" required :error="formErrors.account">
            <USelectMenu
              v-model="transactionForm.account"
              :options="accounts"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner un compte"
            />
          </UFormGroup>

          <!-- Destination Account (only for transfers) -->
          <UFormGroup v-if="transactionForm.type === 'transfer'" label="Compte destination" required :error="formErrors.destination_account">
            <USelectMenu
              v-model="transactionForm.destination_account"
              :options="accounts.filter(a => a.id !== parseInt(transactionForm.account))"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner le compte de destination"
            />
          </UFormGroup>

          <!-- Category (only for income/expense) -->
          <UFormGroup v-if="transactionForm.type !== 'transfer'" label="Catégorie" required :error="formErrors.category">
            <USelectMenu
              v-model="transactionForm.category"
              :options="filteredCategories"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner une catégorie"
            />
          </UFormGroup>

          <!-- Description -->
          <UFormGroup label="Description" :error="formErrors.description">
            <UInput
              v-model="transactionForm.description"
              placeholder="Ex: Courses Migros"
            />
          </UFormGroup>

          <!-- Date -->
          <UFormGroup label="Date" required :error="formErrors.date">
            <UInput
              v-model="transactionForm.date"
              type="date"
              required
            />
          </UFormGroup>

          <!-- Actions -->
          <div class="flex justify-end gap-2 pt-4">
            <UButton color="gray" variant="ghost" @click="closeModal">
              Annuler
            </UButton>
            <UButton type="submit" :loading="loading">
              Créer
            </UButton>
          </div>
        </form>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { Transaction } from '~/types';

definePageMeta({
  middleware: 'auth'
});

const { getAccountsSummary, getAccounts } = useAccounts();
const { getTransactions, getStatistics, createTransaction } = useTransactions();
const { getCategories } = useCategories();
const toast = useToast();

// Reactive state
const totalBalance = ref(0);
const accounts = ref<any[]>([]);
const categories = ref<any[]>([]);
const monthlyIncome = ref(0);
const monthlyExpenses = ref(0);
const savings = ref(0);
const futureIncome = ref(0);
const futureExpenses = ref(0);
const recentTransactions = ref<Transaction[]>([]);
const showTransactionModal = ref(false);
const loading = ref(false);
const formErrors = ref<Record<string, string>>({});

// Transaction form
const transactionForm = ref<{
  type: string;
  amount: string;
  account: string | number;
  destination_account: string | number;
  category: string | number;
  description: string;
  date: string;
}>({
  type: 'expense',
  amount: '',
  account: '',
  destination_account: '',
  category: '',
  description: '',
  date: new Date().toISOString().split('T')[0]
});

// Filtered categories based on transaction type
const filteredCategories = computed(() => {
  return categories.value.filter(cat => {
    if (transactionForm.value.type === 'income') return cat.type === 'income';
    if (transactionForm.value.type === 'expense') return cat.type === 'expense';
    return false;
  });
});

// Calculate future savings (future income - future expenses)
const futureSavings = computed(() => {
  return futureIncome.value - futureExpenses.value;
});

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

    // Fetch categories
    const categoriesResponse = await getCategories({ is_active: true });
    if (categoriesResponse.success && categoriesResponse.data) {
      categories.value = categoriesResponse.data.results;
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
      futureIncome.value = statsResponse.data.income.future || 0;
      futureExpenses.value = statsResponse.data.expense.future || 0;
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
  }
};

// Handle form submission
const handleSubmit = async () => {
  loading.value = true;
  formErrors.value = {}; // Reset errors

  const transactionData: any = {
    type: transactionForm.value.type,
    amount: transactionForm.value.amount,
    account: parseInt(transactionForm.value.account),
    description: transactionForm.value.description,
    date: transactionForm.value.date
  };

  // Add category for income/expense
  if (transactionForm.value.type !== 'transfer' && transactionForm.value.category) {
    transactionData.category = parseInt(transactionForm.value.category);
  }

  // Add destination account for transfers
  if (transactionForm.value.type === 'transfer' && transactionForm.value.destination_account) {
    transactionData.destination_account = parseInt(transactionForm.value.destination_account);
  }

  const result = await createTransaction(transactionData);
  loading.value = false;

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Transaction créée avec succès',
      color: 'green'
    });
    closeModal();
    await fetchDashboardData(); // Refresh data
  } else {
    // Parse validation errors
    if (result.error?.data) {
      const errors = result.error.data;
      // Convert error arrays to strings
      Object.keys(errors).forEach(key => {
        if (Array.isArray(errors[key])) {
          formErrors.value[key] = errors[key][0];
        } else if (typeof errors[key] === 'string') {
          formErrors.value[key] = errors[key];
        }
      });

      // Show first error in toast
      const firstError = Object.values(formErrors.value)[0];
      toast.add({
        title: 'Erreur de validation',
        description: firstError || 'Veuillez vérifier les champs du formulaire',
        color: 'red'
      });
    } else {
      toast.add({
        title: 'Erreur',
        description: 'Impossible de créer la transaction',
        color: 'red'
      });
    }
  }
};

// Close modal and reset form
const closeModal = () => {
  showTransactionModal.value = false;
  formErrors.value = {}; // Reset errors
  transactionForm.value = {
    type: 'expense',
    amount: '',
    account: '',
    destination_account: '',
    category: '',
    description: '',
    date: new Date().toISOString().split('T')[0]
  };
};

// Open transaction modal with pre-selected account
const openTransactionWithAccount = (accountId: number) => {
  transactionForm.value.account = accountId;
  showTransactionModal.value = true;
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
