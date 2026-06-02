<template>
  <div class="page-root fade-up">

    <!-- ── Page header ─────────────────────────────────────── -->
    <PageHeader title="Comptes" subtitle="Vue d'ensemble de votre patrimoine sur tous vos comptes.">
      <template #actions>
        <button class="ds-btn ds-btn-secondary" style="height:36px;padding:0 14px;font-size:13px;" @click="openAddModal">
          <UIcon name="i-heroicons-plus" style="width:14px;height:14px;" />
          <span class="hidden sm:inline">Nouveau compte</span>
        </button>
      </template>
    </PageHeader>

    <!-- ── Loading ─────────────────────────────────────────── -->
    <div v-if="loading" class="accounts-grid">
      <div v-for="i in 3" :key="i" class="account-card-skeleton">
        <div class="skeleton-block" style="height:200px;" />
      </div>
    </div>

    <!-- ── Error ───────────────────────────────────────────── -->
    <div v-else-if="loadError" class="section-card">
      <EmptyState
        icon="i-heroicons-exclamation-circle"
        color="red"
        title="Impossible de charger les comptes"
        description="Vérifiez votre connexion et réessayez."
        button-text="Réessayer"
        button-icon="i-heroicons-arrow-path"
        @action="fetchAccounts(); fetchSummary()"
      />
    </div>

    <!-- ── Main content ───────────────────────────────────── -->
    <template v-else>

      <!-- Net Worth Hero -->
      <NetWorthHero
        v-if="accounts.length > 0"
        :accounts="accounts"
        :net-worth-history="netWorthHistory"
        :is-loading-history="isLoadingHistory"
      />

      <!-- Accounts grid -->
      <div class="accounts-grid">
        <button
          v-for="account in accounts"
          :key="account.id"
          class="account-card-btn"
          :class="{ 'account-card-btn--selected': selectedAccountId === account.id }"
          :style="selectedAccountId === account.id
            ? { border: `1px solid ${accountColor(account.account_type)}`, boxShadow: `0 0 0 3px color-mix(in oklab, ${accountColor(account.account_type)} 18%, transparent), var(--shadow-md)` }
            : {}"
          @click="handleCardClick(account.id)"
        >
          <!-- Top accent stripe -->
          <div class="account-card-stripe" :style="{ background: accountColor(account.account_type), opacity: selectedAccountId === account.id ? '1' : '0.7' }" />

          <!-- Header -->
          <div class="account-card-header">
            <div class="account-card-icon" :style="{ background: `color-mix(in oklab, ${accountColor(account.account_type)} 12%, var(--surface))`, color: accountColor(account.account_type), border: `1px solid color-mix(in oklab, ${accountColor(account.account_type)} 20%, transparent)` }">
              <UIcon :name="accountIcon(account.account_type)" style="width:18px;height:18px;" />
            </div>
            <div style="flex:1;min-width:0;">
              <div class="account-name">{{ account.name }}</div>
              <div class="account-type">{{ account.account_type_display }}</div>
            </div>
            <span v-if="selectedAccountId === account.id" class="account-badge-active" :style="{ background: accountColor(account.account_type) }">Actif</span>
            <span v-else class="account-badge" :class="account.is_active ? 'account-badge--active' : 'account-badge--inactive'">
              {{ account.is_active ? 'Actif' : 'Inactif' }}
            </span>
          </div>

          <!-- Balance -->
          <div>
            <div class="account-balance mono">{{ formatCurrencyDisplay(parseFloat(account.current_balance || account.balance), account.currency) }}</div>
            <div class="account-balance-label">Solde actuel</div>
          </div>

          <!-- Projected balance -->
          <div v-if="account.projected_balance && parseFloat(account.projected_balance) !== parseFloat(account.current_balance || account.balance)" class="account-projected">
            <span class="account-projected-label">Solde projeté</span>
            <span class="account-projected-amount mono">{{ formatCurrencyDisplay(parseFloat(account.projected_balance), account.currency) }}</span>
          </div>

          <!-- Sparkline placeholder -->
          <div style="margin-top:auto;padding-top:8px;">
            <svg width="100%" height="36" viewBox="0 0 260 36" style="display:block;opacity:0.5;">
              <line x1="0" y1="18" x2="260" y2="18" stroke="var(--line)" stroke-width="1" />
            </svg>
          </div>
        </button>

        <!-- Add account tile -->
        <button class="account-add-tile" @click="openAddModal">
          <div class="account-add-icon">
            <UIcon name="i-heroicons-plus" style="width:22px;height:22px;" />
          </div>
          <div class="account-add-label">Ajouter un compte</div>
          <div class="account-add-hint">Courant, épargne, carte de crédit…</div>
        </button>

        <!-- Empty state -->
        <div v-if="accounts.length === 0" class="section-card" style="grid-column:1/-1;">
          <EmptyState
            icon="i-heroicons-banknotes"
            color="blue"
            title="Créez votre premier compte"
            description="Ajoutez votre compte courant, épargne ou carte de crédit pour commencer à suivre vos finances."
            button-text="Créer un compte"
            @action="openAddModal"
          />
        </div>
      </div>

      <!-- Account Detail Panel -->
      <AccountDetailPanel
        v-if="selectedAccount"
        :account="selectedAccount"
        :transactions="detailTransactions"
        :balance-history="accountBalanceHistory"
        :is-loading="isLoadingDetail"
        :current-year="currentYear"
        :current-month="currentMonth"
        @edit="openEditModal(selectedAccount)"
        @toggle-active="toggleActive(selectedAccount)"
        @delete="confirmDelete(selectedAccount)"
      />

    </template>

    <!-- ── Confirm delete ──────────────────────────────────── -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer le compte"
      :message="`Êtes-vous sûr de vouloir supprimer le compte « ${accountToDelete?.name} » ?`"
      confirm-label="Supprimer"
      @confirm="executeDelete"
    />

    <!-- ── Add / Edit modal ────────────────────────────────── -->
    <UModal
      v-model="showModal"
      :ui="{
        width: 'w-full sm:max-w-lg',
        container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
        base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
        padding: 'p-0', background: '', ring: '', shadow: '',
      }"
    >
      <div class="modal-panel">
        <div class="modal-handle" aria-hidden />
        <div class="modal-header">
          <div class="modal-header-icon">
            <UIcon :name="editingAccount ? 'i-heroicons-pencil' : 'i-heroicons-building-library'" style="width:16px;height:16px;" />
          </div>
          <h3 class="modal-title">{{ editingAccount ? 'Modifier' : 'Ajouter' }} un compte</h3>
          <button class="modal-close" type="button" @click="showModal = false">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="handleSubmit">

          <!-- Nom -->
          <div class="field-group">
            <label class="field-label">Nom du compte <span class="field-required">*</span></label>
            <div class="field-wrap" :class="{ 'field-error': getErrorForField(formErrors, 'name') }">
              <UIcon name="i-heroicons-building-library" class="field-icon" />
              <input v-model="form.name" type="text" placeholder="Ex: Compte courant principal" class="field-input" required />
            </div>
            <p v-if="getErrorForField(formErrors, 'name')" class="field-err">{{ getErrorForField(formErrors, 'name') }}</p>
          </div>

          <!-- Type -->
          <div class="field-group">
            <label class="field-label">Type de compte <span class="field-required">*</span></label>
            <USelectMenu v-model="form.account_type" :options="accountTypes" value-attribute="value" option-attribute="label" size="lg" />
            <p v-if="getErrorForField(formErrors, 'account_type')" class="field-err">{{ getErrorForField(formErrors, 'account_type') }}</p>
          </div>

          <!-- Solde -->
          <div class="field-group">
            <label class="field-label">{{ editingAccount ? 'Solde actuel' : 'Solde initial' }} <span class="field-required">*</span></label>
            <div class="field-wrap" :class="{ 'field-error': getErrorForField(formErrors, 'balance') }">
              <UIcon name="i-heroicons-banknotes" class="field-icon" />
              <input v-model="form.balance" type="number" step="0.01" placeholder="0.00" class="field-input" inputmode="decimal" required />
            </div>
            <p style="font-size:12px;color:var(--ink-3);">
              {{ editingAccount ? "Modifiez le solde pour créer automatiquement une transaction d'ajustement." : 'Le solde initial de votre compte.' }}
            </p>
            <p v-if="getErrorForField(formErrors, 'balance')" class="field-err">{{ getErrorForField(formErrors, 'balance') }}</p>
          </div>

          <!-- Devise -->
          <div class="field-group">
            <label class="field-label">Devise <span class="field-required">*</span></label>
            <USelectMenu v-model="form.currency" :options="currencies" size="lg" />
            <p v-if="getErrorForField(formErrors, 'currency')" class="field-err">{{ getErrorForField(formErrors, 'currency') }}</p>
          </div>

          <!-- Description -->
          <div class="field-group">
            <label class="field-label">Description</label>
            <div class="field-wrap field-wrap--textarea">
              <textarea v-model="form.description" placeholder="Description optionnelle" class="field-input field-input--textarea" rows="3" />
            </div>
          </div>

          <p v-if="error" style="font-size:13px;color:var(--danger);margin:0;">{{ error }}</p>

          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button type="button" class="ds-btn ds-btn-ghost" @click="showModal = false">Annuler</button>
            <button type="submit" class="ds-btn ds-btn-primary" :disabled="submitting">
              <span v-if="submitting" class="btn-spinner" />
              <span v-else>{{ editingAccount ? 'Modifier' : 'Créer' }}</span>
            </button>
          </div>
        </form>
      </div>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { Account, AccountSummary, Transaction } from '~/types';
import type { StandardError } from '~/types/errors';

definePageMeta({ middleware: 'auth' });

/* ─── Composables ─────────────────────────────────────────── */
const { getAccounts, createAccount, updateAccount, deleteAccount: apiDeleteAccount, getAccountsSummary, toggleAccountActive } = useAccounts();
const { getTransactions, getMonthlySummary } = useTransactions();
const { getErrorForField, formatForToast } = useErrorHandler();
const { ensureProfileLoaded } = useUserProfile();
const toast = useToast();

/* ─── Date helpers ─────────────────────────────────────────── */
const now = new Date();
const currentYear = now.getFullYear();
const currentMonth = now.getMonth() + 1; // 1-based

/* ─── State ────────────────────────────────────────────────── */
const accounts = ref<Account[]>([]);
const summary = ref<AccountSummary | null>(null);
const loading = ref(false);
const loadError = ref(false);
const showModal = ref(false);
const submitting = ref(false);
const error = ref('');
const formErrors = ref<StandardError | null>(null);
const editingAccount = ref<Account | null>(null);
const showConfirmDelete = ref(false);
const accountToDelete = ref<Account | null>(null);

// Selected account & detail state
const selectedAccountId = ref<number | null>(null);
const detailTransactions = ref<Transaction[]>([]);
const accountBalanceHistory = ref<number[]>([]);
const isLoadingDetail = ref(false);

// Net worth history (12 months)
const netWorthHistory = ref<number[]>([]);
const isLoadingHistory = ref(false);

const form = ref({ name: '', account_type: 'checking', balance: '0.00', currency: 'CHF', description: '' });

/* ─── Lookups ──────────────────────────────────────────────── */
const accountTypes = [
  { value: 'checking',    label: 'Compte Courant' },
  { value: 'savings',     label: 'Compte Épargne' },
  { value: 'credit_card', label: 'Carte de Crédit' },
  { value: 'cash',        label: 'Espèces' },
  { value: 'investment',  label: 'Investissement' },
  { value: 'loan',        label: 'Prêt' },
  { value: 'other',       label: 'Autre' },
];
const currencies = ['CHF', 'EUR', 'USD', 'GBP'];

/* ─── Computed ─────────────────────────────────────────────── */
const selectedAccount = computed(() =>
  accounts.value.find(a => a.id === selectedAccountId.value) ?? null
);

/* ─── Formatters ───────────────────────────────────────────── */
/**
 * Format amount as "CHF 14'820" (fr-CH locale, 0 decimals).
 */
const formatCurrencyDisplay = (amount: number, currency = 'CHF'): string => {
  return new Intl.NumberFormat('fr-CH', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
  }).format(amount);
};

/**
 * Compact format: 14820 → "14.8k", 850 → "850"
 */
const fmtShort = (n: number): string => {
  if (Math.abs(n) >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(Math.round(n));
};

/* ─── Account type helpers ─────────────────────────────────── */
const accountColor = (type: string): string => ({
  checking:    '#2563eb',
  savings:     '#16a34a',
  credit_card: '#ea580c',
  cash:        '#64748b',
  investment:  '#7c3aed',
  loan:        '#dc2626',
  other:       '#64748b',
}[type] ?? '#64748b');

const accountIcon = (type: string): string => ({
  checking:    'i-heroicons-building-library',
  savings:     'i-heroicons-banknotes',
  credit_card: 'i-heroicons-credit-card',
  cash:        'i-heroicons-banknotes',
  investment:  'i-heroicons-arrow-trending-up',
  loan:        'i-heroicons-document-text',
  other:       'i-heroicons-wallet',
}[type] ?? 'i-heroicons-wallet');

/* ─── Net worth history ────────────────────────────────────── */
/**
 * Build 12-month net-worth history by reconstructing backwards from
 * current total balance using the monthly net income/expense data.
 * history[11] = current month (most recent)
 * history[0]  = 11 months ago
 */
const buildNetWorthHistory = (
  currentTotal: number,
  monthlySummary: Record<number, { month: number; income: number; expense: number; net: number }>
): number[] => {
  const history = new Array(12).fill(0);
  history[11] = currentTotal;
  // Reconstruct backwards: balance at month i-1 = balance at month i - net[i]
  for (let i = 11; i >= 1; i--) {
    const monthIndex = currentMonth - (11 - i); // actual month number
    const adjustedMonth = ((monthIndex - 1 + 12) % 12) + 1;
    const monthData = Object.values(monthlySummary).find(m => m.month === adjustedMonth);
    const net = monthData?.net ?? 0;
    history[i - 1] = history[i] - net;
  }
  return history;
};

/**
 * Build per-account 12-month balance history from transactions,
 * reconstructing backwards from current_balance.
 */
const buildAccountBalanceHistory = (
  currentBalance: number,
  transactions: Transaction[],
  year: number,
  month: number
): number[] => {
  const history = new Array(12).fill(0);
  history[11] = currentBalance;

  for (let i = 11; i >= 1; i--) {
    // Month for position i: (11 - i) months before current
    let m = month - (11 - i);
    let y = year;
    while (m <= 0) { m += 12; y--; }
    const isoPrefix = `${y}-${String(m).padStart(2, '0')}`;

    // Sum of net amounts for transactions in this month
    const monthNet = transactions
      .filter(t => t.date.startsWith(isoPrefix))
      .reduce((sum, t) => {
        const amt = parseFloat(t.amount);
        if (t.type === 'income') return sum + amt;
        if (t.type === 'expense') return sum - amt;
        // For transfers: positive if destination, negative if source (amount is always positive)
        return sum; // skip transfers to avoid double counting
      }, 0);

    history[i - 1] = history[i] - monthNet;
  }
  return history;
};

/* ─── Data fetching ────────────────────────────────────────── */
const fetchAccounts = async () => {
  loading.value = true;
  loadError.value = false;
  const result = await getAccounts();
  if (result.success && result.data) {
    accounts.value = result.data.results;
  } else {
    loadError.value = true;
  }
  loading.value = false;
};

const fetchSummary = async () => {
  const result = await getAccountsSummary();
  if (result.success && result.data) summary.value = result.data;
};

const fetchNetWorthHistory = async () => {
  isLoadingHistory.value = true;
  const result = await getMonthlySummary(currentYear);
  if (result.success && result.data && accounts.value.length > 0) {
    const totalBalance = accounts.value.reduce((sum, a) => sum + parseFloat(a.current_balance || a.balance), 0);
    netWorthHistory.value = buildNetWorthHistory(totalBalance, result.data);
  }
  isLoadingHistory.value = false;
};

const fetchAccountDetail = async (accountId: number) => {
  isLoadingDetail.value = true;
  detailTransactions.value = [];
  accountBalanceHistory.value = [];

  // Fetch last 12 months of transactions
  const twelveMonthsAgo = new Date(now);
  twelveMonthsAgo.setMonth(twelveMonthsAgo.getMonth() - 11);
  twelveMonthsAgo.setDate(1);
  const startDate = twelveMonthsAgo.toISOString().slice(0, 10);

  const result = await getTransactions({
    account: accountId,
    ordering: '-date',
    start_date: startDate,
    page_size: 500,
  });

  if (result.success && result.data) {
    detailTransactions.value = result.data.results;
    const account = accounts.value.find(a => a.id === accountId);
    if (account) {
      const balance = parseFloat(account.current_balance || account.balance);
      accountBalanceHistory.value = buildAccountBalanceHistory(balance, result.data.results, currentYear, currentMonth);
    }
  }

  isLoadingDetail.value = false;
};

/* ─── Card click handler ───────────────────────────────────── */
const handleCardClick = async (accountId: number) => {
  if (selectedAccountId.value === accountId) {
    // Toggle off
    selectedAccountId.value = null;
    return;
  }
  selectedAccountId.value = accountId;
  await fetchAccountDetail(accountId);
};

/* ─── CRUD ─────────────────────────────────────────────────── */
const openAddModal = () => {
  editingAccount.value = null;
  form.value = { name: '', account_type: 'checking', balance: '0.00', currency: 'CHF', description: '' };
  error.value = '';
  formErrors.value = null;
  showModal.value = true;
};

const openEditModal = (account: Account) => {
  editingAccount.value = account;
  form.value = {
    name: account.name,
    account_type: account.account_type,
    balance: (account.current_balance || account.balance).toString(),
    currency: account.currency,
    description: account.description || '',
  };
  error.value = '';
  formErrors.value = null;
  showModal.value = true;
};

const handleSubmit = async () => {
  submitting.value = true;
  error.value = '';
  formErrors.value = null;
  try {
    const result = editingAccount.value
      ? await updateAccount(editingAccount.value.id, form.value)
      : await createAccount(form.value);
    if (result.success) {
      toast.add({ title: 'Succès', description: editingAccount.value ? 'Compte modifié' : 'Compte créé', color: 'green' });
      showModal.value = false;
      await Promise.all([fetchAccounts(), fetchSummary()]);
      // Refresh detail if the edited account is selected
      if (editingAccount.value && selectedAccountId.value === editingAccount.value.id) {
        await fetchAccountDetail(editingAccount.value.id);
      }
    } else if (result.error) {
      formErrors.value = result.error;
      error.value = formatForToast(result.error);
      toast.add({ title: 'Erreur', description: error.value, color: 'red' });
    }
  } catch {
    error.value = 'Une erreur inattendue est survenue';
  } finally {
    submitting.value = false;
  }
};

const toggleActive = async (account: Account) => {
  const result = await toggleAccountActive(account.id);
  if (result.success) {
    toast.add({ title: 'Succès', description: `Compte ${result.data?.is_active ? 'activé' : 'désactivé'}`, color: 'green' });
    await Promise.all([fetchAccounts(), fetchSummary()]);
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de modifier le statut', color: 'red' });
  }
};

const confirmDelete = (account: Account) => {
  accountToDelete.value = account;
  showConfirmDelete.value = true;
};

const executeDelete = () => {
  if (accountToDelete.value) {
    const id = accountToDelete.value.id;
    if (selectedAccountId.value === id) selectedAccountId.value = null;
    deleteAccountHandler(id);
    accountToDelete.value = null;
  }
};

const deleteAccountHandler = async (id: number) => {
  const result = await apiDeleteAccount(id);
  if (result.success) {
    toast.add({ title: 'Succès', description: 'Compte supprimé', color: 'green' });
    await Promise.all([fetchAccounts(), fetchSummary()]);
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de supprimer le compte', color: 'red' });
  }
};

/* ─── Lifecycle ────────────────────────────────────────────── */
onMounted(async () => {
  await ensureProfileLoaded();
  await Promise.all([fetchAccounts(), fetchSummary()]);
  await fetchNetWorthHistory();
  // Auto-select first account
  if (accounts.value.length > 0) {
    selectedAccountId.value = accounts.value[0].id;
    await fetchAccountDetail(accounts.value[0].id);
  }
});

/* ─── Provide helpers to child components ─────────────────── */
provide('formatCurrencyDisplay', formatCurrencyDisplay);
provide('fmtShort', fmtShort);
provide('accountColor', accountColor);
provide('accountIcon', accountIcon);
provide('openEditModal', openEditModal);
provide('confirmDelete', confirmDelete);
provide('toggleActive', toggleActive);
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp .4s cubic-bezier(.2,.7,.2,1) both; }

/* ── Root ── */
.page-root {
  padding: 20px 24px 48px;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
@media (min-width: 1024px) { .page-root { padding: 20px 32px 48px; } }

/* ── Accounts grid ── */
.accounts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}
@media (min-width: 640px)  { .accounts-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .accounts-grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1280px) { .accounts-grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); } }

/* ── Account card button ── */
.account-card-btn {
  text-align: left;
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.18s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-family: inherit;
  min-height: 200px;
}
.account-card-btn:hover:not(.account-card-btn--selected) {
  border-color: var(--line-strong);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.account-card-stripe {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  transition: opacity 0.18s ease;
}

.account-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}
.account-card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.account-name { font-size: 14px; font-weight: 600; color: var(--ink); letter-spacing: -0.2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.account-type { font-size: 11.5px; color: var(--ink-3); margin-top: 1px; }

.account-badge {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 500;
  flex-shrink: 0;
}
.account-badge--active   { background: color-mix(in oklab, #16a34a 12%, transparent); color: #16a34a; border: 1px solid color-mix(in oklab, #16a34a 25%, transparent); }
.account-badge--inactive { background: var(--surface-2); color: var(--ink-4); border: 1px solid var(--line); }

.account-badge-active {
  padding: 3px 8px;
  height: 18px;
  line-height: 12px;
  color: #fff;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.4px;
  text-transform: uppercase;
  flex-shrink: 0;
}

.account-balance {
  font-size: 26px;
  font-weight: 500;
  color: var(--ink);
  letter-spacing: -0.8px;
  line-height: 1;
}
.account-balance-label {
  font-size: 11.5px;
  color: var(--ink-3);
  margin-top: 2px;
}

.account-projected {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--accent-soft);
  border: 1px solid color-mix(in oklab, var(--accent) 20%, transparent);
  border-radius: 8px;
}
.account-projected-label  { font-size: 12px; color: var(--accent); }
.account-projected-amount { font-size: 14px; font-weight: 500; color: var(--accent); }

/* ── Add tile ── */
.account-add-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px;
  background: transparent;
  border: 2px dashed var(--line-strong);
  border-radius: 14px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s, color 0.15s;
  font-family: inherit;
  color: var(--ink-3);
  min-height: 200px;
}
.account-add-tile:hover {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: var(--accent);
}
.account-add-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--surface-2);
  display: grid;
  place-items: center;
  transition: background 0.15s;
}
.account-add-tile:hover .account-add-icon {
  background: color-mix(in oklab, var(--accent) 15%, transparent);
}
.account-add-label { font-size: 13.5px; font-weight: 500; }
.account-add-hint  { font-size: 11.5px; opacity: .7; }

/* ── Section card ── */
.section-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 20px 24px;
}

/* ── Skeletons ── */
.account-card-skeleton {
  border-radius: 14px;
  overflow: hidden;
}
.skeleton-block {
  background: var(--surface-2);
  border-radius: 8px;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: .45; }
}
</style>
