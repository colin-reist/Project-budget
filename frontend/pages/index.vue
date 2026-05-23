<template>
  <div>
    <div class="mb-6 sm:mb-8 flex justify-between items-center">
      <div>
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p class="mt-1 text-sm sm:text-base text-gray-600 dark:text-gray-400 hidden sm:block">
          Vue d'ensemble de vos finances
        </p>
      </div>
      <!-- Icon-only on mobile, full button on desktop -->
      <UButton
        icon="i-heroicons-plus"
        size="lg"
        color="primary"
        class="sm:hidden"
        aria-label="Nouvelle transaction"
        @click="showTransactionModal = true"
      />
      <UButton
        icon="i-heroicons-plus"
        size="lg"
        color="primary"
        class="hidden sm:inline-flex"
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
        class="p-4 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
      >
        <div class="flex items-start gap-3">
          <UIcon name="i-heroicons-device-phone-mobile" class="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
          <span class="text-sm text-orange-700 dark:text-orange-400">
            <strong>"{{ alert.payload.label }}"</strong> ({{ formatCurrency(parseFloat(alert.payload.amount)) }}) — catégorie "{{ alert.payload.category_name }}" non trouvée.
          </span>
        </div>
        <div class="flex gap-2 flex-shrink-0 ml-8 sm:ml-0">
          <UButton size="sm" variant="soft" @click="openCorrectionModal(alert)">Corriger</UButton>
          <UButton size="sm" variant="ghost" color="gray" @click="handleDismissAlert(alert.id)">Ignorer</UButton>
        </div>
      </div>
    </div>

    <!-- Loading State: Summary Cards Skeletons -->
    <div v-if="initialLoading" class="grid grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-5 sm:mb-8">
      <SkeletonCard v-for="i in 3" :key="i" :lines="2" :show-header="false" :class="i === 3 ? 'col-span-2 sm:col-span-1' : ''" />
    </div>

    <!-- Summary Cards -->
    <div v-else class="grid grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-5 sm:mb-8">
      <SummaryCard
        icon="i-heroicons-arrow-trending-up"
        icon-color="text-blue-600"
        label="Revenus ce mois"
        :amount="monthlyIncome"
        :future-amount="futureIncome"
        tooltip-text="Solde projeté incluant vos revenus futurs planifiés ce mois"
        future-amount-class="text-blue-600 dark:text-blue-400"
      />
      <SummaryCard
        icon="i-heroicons-arrow-trending-down"
        icon-color="text-red-600"
        label="Dépenses ce mois"
        :amount="monthlyExpenses"
        :future-amount="futureExpenses"
        tooltip-text="Montant projeté incluant vos dépenses futures planifiées ce mois"
        future-amount-class="text-red-600 dark:text-red-400"
      />
      <SummaryCard
        class="col-span-2 sm:col-span-1"
        icon="i-heroicons-chart-bar"
        icon-color="text-purple-600"
        label="Économies"
        :amount="savings"
        :future-amount="futureSavings"
        tooltip-text="Économies projetées incluant vos transactions futures et virements d'épargne planifiés ce mois"
        :future-amount-class="(savings + futureSavings) > 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'"
      />
    </div>

    <!-- Accounts Section -->
    <div class="mb-5 sm:mb-8">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Mes comptes</h2>
        <NuxtLink to="/accounts" class="text-sm text-primary-600 hover:text-primary-500">
          Gérer les comptes
        </NuxtLink>
      </div>

      <!-- Loading State: Account Cards Skeletons -->
      <div v-if="initialLoading" class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <SkeletonCard v-for="i in 4" :key="i" :lines="2" :show-header="false" />
      </div>

      <div v-else class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <UCard v-for="account in accounts" :key="account.id" class="hover:shadow-md transition-shadow cursor-pointer" @click="openTransactionWithAccount(account.id)">
          <div class="space-y-2">
            <div class="flex items-center justify-between gap-1">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white truncate">{{ account.name }}</h3>
              <UBadge :color="account.account_type === 'checking' ? 'blue' : account.account_type === 'savings' ? 'green' : account.account_type === 'credit_card' ? 'orange' : 'gray'" variant="subtle" size="xs" class="flex-shrink-0">
                <span class="hidden sm:inline">{{ account.account_type_display }}</span>
              </UBadge>
            </div>
            <CurrencyAmount :amount="Number(account.current_balance || 0)" compact class="text-lg sm:text-2xl font-bold text-gray-900 dark:text-white" />
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
          <CurrencyAmount :amount="totalBalance" compact class="text-xl sm:text-2xl font-bold text-primary-600 dark:text-primary-400" />
        </div>
      </div>
    </div>

    <!-- Budget vs Réel Section -->
    <div v-if="budgetDashData" class="mb-5 sm:mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Budget vs Réel</h2>
        <div class="flex items-center gap-2">
          <UButton icon="i-heroicons-chevron-left" color="gray" variant="ghost" size="sm" @click="goToPrevMonth" aria-label="Mois précédent" />
          <span class="text-sm font-medium capitalize text-gray-700 dark:text-gray-300 min-w-[110px] text-center">{{ selectedMonthLabel }}</span>
          <UButton icon="i-heroicons-chevron-right" color="gray" variant="ghost" size="sm" :disabled="isCurrentMonth" @click="goToNextMonth" aria-label="Mois suivant" />
        </div>
      </div>
      <div v-if="budgetDashData.categories.length === 0" class="text-sm text-gray-500 dark:text-gray-400 text-center py-8 border border-dashed border-gray-200 dark:border-gray-700 rounded-lg">
        Aucune donnée budgétaire pour ce mois.
      </div>
      <template v-else>

      <!-- Soldes résumé -->
      <div class="grid grid-cols-3 gap-2 sm:gap-4 mb-4">
        <div class="p-3 sm:p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400">Solde prévisionnel</p>
          <CurrencyAmount :amount="budgetDashData.solde_previsionnel" compact class="text-base sm:text-xl font-bold text-blue-600 dark:text-blue-400" />
        </div>
        <div class="p-3 sm:p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400">Solde réel</p>
          <CurrencyAmount :amount="budgetDashData.solde_reel" compact class="text-base sm:text-xl font-bold text-green-600 dark:text-green-400" />
        </div>
        <div :class="[
          'p-3 sm:p-4 rounded-lg border',
          budgetDashData.ecart >= 0
            ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800'
            : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
        ]">
          <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400">Écart</p>
          <p :class="[
            'text-base sm:text-xl font-bold',
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
        <ResponsiveTable :columns="budgetColumns" :rows="budgetDashData.categories">
          <template #cell-category_name="{ row }">
            <div class="flex items-center gap-2 min-w-0">
              <UIcon :name="row.category_icon" class="h-4 w-4 flex-shrink-0" />
              <span class="truncate">{{ row.category_name }}</span>
              <UBadge v-if="row.is_mandatory_savings" color="blue" variant="subtle" size="xs">Épargne</UBadge>
              <UBadge v-else-if="row.unbudgeted" color="gray" variant="subtle" size="xs">Non budgété</UBadge>
            </div>
          </template>
          <template #cell-prevu="{ row }">
            <CurrencyAmount v-if="row.prevu > 0" :amount="row.prevu" class="text-gray-600 dark:text-gray-400" />
            <span v-else class="text-gray-400">-</span>
          </template>
          <template #cell-reel="{ row }">
            <CurrencyAmount :amount="row.reel" :class="row.is_over ? 'text-red-600 font-medium' : 'text-gray-900 dark:text-white font-medium'" />
          </template>
          <template #cell-ecart="{ row }">
            <span :class="['font-medium', row.ecart >= 0 ? 'text-green-600' : 'text-red-600']">
              {{ row.ecart >= 0 ? '+' : '' }}{{ formatCurrency(row.ecart) }}
            </span>
          </template>
        </ResponsiveTable>
      </UCard>
      </template>
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
        <div>
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
          <TransactionRow
            v-for="transaction in recentTransactions"
            :key="transaction.id"
            :transaction="transaction"
          />
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
    <TransactionModal
      v-model="showTransactionModal"
      :accounts="accounts"
      :categories="categories"
      :initial-account="transactionInitialAccount"
      @success="fetchDashboardData"
    />
  </div>
</template>

<script setup lang="ts">
import type { Transaction, PendingAlert, Account, Category } from '~/types';

definePageMeta({
  middleware: 'auth'
});

const { getAccounts } = useAccounts();
const { getTransactions, getStatistics, updateTransaction } = useTransactions();
const { getCategories } = useCategories();
const { getDashboardData: getBudgetDashboardData } = useBudgets();
const { getAlerts, dismissAlert } = useAlerts();
const { registerShortcut, getShortcutLabel } = useKeyboardShortcuts();
const { ensureProfileLoaded } = useUserProfile();
const { formatForToast } = useErrorHandler();
const toast = useToast();

// Keyboard shortcut label for the button
const shortcutLabel = computed(() => getShortcutLabel('n', { ctrl: true }));

// Reactive state
const totalBalance = ref(0);
const accounts = ref<Account[]>([]);
const categories = ref<Category[]>([]);
const monthlyIncome = ref(0);
const monthlyExpenses = ref(0);
const savings = ref(0);
const futureIncome = ref(0);
const futureExpenses = ref(0);
const futureTransfers = ref(0);
const monthlyTransfers = ref(0);
const recentTransactions = ref<Transaction[]>([]);
const showTransactionModal = ref(false);
const transactionInitialAccount = ref<number | string>('');
const initialLoading = ref(true);
const budgetDashData = ref<any>(null);

// Onboarding state
const showOnboarding = ref(false);

// Alerts state
const pendingAlerts = ref<PendingAlert[]>([]);
const showCorrectionModal = ref(false);
const correctionAlert = ref<PendingAlert | null>(null);
const correctionCategory = ref<string | number>('');
const correcting = ref(false);

// Calculate future savings (future income - future expenses - future transfers)
const futureSavings = computed(() => {
  return futureIncome.value - futureExpenses.value - futureTransfers.value;
});

// Budget table columns
const budgetColumns = [
  { key: 'category_name', label: 'Catégorie' },
  { key: 'prevu', label: 'Prévu', class: 'text-right' },
  { key: 'reel', label: 'Réel', class: 'text-right' },
  { key: 'ecart', label: 'Écart', class: 'text-right' },
];

// Month navigation
const selectedMonthDate = ref(new Date());
const selectedYear = computed(() => selectedMonthDate.value.getFullYear());
const selectedMonth = computed(() => selectedMonthDate.value.getMonth() + 1);
const selectedMonthLabel = computed(() =>
  selectedMonthDate.value.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
);
const isCurrentMonth = computed(() => {
  const now = new Date();
  return selectedMonthDate.value.getMonth() === now.getMonth() &&
         selectedMonthDate.value.getFullYear() === now.getFullYear();
});
const goToPrevMonth = async () => {
  const d = new Date(selectedMonthDate.value);
  d.setMonth(d.getMonth() - 1);
  selectedMonthDate.value = d;
  await fetchMonthData();
};
const goToNextMonth = async () => {
  const d = new Date(selectedMonthDate.value);
  d.setMonth(d.getMonth() + 1);
  selectedMonthDate.value = d;
  await fetchMonthData();
};

// Get selected month date range
const getCurrentMonthRange = () => {
  const year = selectedYear.value;
  const month = selectedMonth.value;
  const startOfMonth = new Date(year, month - 1, 1);
  const endOfMonth = new Date(year, month, 0);

  const formatDate = (date: Date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  return {
    start_date: formatDate(startOfMonth),
    end_date: formatDate(endOfMonth)
  };
};

// Fetch data for the selected month only
const fetchMonthData = async () => {
  const monthRange = getCurrentMonthRange();
  const statsResponse = await getStatistics(monthRange);
  if (statsResponse.success && statsResponse.data) {
    monthlyIncome.value = statsResponse.data.income.total;
    monthlyExpenses.value = statsResponse.data.expense.total;
    monthlyTransfers.value = statsResponse.data.transfer.total || 0;
    savings.value = statsResponse.data.net - monthlyTransfers.value;
    futureIncome.value = statsResponse.data.income.future || 0;
    futureExpenses.value = statsResponse.data.expense.future || 0;
    futureTransfers.value = statsResponse.data.transfer.future || 0;
  }

  const budgetDashResult = await getBudgetDashboardData({ year: selectedYear.value, month: selectedMonth.value });
  if (budgetDashResult.success && budgetDashResult.data) {
    budgetDashData.value = budgetDashResult.data;
  }
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
    category: parseInt(String(correctionCategory.value))
  });

  if (result.success) {
    await dismissAlert(correctionAlert.value.id);
    pendingAlerts.value = pendingAlerts.value.filter(a => a.id !== correctionAlert.value!.id);
    showCorrectionModal.value = false;
    toast.add({ title: 'Corrigé', description: 'Catégorie mise à jour', color: 'green' });
    await fetchDashboardData();
  } else if (result.error) {
    const errorMessage = formatForToast(result.error);
    toast.add({ title: 'Erreur', description: errorMessage, color: 'red' });
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
        return sum + Number(account.current_balance || 0);
      }, 0);
    }

    // Fetch categories
    const categoriesResponse = await getCategories({ is_active: true });
    if (categoriesResponse.success && categoriesResponse.data) {
      categories.value = categoriesResponse.data.results;
    }

    // Check if first time user (no accounts and no categories)
    if (import.meta.client && accounts.value.length === 0 && categories.value.length === 0) {
      const hasCompletedOnboarding = localStorage.getItem('onboarding_completed');
      if (!hasCompletedOnboarding) {
        showOnboarding.value = true;
      }
    }

    // Fetch recent transactions (past only, limit to 5)
    const today = new Date().toISOString().split('T')[0];
    const transactionsResponse = await getTransactions({ ordering: '-date', end_date: today });
    if (transactionsResponse.success && transactionsResponse.data) {
      recentTransactions.value = transactionsResponse.data.results.slice(0, 5);
    }

    await fetchMonthData();
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
  } finally {
    initialLoading.value = false;
  }
};

// Open transaction modal with pre-selected account
const openTransactionWithAccount = (accountId: number) => {
  transactionInitialAccount.value = accountId;
  showTransactionModal.value = true;
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
onMounted(async () => {
  await ensureProfileLoaded();
  await Promise.all([fetchDashboardData(), fetchAlerts()]);

  // Register keyboard shortcut: Ctrl+N or Cmd+N for new transaction
  registerShortcut('n', () => {
    showTransactionModal.value = true;
  }, {
    modifiers: { ctrl: true },
    description: 'Créer une nouvelle transaction'
  });
});
</script>
