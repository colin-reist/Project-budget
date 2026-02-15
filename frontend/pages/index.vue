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
        <template #trailing>
          <UKbd>{{ shortcutLabel }}</UKbd>
        </template>
      </UButton>
    </div>

    <!-- Pending Alerts Banner -->
    <div v-if="pendingAlerts.length > 0" class="mb-6 space-y-2">
      <div
        v-for="alert in pendingAlerts"
        :key="alert.id"
        class="p-4 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg flex items-center justify-between"
      >
        <div class="flex items-center gap-3">
          <UIcon name="i-heroicons-device-phone-mobile" class="h-5 w-5 text-orange-600 flex-shrink-0" />
          <span class="text-sm text-orange-700 dark:text-orange-400">
            Transaction iOS : "{{ alert.payload.label }}" ({{ formatCurrency(parseFloat(alert.payload.amount)) }}) &mdash; catégorie "{{ alert.payload.category_name }}" non trouvée.
          </span>
        </div>
        <div class="flex gap-2 flex-shrink-0">
          <UButton size="sm" variant="soft" @click="openCorrectionModal(alert)">Corriger</UButton>
          <UButton size="sm" variant="ghost" color="gray" @click="handleDismissAlert(alert.id)">Ignorer</UButton>
        </div>
      </div>
    </div>

    <!-- Loading State: Summary Cards Skeletons -->
    <div v-if="initialLoading" class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
      <SkeletonCard v-for="i in 3" :key="i" :lines="2" :show-header="false" />
    </div>

    <!-- Summary Cards -->
    <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 mb-8">
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
              <UTooltip v-if="futureIncome !== 0" text="Solde projeté incluant vos revenus futurs planifiés ce mois">
                <p class="text-sm text-blue-600 dark:text-blue-400 font-medium cursor-help">
                  ({{ formatCurrency(monthlyIncome + futureIncome) }})
                </p>
              </UTooltip>
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
              <UTooltip v-if="futureExpenses !== 0" text="Montant projeté incluant vos dépenses futures planifiées ce mois">
                <p class="text-sm text-red-600 dark:text-red-400 font-medium cursor-help">
                  ({{ formatCurrency(monthlyExpenses + futureExpenses) }})
                </p>
              </UTooltip>
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
              <UTooltip v-if="futureSavings !== 0" text="Économies projetées incluant vos transactions futures planifiées ce mois">
                <p :class="[
                  'text-sm font-medium cursor-help',
                  (savings + futureSavings) > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                ]">
                  ({{ formatCurrency(savings + futureSavings) }})
                </p>
              </UTooltip>
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

      <!-- Loading State: Account Cards Skeletons -->
      <div v-if="initialLoading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <SkeletonCard v-for="i in 4" :key="i" :lines="2" :show-header="false" />
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
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
          <EmptyState
            icon="i-heroicons-banknotes"
            color="blue"
            title="Commencez votre suivi financier 💰"
            description="Un compte, c'est comme une tirelire numérique. Ajoutez votre compte courant pour voir où part votre argent et suivre vos dépenses en temps réel!"
            button-text="Créer mon premier compte"
            @action="navigateTo('/accounts')"
          />
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

    <!-- Budget vs Réel Section -->
    <div v-if="budgetDashData && budgetDashData.categories.length > 0" class="mb-8">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Budget vs Réel</h2>

      <!-- Soldes résumé -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
        <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p class="text-sm text-gray-600 dark:text-gray-400">Solde prévisionnel</p>
          <p class="text-xl font-bold text-blue-600 dark:text-blue-400">
            {{ formatCurrency(budgetDashData.solde_previsionnel) }}
          </p>
        </div>
        <div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <p class="text-sm text-gray-600 dark:text-gray-400">Solde réel</p>
          <p class="text-xl font-bold text-green-600 dark:text-green-400">
            {{ formatCurrency(budgetDashData.solde_reel) }}
          </p>
        </div>
        <div :class="[
          'p-4 rounded-lg border',
          budgetDashData.ecart >= 0
            ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800'
            : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
        ]">
          <p class="text-sm text-gray-600 dark:text-gray-400">Écart</p>
          <p :class="[
            'text-xl font-bold',
            budgetDashData.ecart >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'
          ]">
            {{ budgetDashData.ecart >= 0 ? '+' : '' }}{{ formatCurrency(budgetDashData.ecart) }}
          </p>
        </div>
      </div>

      <!-- Graphique -->
      <UCard class="mb-4">
        <template #header>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Dépenses par catégorie</h3>
        </template>
        <BudgetVsActualChart :data="budgetDashData.categories" />
      </UCard>

      <!-- Tableau détaillé -->
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Détail par catégorie</h3>
        </template>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-200 dark:border-gray-700">
                <th class="text-left py-2 px-3 font-medium text-gray-500">Catégorie</th>
                <th class="text-right py-2 px-3 font-medium text-gray-500">Prévu</th>
                <th class="text-right py-2 px-3 font-medium text-gray-500">Réel</th>
                <th class="text-right py-2 px-3 font-medium text-gray-500">Écart</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="cat in budgetDashData.categories"
                :key="cat.category_id"
                class="border-b border-gray-100 dark:border-gray-800"
              >
                <td class="py-2 px-3">
                  <div class="flex items-center gap-2">
                    <UIcon :name="cat.category_icon" class="h-4 w-4" />
                    <span class="text-gray-900 dark:text-white">{{ cat.category_name }}</span>
                    <UBadge v-if="cat.is_mandatory_savings" color="blue" variant="subtle" size="xs">💰 Épargne obligatoire</UBadge>
                    <UBadge v-else-if="cat.unbudgeted" color="gray" variant="subtle" size="xs">Non budgété</UBadge>
                  </div>
                </td>
                <td class="py-2 px-3 text-right text-gray-600 dark:text-gray-400">
                  {{ cat.prevu > 0 ? formatCurrency(cat.prevu) : '-' }}
                </td>
                <td :class="['py-2 px-3 text-right font-medium', cat.is_over ? 'text-red-600' : 'text-gray-900 dark:text-white']">
                  {{ formatCurrency(cat.reel) }}
                </td>
                <td :class="['py-2 px-3 text-right font-medium', cat.ecart >= 0 ? 'text-green-600' : 'text-red-600']">
                  {{ cat.ecart >= 0 ? '+' : '' }}{{ formatCurrency(cat.ecart) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </UCard>
    </div>

    <!-- Charts and Recent Transactions -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

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
          <div v-if="recentTransactions.length === 0">
            <EmptyState
              icon="i-heroicons-arrows-right-left"
              color="purple"
              title="Aucune transaction"
              description="Commencez à enregistrer vos dépenses et revenus pour suivre votre budget!"
              button-text="Créer une transaction"
              button-icon="i-heroicons-plus"
              @action="showTransactionModal = true"
            />
          </div>
          <div
            v-for="transaction in recentTransactions"
            :key="transaction.id"
            class="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700 last:border-0"
          >
            <div class="flex items-center">
              <UIcon
                v-if="transaction.source === 'ios' || transaction.source === 'ios_uncategorized'"
                name="i-heroicons-device-phone-mobile"
                class="h-4 w-4 text-gray-400 flex-shrink-0"
                title="Transaction iOS"
              />
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

    <!-- Correction Modal (for iOS uncategorized transactions) -->
    <UModal v-model="showCorrectionModal">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">Corriger la catégorie</h3>
        </template>
        <div v-if="correctionAlert" class="space-y-4">
          <div class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p class="text-sm"><strong>Transaction :</strong> {{ correctionAlert.payload.label }}</p>
            <p class="text-sm"><strong>Montant :</strong> {{ formatCurrency(parseFloat(correctionAlert.payload.amount)) }}</p>
            <p class="text-sm"><strong>Catégorie saisie :</strong> {{ correctionAlert.payload.category_name }}</p>
          </div>
          <UFormGroup label="Catégorie">
            <USelectMenu
              v-model="correctionCategory"
              :options="categories.filter(c => c.type === 'expense')"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner une catégorie"
            />
          </UFormGroup>
          <div class="flex justify-end gap-2">
            <UButton variant="ghost" color="gray" @click="showCorrectionModal = false">Annuler</UButton>
            <UButton @click="handleCorrection" :loading="correcting" :disabled="!correctionCategory">Enregistrer</UButton>
          </div>
        </div>
      </UCard>
    </UModal>

    <!-- Onboarding Wizard -->
    <OnboardingWizard
      v-model="showOnboarding"
      @complete="handleOnboardingComplete"
      @skip="handleOnboardingComplete"
    />

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
              @blur="validateAmount"
              @input="formErrors.amount = ''"
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
              @update:model-value="formErrors.account = ''"
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
              @input="formErrors.description = ''"
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
import type { Transaction, PendingAlert } from '~/types';

definePageMeta({
  middleware: 'auth'
});

const { getAccountsSummary, getAccounts } = useAccounts();
const { getTransactions, getStatistics, createTransaction, updateTransaction } = useTransactions();
const { getCategories } = useCategories();
const { getDashboardData: getBudgetDashboardData } = useBudgets();
const { getAlerts, dismissAlert } = useAlerts();
const { registerShortcut, getShortcutLabel } = useKeyboardShortcuts();
const toast = useToast();

// Keyboard shortcut label for the button
const shortcutLabel = computed(() => getShortcutLabel('n', { ctrl: true }));

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
const initialLoading = ref(true);
const formErrors = ref<Record<string, string>>({});
const budgetDashData = ref<any>(null);

// Onboarding state
const showOnboarding = ref(false);

// Alerts state
const pendingAlerts = ref<PendingAlert[]>([]);
const showCorrectionModal = ref(false);
const correctionAlert = ref<PendingAlert | null>(null);
const correctionCategory = ref<string | number>('');
const correcting = ref(false);

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

// Fetch alerts
const fetchAlerts = async () => {
  const result = await getAlerts();
  if (result.success && result.data) {
    pendingAlerts.value = result.data;
  }
};

const handleDismissAlert = async (alertId: number) => {
  const result = await dismissAlert(alertId);
  if (result.success) {
    pendingAlerts.value = pendingAlerts.value.filter(a => a.id !== alertId);
  }
};

const openCorrectionModal = (alert: PendingAlert) => {
  correctionAlert.value = alert;
  correctionCategory.value = '';
  showCorrectionModal.value = true;
};

const handleCorrection = async () => {
  if (!correctionAlert.value || !correctionCategory.value) return;
  correcting.value = true;

  const result = await updateTransaction(correctionAlert.value.payload.transaction_id, {
    category: parseInt(String(correctionCategory.value)),
    source: 'ios'
  });

  if (result.success) {
    await dismissAlert(correctionAlert.value.id);
    pendingAlerts.value = pendingAlerts.value.filter(a => a.id !== correctionAlert.value!.id);
    showCorrectionModal.value = false;
    toast.add({ title: 'Corrigé', description: 'Catégorie mise à jour', color: 'green' });
    await fetchDashboardData();
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de corriger la transaction', color: 'red' });
  }
  correcting.value = false;
};

// Fetch dashboard data
const fetchDashboardData = async () => {
  try {
    initialLoading.value = true;

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

    // Check if first time user (no accounts and no categories)
    if (process.client && accounts.value.length === 0 && categories.value.length === 0) {
      const hasCompletedOnboarding = localStorage.getItem('onboarding_completed');
      if (!hasCompletedOnboarding) {
        showOnboarding.value = true;
      }
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

    // Fetch budget vs actual data
    const budgetDashResult = await getBudgetDashboardData();
    if (budgetDashResult.success && budgetDashResult.data) {
      budgetDashData.value = budgetDashResult.data;
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
  } finally {
    initialLoading.value = false;
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

// Real-time validation functions
const validateAmount = () => {
  const amount = parseFloat(transactionForm.value.amount);
  if (!transactionForm.value.amount) {
    formErrors.value.amount = 'Le montant est requis';
  } else if (isNaN(amount) || amount <= 0) {
    formErrors.value.amount = 'Le montant doit être supérieur à 0';
  } else {
    formErrors.value.amount = '';
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

// Handle onboarding completion
const handleOnboardingComplete = async () => {
  // Reload data to show the newly created account
  await fetchDashboardData();
  toast.add({
    title: 'Bienvenue! 🎉',
    description: 'Votre compte a été créé avec succès',
    color: 'green'
  });
};

// Load data on mount
onMounted(() => {
  fetchDashboardData();
  fetchAlerts();

  // Register keyboard shortcut: Ctrl+N or Cmd+N for new transaction
  registerShortcut('n', () => {
    showTransactionModal.value = true;
  }, {
    modifiers: { ctrl: true },
    description: 'Créer une nouvelle transaction'
  });
});
</script>
