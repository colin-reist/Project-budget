<template>
  <div class="dash-root fade-up">

    <!-- ── Page header ─────────────────────────────────────── -->
    <PageHeader
      :title="`Bonjour${user?.first_name ? ` ${user.first_name}` : ''} 👋`"
      :subtitle="`Situation financière pour ${selectedMonthLabel}`"
    >
      <template #actions>
        <MonthNavigation
          :model-value="{ year: selectedYear, month: selectedMonth }"
          @update:model-value="onMonthChange"
        />
        <button class="ds-btn ds-btn-primary" @click="showTransactionModal = true">
          <UIcon name="i-heroicons-plus" style="width:15px;height:15px;" />
          <span class="hidden sm:inline">Nouvelle transaction</span>
        </button>
      </template>
    </PageHeader>

    <!-- ── Alerts banner ───────────────────────────────────── -->
    <div v-if="pendingAlerts.length > 0" class="alerts-wrap">
      <div
        v-for="alert in pendingAlerts"
        :key="alert.id"
        class="alert-row"
      >
        <div class="alert-row-left">
          <UIcon name="i-heroicons-device-phone-mobile" style="width:16px;height:16px;color:#f59e0b;flex-shrink:0;" />
          <span style="font-size:13px;">
            <strong>"{{ alert.payload.label }}"</strong> ({{ formatCurrency(parseFloat(alert.payload.amount)) }}) — catégorie "{{ alert.payload.category_name }}" non trouvée.
          </span>
        </div>
        <div class="alert-row-right">
          <button class="ds-btn ds-btn-secondary" style="height:30px;font-size:12px;" @click="openCorrectionModal(alert)">Corriger</button>
          <button class="ds-btn ds-btn-ghost" style="height:30px;font-size:12px;" @click="handleDismissAlert(alert.id)">Ignorer</button>
        </div>
      </div>
    </div>

    <!-- ── 3 hero stat cards ────────────────────────────────── -->
    <div class="hero-grid">

      <!-- Solde total -->
      <div class="stat-card stat-card--hero">
        <div class="stat-label">
          <UIcon name="i-heroicons-wallet" style="width:14px;height:14px;color:var(--ink-4);" />
          Solde total · tous comptes
        </div>
        <div class="stat-amount-row">
          <span class="stat-amount mono">
            {{ formatCurrencyDisplay(totalBalance) }}
          </span>
          <span v-if="!initialLoading" class="stat-trend" :class="monthlyIncome - monthlyExpenses >= 0 ? 'stat-trend--up' : 'stat-trend--down'">
            <UIcon :name="monthlyIncome - monthlyExpenses >= 0 ? 'i-heroicons-arrow-trending-up' : 'i-heroicons-arrow-trending-down'" style="width:12px;height:12px;" />
            {{ monthlyIncome - monthlyExpenses >= 0 ? '+' : '' }}{{ formatCurrencyDisplay(monthlyIncome - monthlyExpenses) }}
          </span>
        </div>
        <div class="stat-sub">Solde net ce mois</div>

        <!-- Accounts list -->
        <div v-if="accounts.length > 0" class="accounts-pills">
          <div class="accounts-pills-label">Comptes</div>
          <div class="accounts-pills-list">
            <div v-for="account in accounts" :key="account.id" class="account-pill" @click="openTransactionWithAccount(account.id)">
              <div class="account-pill-icon">
                <UIcon name="i-heroicons-building-library" style="width:13px;height:13px;" />
              </div>
              <div>
                <div class="account-pill-name">{{ account.name }}</div>
                <div class="account-pill-balance mono">{{ formatCurrencyDisplay(Number(account.current_balance || 0)) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Skeleton -->
        <div v-if="initialLoading" class="skeleton-block" style="height:80px;margin-top:18px;" />
      </div>

      <!-- Argent à assigner -->
      <div class="stat-card" :class="toAssign > 0 ? 'stat-card--accent' : ''">
        <div class="stat-label">
          <UIcon name="i-heroicons-envelope-open" style="width:14px;height:14px;color:var(--ink-4);" />
          Argent à assigner
        </div>
        <div v-if="initialLoading" class="skeleton-block" style="height:48px;margin-top:8px;" />
        <template v-else>
          <div class="mono" style="font-size:38px;font-weight:500;letter-spacing:-1.2px;line-height:1.05;margin-top:8px;"
               :style="{ color: toAssign > 0 ? 'var(--accent)' : 'var(--ink-3)' }">
            {{ formatCurrencyDisplay(toAssign) }}
          </div>
          <div style="font-size:13px;color:var(--ink-3);margin-top:6px;line-height:1.5;">
            {{ toAssign > 0 ? 'Distribuez ce solde dans vos budgets avant la fin du mois.' : 'Tout est assigné. Bravo !' }}
          </div>
          <button class="ds-btn ds-btn-primary" style="margin-top:16px;" @click="navigateTo('/budgets')">
            <UIcon name="i-heroicons-plus" style="width:14px;height:14px;" />
            Gérer les budgets
          </button>
        </template>
      </div>

      <!-- Progression du mois -->
      <div class="stat-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
          <span style="font-size:13px;font-weight:500;color:var(--ink-2);">{{ selectedMonthLabel }}</span>
          <span style="font-size:11px;color:var(--ink-3);">{{ currentDay }} / {{ daysInMonth }}j</span>
        </div>

        <div v-if="initialLoading">
          <div class="skeleton-block" style="height:8px;" />
          <div class="skeleton-block" style="height:36px;margin-top:12px;" />
        </div>
        <template v-else>
          <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px;">
            <span style="font-size:12px;color:var(--ink-3);">Dépensé / budgété</span>
            <span class="mono" style="font-size:13px;font-weight:500;color:var(--ink);">
              {{ formatCurrencyDisplay(monthlyExpenses) }} / {{ formatCurrencyDisplay(totalBudget) }}
            </span>
          </div>

          <!-- Progress bar -->
          <div style="position:relative;height:8px;background:var(--surface-2);border-radius:999px;overflow:hidden;">
            <div
              :style="{
                width: Math.min(100, totalBudget > 0 ? (monthlyExpenses / totalBudget) * 100 : 0) + '%',
                background: spendPct > dayPct + 8
                  ? 'linear-gradient(90deg, #f59e0b, var(--danger))'
                  : 'linear-gradient(90deg, var(--accent), color-mix(in oklab, var(--accent) 70%, #60a5fa))',
              }"
              style="position:absolute;inset:0;border-radius:999px;transition:width .4s ease;"
            />
            <div
              :style="{ left: dayPct + '%' }"
              style="position:absolute;top:-2px;bottom:-2px;width:2px;background:var(--ink);opacity:.4;border-radius:1px;"
              title="Avancement du mois"
            />
          </div>

          <div style="font-size:11px;color:var(--ink-3);margin-top:6px;line-height:1.4;">
            {{ spendPct > dayPct + 8
              ? `Avance rapide (${spendPct.toFixed(0)}% vs ${dayPct.toFixed(0)}% du mois)`
              : `Au rythme idéal — ${spendPct.toFixed(0)}% dépensé pour ${dayPct.toFixed(0)}% du mois` }}
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px;padding-top:16px;border-top:1px solid var(--line);">
            <div>
              <div style="font-size:11px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.5px;">Revenus</div>
              <div class="mono" style="font-size:18px;font-weight:500;color:var(--success);margin-top:2px;">
                +{{ formatCurrencyDisplay(monthlyIncome) }}
              </div>
            </div>
            <div>
              <div style="font-size:11px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.5px;">Dépenses</div>
              <div class="mono" style="font-size:18px;font-weight:500;color:var(--ink);margin-top:2px;">
                −{{ formatCurrencyDisplay(monthlyExpenses) }}
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- ── Enveloppes ────────────────────────────────────────── -->
    <div v-if="budgetDashData && budgetDashData.categories.length > 0" class="section-card">
      <div class="section-header">
        <div>
          <div class="section-title">Enveloppes</div>
          <div class="section-sub">{{ budgetDashData.categories.length }} enveloppes · {{ selectedMonthLabel }}</div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <span class="ds-badge" :class="budgetDashData.ecart >= 0 ? 'ds-badge-success' : 'ds-badge-danger'">
            {{ budgetDashData.ecart >= 0 ? '+' : '' }}{{ formatCurrency(budgetDashData.ecart) }}
          </span>
          <NuxtLink to="/budgets" style="font-size:13px;color:var(--accent);text-decoration:none;display:inline-flex;align-items:center;gap:4px;">
            Voir tout
            <UIcon name="i-heroicons-chevron-right" style="width:12px;height:12px;" />
          </NuxtLink>
        </div>
      </div>

      <div class="envelopes-grid">
        <NuxtLink
          v-for="cat in budgetDashData.categories"
          :key="cat.category_id ?? cat.category_name"
          to="/budgets"
          class="envelope-card"
        >
          <!-- Icon + name + over badge -->
          <div style="display:flex;align-items:center;gap:10px;justify-content:space-between;">
            <div style="display:flex;align-items:center;gap:10px;min-width:0;">
              <span
                class="envelope-icon"
                :style="{
                  background: `color-mix(in oklab, ${cat.category_color || 'var(--accent)'} 12%, var(--surface))`,
                  color: cat.category_color || 'var(--accent)',
                  border: `1px solid color-mix(in oklab, ${cat.category_color || 'var(--accent)'} 20%, transparent)`,
                }"
              >
                <UIcon :name="cat.category_icon || 'i-heroicons-tag'" style="width:15px;height:15px;" />
              </span>
              <span class="envelope-name">{{ cat.category_name }}</span>
            </div>
            <span v-if="cat.is_over" class="envelope-over-badge">
              +{{ formatCurrency(cat.reel - cat.prevu) }}
            </span>
          </div>

          <!-- Amounts + progress bar -->
          <div>
            <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:6px;">
              <span class="mono" style="font-size:17px;font-weight:500;color:var(--ink);">
                {{ formatCurrencyDisplay(cat.reel) }}
              </span>
              <span class="mono" style="font-size:11.5px;color:var(--ink-3);">
                / {{ formatCurrencyDisplay(cat.prevu) }}
              </span>
            </div>
            <div style="position:relative;height:5px;background:var(--surface-2);border-radius:999px;overflow:hidden;">
              <div
                :style="{
                  width: Math.min(100, cat.prevu > 0 ? (cat.reel / cat.prevu) * 100 : 0) + '%',
                  background: cat.is_over
                    ? 'linear-gradient(90deg, #f59e0b, var(--danger))'
                    : (cat.category_color || 'var(--accent)'),
                }"
                style="position:absolute;inset:0;border-radius:999px;transition:width .4s ease;"
              />
            </div>
          </div>

          <!-- Remaining -->
          <div style="display:flex;justify-content:space-between;font-size:11.5px;color:var(--ink-3);">
            <span>{{ cat.is_over ? 'Dépassement' : 'Restant' }}</span>
            <span class="mono" :style="{ color: cat.is_over ? 'var(--danger)' : 'var(--ink-2)', fontWeight: 500 }">
              {{ formatCurrencyDisplay(Math.abs(cat.ecart)) }}
            </span>
          </div>
        </NuxtLink>
      </div>
    </div>

    <!-- ── Bottom 2-col: Évolution + Transactions ───────────── -->
    <div class="bottom-grid">

      <!-- Évolution sur 12 mois -->
      <div class="section-card">
        <div class="chart-section-header">
          <div>
            <div class="section-title">Évolution sur 12 mois</div>
            <div class="section-sub">Revenus vs dépenses</div>
          </div>
          <div class="chart-legend">
            <span class="chart-legend-item">
              <span class="chart-legend-dot" style="background:var(--accent);" />
              Revenus
            </span>
            <span class="chart-legend-item">
              <span class="chart-legend-dot" style="background:var(--ink-3);" />
              Dépenses
            </span>
          </div>
        </div>

        <div v-if="initialLoading" class="skeleton-block" style="height:200px;" />

        <template v-else-if="chartPoints.length >= 2">
          <div class="chart-overflow-wrap">
            <svg :viewBox="`0 0 ${CHART_W} ${CHART_H}`" style="width:100%;height:auto;display:block;">
              <!-- Grid lines -->
              <line
                v-for="(g, gi) in chartGridLines" :key="'gl'+gi"
                :x1="CHART_P.l" :y1="g.y" :x2="CHART_W - CHART_P.r" :y2="g.y"
                stroke="var(--line)" stroke-width="1" stroke-dasharray="2 3"
              />
              <!-- X labels -->
              <text
                v-for="(p, i) in chartPoints" :key="'xl'+i"
                :x="p.x.toFixed(1)" :y="CHART_H - 8"
                font-size="10" text-anchor="middle" fill="var(--ink-3)" font-family="Geist Mono, ui-monospace, monospace"
              >{{ p.m }}</text>
              <!-- Y labels -->
              <text
                v-for="(yl, i) in chartYLabels" :key="'yl'+i"
                :x="CHART_P.l - 6" :y="yl.y"
                font-size="9.5" text-anchor="end" fill="var(--ink-3)" font-family="Geist Mono, ui-monospace, monospace"
              >{{ yl.label }}</text>
              <!-- Expense area + line -->
              <path :d="chartExpArea" fill="var(--ink-3)" fill-opacity="0.08" />
              <path :d="chartExpPath" fill="none" stroke="var(--ink-3)" stroke-width="1.6" />
              <!-- Income area + line -->
              <path :d="chartIncArea" fill="var(--accent)" fill-opacity="0.12" />
              <path :d="chartIncPath" fill="none" stroke="var(--accent)" stroke-width="2" />
              <!-- Points + hover zones -->
              <g
                v-for="(p, i) in chartPoints" :key="'pt'+i"
                style="cursor:pointer;"
                @mouseenter="chartHover = i" @mouseleave="chartHover = null"
              >
                <rect :x="p.x - 22" :y="CHART_P.t" width="44" :height="CHART_H - CHART_P.t - CHART_P.b" fill="transparent" />
                <circle :cx="p.x.toFixed(1)" :cy="p.yInc.toFixed(1)" :r="chartHover === i ? 4.5 : 3"
                  fill="var(--accent)" stroke="var(--surface)" stroke-width="1.8" />
                <circle :cx="p.x.toFixed(1)" :cy="p.yExp.toFixed(1)" :r="chartHover === i ? 4.5 : 3"
                  fill="var(--ink-3)" stroke="var(--surface)" stroke-width="1.8" />
                <line v-if="chartHover === i"
                  :x1="p.x.toFixed(1)" :y1="CHART_P.t" :x2="p.x.toFixed(1)" :y2="CHART_H - CHART_P.b"
                  stroke="var(--ink-2)" stroke-width="1" stroke-dasharray="2 2" opacity="0.4"
                />
              </g>
            </svg>
          </div>
          <!-- Hover tooltip -->
          <div v-if="chartHover !== null && chartPoints[chartHover]" class="chart-tooltip">
            <span class="chart-tooltip-month">{{ chartPoints[chartHover].m }}</span>
            <div class="chart-tooltip-values mono">
              <span style="color:var(--accent);">+{{ formatCurrencyDisplay(chartPoints[chartHover].inc) }}</span>
              <span style="color:var(--ink-4);">·</span>
              <span style="color:var(--ink-3);">−{{ formatCurrencyDisplay(chartPoints[chartHover].exp) }}</span>
              <span style="color:var(--ink-4);">·</span>
              <span :style="{ color: chartPoints[chartHover].inc - chartPoints[chartHover].exp >= 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 500 }">
                {{ chartPoints[chartHover].inc - chartPoints[chartHover].exp >= 0 ? '+' : '' }}{{ formatCurrencyDisplay(chartPoints[chartHover].inc - chartPoints[chartHover].exp) }}
              </span>
            </div>
          </div>
        </template>
        <div v-else style="padding:40px 0;text-align:center;color:var(--ink-4);font-size:13px;">
          Pas encore de données sur 12 mois.
        </div>
      </div>

      <!-- Transactions récentes -->
      <div class="section-card recent-tx-card">
        <SectionHeader title="Transactions récentes" subtitle="5 dernières opérations" link="/transactions" />
        <div v-if="initialLoading">
          <div v-for="i in 3" :key="i" class="skeleton-block" style="height:44px;margin-bottom:6px;" />
        </div>
        <div v-else-if="recentTransactions.length === 0">
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
        <div v-else>
          <TransactionRow
            v-for="transaction in recentTransactions"
            :key="transaction.id"
            :transaction="transaction"
          />
        </div>
      </div>
    </div>

    <!-- ── À venir ─────────────────────────────────────────── -->
    <div v-if="upcomingSeries.length > 0" class="section-card">
      <SectionHeader title="À venir" subtitle="Transactions récurrentes prévues" />
      <div style="display:flex;flex-direction:column;gap:10px;">
        <div
          v-for="series in upcomingSeries" :key="series.id"
          style="display:flex;align-items:center;gap:12px;padding:10px 12px;background:var(--surface-2);border:1px solid var(--line);border-radius:10px;"
        >
          <div
            style="width:30px;height:30px;border-radius:8px;background:var(--surface);border:1px solid var(--line);display:grid;place-items:center;flex-shrink:0;"
            :style="{ color: series.type === 'income' ? 'var(--success)' : 'var(--ink-2)' }"
          >
            <UIcon
              :name="series.type === 'income' ? 'i-heroicons-banknotes' : 'i-heroicons-arrow-path'"
              style="width:14px;height:14px;"
            />
          </div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:13px;font-weight:500;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
              {{ series.description }}
            </div>
            <div class="mono" style="font-size:11px;color:var(--ink-3);">
              {{ formatUpcomingDate(series.next_occurrence) }}
              <span v-if="series.category" style="margin-left:6px;padding:0 5px;border-radius:3px;background:var(--surface);border:1px solid var(--line);font-size:10px;">
                {{ series.category.name }}
              </span>
            </div>
          </div>
          <div
            class="mono"
            style="font-size:13px;font-weight:500;flex-shrink:0;"
            :style="{ color: series.type === 'income' ? 'var(--success)' : 'var(--ink)' }"
          >
            {{ series.type === 'income' ? '+' : '−' }}{{ formatCurrencyDisplay(Math.abs(parseFloat(series.amount))) }}
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modals ──────────────────────────────────────────── -->
    <UModal v-model="showCorrectionModal">
      <UCard>
        <template #header>
          <h3 style="font-size:15px;font-weight:600;color:var(--ink);margin:0;">Corriger la catégorie</h3>
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
            <UButton :loading="correcting" :disabled="!correctionCategory" @click="handleCorrection">Enregistrer</UButton>
          </div>
        </div>
      </UCard>
    </UModal>

    <OnboardingWizard
      v-model="showOnboarding"
      @complete="handleOnboardingComplete"
      @skip="handleOnboardingComplete"
    />

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

definePageMeta({ middleware: 'auth' });

const { user } = useAuth();
const { getAccounts } = useAccounts();
const { getTransactions, getStatistics, updateTransaction, getMonthlySummary } = useTransactions();
const { getRecurringSeries } = useRecurring();
const { getCategories } = useCategories();
const { getDashboardData: getBudgetDashboardData } = useBudgets();
const { getAlerts, dismissAlert } = useAlerts();
const { registerShortcut } = useKeyboardShortcuts();
const { ensureProfileLoaded, budgetStartDay, getCurrentBudgetMonth } = useUserProfile();
const { formatForToast } = useErrorHandler();
const toast = useToast();

// State
const totalBalance = ref(0);
const accounts = ref<Account[]>([]);
const categories = ref<Category[]>([]);
const monthlyIncome = ref(0);
const monthlyExpenses = ref(0);
const recentTransactions = ref<Transaction[]>([]);
const showTransactionModal = ref(false);
const transactionInitialAccount = ref<number | string>('');
const initialLoading = ref(true);
const budgetDashData = ref<any>(null);
const showOnboarding = ref(false);
const pendingAlerts = ref<PendingAlert[]>([]);
const showCorrectionModal = ref(false);
const correctionAlert = ref<PendingAlert | null>(null);
const correctionCategory = ref<string | number>('');
const correcting = ref(false);
const monthlyHistory = ref<Array<{ m: string; inc: number; exp: number }>>([]);
const upcomingSeries = ref<any[]>([]);
const chartHover = ref<number | null>(null);

// Chart constants
const CHART_W = 600;
const CHART_H = 200;
const CHART_P = { l: 36, r: 12, t: 16, b: 28 };
const MONTH_ABBR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];
const MONTH_SHORT = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'];

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

// Month progress helpers
const currentDay = computed(() => {
  if (isCurrentMonth.value) return new Date().getDate();
  return new Date(selectedYear.value, selectedMonth.value, 0).getDate();
});
const daysInMonth = computed(() =>
  new Date(selectedYear.value, selectedMonth.value, 0).getDate()
);
const dayPct = computed(() => (currentDay.value / daysInMonth.value) * 100);

// Derived budget data
const totalBudget = computed(() => {
  if (!budgetDashData.value) return 0;
  return budgetDashData.value.categories.reduce((s: number, c: any) => s + (c.prevu || 0), 0);
});
const toAssign = computed(() => monthlyIncome.value - totalBudget.value);
const spendPct = computed(() =>
  totalBudget.value > 0 ? Math.min(100, (monthlyExpenses.value / totalBudget.value) * 100) : 0
);

// Format helpers
const fmtShort = (n: number) => {
  const abs = Math.abs(n);
  if (abs >= 1000) return (n < 0 ? '−' : '') + (abs / 1000).toFixed(1).replace('.0', '') + 'k';
  return Math.round(n).toString();
};

const formatUpcomingDate = (iso: string) => {
  const d = new Date(iso);
  return `${String(d.getDate()).padStart(2, '0')} ${MONTH_SHORT[d.getMonth()]}`;
};

// Chart computed properties
const chartPoints = computed(() => {
  const hist = monthlyHistory.value;
  if (hist.length < 2) return [];
  const max = Math.max(...hist.flatMap(d => [d.inc, d.exp])) * 1.1 || 1;
  const xFn = (i: number) => CHART_P.l + (i / (hist.length - 1)) * (CHART_W - CHART_P.l - CHART_P.r);
  const yFn = (v: number) => CHART_P.t + (1 - v / max) * (CHART_H - CHART_P.t - CHART_P.b);
  return hist.map((d, i) => ({ ...d, x: xFn(i), yInc: yFn(d.inc), yExp: yFn(d.exp) }));
});
const chartMax = computed(() => {
  const hist = monthlyHistory.value;
  return Math.max(...hist.flatMap(d => [d.inc, d.exp])) * 1.1 || 1;
});
const chartIncPath = computed(() =>
  chartPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.yInc.toFixed(1)}`).join(' ')
);
const chartExpPath = computed(() =>
  chartPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.yExp.toFixed(1)}`).join(' ')
);
const chartIncArea = computed(() => {
  const pts = chartPoints.value;
  if (!pts.length) return '';
  return `${chartIncPath.value} L ${pts.at(-1)!.x.toFixed(1)} ${CHART_H - CHART_P.b} L ${pts[0].x.toFixed(1)} ${CHART_H - CHART_P.b} Z`;
});
const chartExpArea = computed(() => {
  const pts = chartPoints.value;
  if (!pts.length) return '';
  return `${chartExpPath.value} L ${pts.at(-1)!.x.toFixed(1)} ${CHART_H - CHART_P.b} L ${pts[0].x.toFixed(1)} ${CHART_H - CHART_P.b} Z`;
});
const chartYLabels = computed(() => {
  const max = chartMax.value;
  return [0, 0.5, 1].map(g => ({
    v: max * (1 - g),
    y: (CHART_P.t + g * (CHART_H - CHART_P.t - CHART_P.b) + 3).toFixed(1),
    label: fmtShort(max * (1 - g)),
  }));
});
const chartGridLines = computed(() =>
  [0.25, 0.5, 0.75].map(g => ({
    y: (CHART_P.t + g * (CHART_H - CHART_P.t - CHART_P.b)).toFixed(1),
  }))
);

const formatCurrencyDisplay = (amount: number) => {
  const abs = Math.abs(amount);
  const formatted = abs.toLocaleString('fr-CH', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
  return `CHF ${amount < 0 ? '−' : ''}${formatted}`
};
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-CH', { style: 'currency', currency: 'CHF' }).format(amount);
};

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
const onMonthChange = async ({ year, month }: { year: number; month: number }) => {
  selectedMonthDate.value = new Date(year, month - 1, 1);
  await fetchMonthData();
};

const getCurrentMonthRange = () => {
  const year = selectedYear.value;
  const month = selectedMonth.value;
  const fmt = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  return {
    start_date: fmt(new Date(year, month - 1, 1)),
    end_date: fmt(new Date(year, month, 0)),
  };
};

const fetchMonthData = async () => {
  const monthRange = getCurrentMonthRange();
  const statsResponse = await getStatistics(monthRange);
  if (statsResponse.success && statsResponse.data) {
    monthlyIncome.value = statsResponse.data.income.total;
    monthlyExpenses.value = statsResponse.data.expense.total;
  }
  const budgetResult = await getBudgetDashboardData({ year: selectedYear.value, month: selectedMonth.value });
  if (budgetResult.success && budgetResult.data) {
    budgetDashData.value = budgetResult.data;
  }
};

const fetchAlerts = async () => {
  const result = await getAlerts();
  if (result.success && result.data) pendingAlerts.value = result.data;
};

const handleDismissAlert = async (alertId: number) => {
  const result = await dismissAlert(alertId);
  if (result.success) pendingAlerts.value = pendingAlerts.value.filter(a => a.id !== alertId);
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
  } else {
    toast.add({ title: 'Erreur', description: formatForToast(result.error), color: 'red' });
  }
  correcting.value = false;
};

const fetchMonthlyHistory = async () => {
  const year = new Date().getFullYear();
  const result = await getMonthlySummary(year);
  if (result.success && result.data) {
    monthlyHistory.value = MONTH_ABBR.map((m, i) => {
      const d = (result.data as any)[i + 1];
      return { m, inc: d?.income ?? 0, exp: d?.expense ?? 0 };
    });
  }
};

const fetchUpcoming = async () => {
  const result = await getRecurringSeries();
  if (result.success && result.data) {
    const today = new Date().toISOString().split('T')[0];
    upcomingSeries.value = result.data
      .filter(s => s.next_occurrence !== null && s.next_occurrence >= today)
      .sort((a, b) => a.next_occurrence!.localeCompare(b.next_occurrence!))
      .slice(0, 5);
  }
};

const fetchDashboardData = async () => {
  try {
    initialLoading.value = true;
    const [accountsRes, categoriesRes, txRes] = await Promise.all([
      getAccounts({ is_active: true }),
      getCategories({ is_active: true }),
      getTransactions({ ordering: '-date', end_date: new Date().toISOString().split('T')[0] }),
    ]);
    if (accountsRes.success && accountsRes.data) {
      accounts.value = accountsRes.data.results;
      totalBalance.value = accounts.value.reduce((s, a) => s + Number(a.current_balance || 0), 0);
    }
    if (categoriesRes.success && categoriesRes.data) categories.value = categoriesRes.data.results;
    if (txRes.success && txRes.data) recentTransactions.value = txRes.data.results.slice(0, 5);

    if (import.meta.client && accounts.value.length === 0 && categories.value.length === 0) {
      if (!localStorage.getItem('onboarding_completed')) showOnboarding.value = true;
    }

    await fetchMonthData();
  } catch (e) {
    console.error('Dashboard fetch error:', e);
  } finally {
    initialLoading.value = false;
  }
};

const openTransactionWithAccount = (accountId: number) => {
  transactionInitialAccount.value = accountId;
  showTransactionModal.value = true;
};

const handleOnboardingComplete = async () => {
  await fetchDashboardData();
  toast.add({ title: 'Bienvenue! 🎉', description: 'Votre compte a été créé avec succès', color: 'green' });
};

onMounted(async () => {
  await ensureProfileLoaded();
  // Initialise la navigation au mois budgétaire courant (selon budget_start_day)
  const { year, month } = getCurrentBudgetMonth(budgetStartDay.value);
  selectedMonthDate.value = new Date(year, month - 1, 1);
  await Promise.all([fetchDashboardData(), fetchAlerts(), fetchMonthlyHistory(), fetchUpcoming()]);
  registerShortcut('n', () => { showTransactionModal.value = true; }, {
    modifiers: { ctrl: true },
    description: 'Créer une nouvelle transaction',
  });
});
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp .4s cubic-bezier(.2,.7,.2,1) both; }

.dash-root {
  padding: 16px 16px 80px;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
@media (min-width: 640px) {
  .dash-root { padding: 20px 24px 40px; gap: 18px; }
}
@media (min-width: 1024px) {
  .dash-root { padding: 20px 32px 48px; }
}

/* ── Alerts ── */
.alerts-wrap { display: flex; flex-direction: column; gap: 8px; }
.alert-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 14px;
  background: color-mix(in oklab, #f59e0b 10%, var(--surface));
  border: 1px solid color-mix(in oklab, #f59e0b 30%, transparent);
  border-radius: 8px;
  flex-wrap: wrap;
}
.alert-row-left  { display: flex; align-items: flex-start; gap: 10px; color: var(--ink-2); }
.alert-row-right { display: flex; gap: 6px; flex-shrink: 0; }

/* ── Hero grid ── */
.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
@media (min-width: 640px)  { .hero-grid { grid-template-columns: 1fr 1fr; gap: 14px; } }
@media (min-width: 1024px) { .hero-grid { grid-template-columns: 1.4fr 1fr 1fr; } }

/* ── Stat cards ── */
.stat-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}
@media (min-width: 640px) {
  .stat-card { border-radius: 14px; padding: 24px; }
}
.stat-card--hero {
  grid-row: span 1;
}
@media (min-width: 640px) {
  .stat-card--hero { grid-column: span 2; }
}
@media (min-width: 1024px) {
  .stat-card--hero { grid-column: span 1; }
}
.stat-card--accent {
  background: linear-gradient(135deg, color-mix(in oklab, var(--accent) 8%, var(--surface)) 0%, var(--surface) 60%);
  border-color: color-mix(in oklab, var(--accent) 22%, var(--line));
}

.stat-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 500;
}
.stat-amount-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-top: 8px;
  flex-wrap: wrap;
}
.stat-amount {
  font-size: 30px;
  font-weight: 500;
  letter-spacing: -1px;
  color: var(--ink);
  line-height: 1;
  word-break: break-all;
}
@media (min-width: 480px) {
  .stat-amount { font-size: 36px; letter-spacing: -1.2px; }
}
@media (min-width: 1024px) {
  .stat-amount { font-size: 44px; letter-spacing: -1.5px; }
}
.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
}
.stat-trend--up {
  background: color-mix(in oklab, var(--success) 14%, transparent);
  color: var(--success);
  border: 1px solid color-mix(in oklab, var(--success) 25%, transparent);
}
.stat-trend--down {
  background: var(--danger-soft);
  color: var(--danger);
  border: 1px solid color-mix(in oklab, var(--danger) 25%, transparent);
}
.stat-sub {
  font-size: 13px;
  color: var(--ink-3);
  margin-top: 5px;
}

/* Accounts pills */
.accounts-pills {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--line);
}
.accounts-pills-label {
  font-size: 11px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 500;
  margin-bottom: 10px;
}
.accounts-pills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.account-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px 7px 8px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 10px;
  cursor: pointer;
  transition: border-color 0.12s, background 0.12s;
}
.account-pill:hover {
  border-color: var(--line-strong);
  background: var(--surface);
}
.account-pill-icon {
  width: 26px;
  height: 26px;
  border-radius: 7px;
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--ink-3);
  display: grid;
  place-items: center;
}
.account-pill-name    { font-size: 11.5px; color: var(--ink-3); line-height: 1.2; }
.account-pill-balance { font-size: 13px; font-weight: 500; color: var(--ink); line-height: 1.2; }

/* ── Sections ── */
.section-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  min-width: 0;
}
@media (min-width: 640px) {
  .section-card { border-radius: 14px; padding: 20px 24px; }
}
.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.section-title { font-size: 15px; font-weight: 600; color: var(--ink); letter-spacing: -0.2px; }
.section-sub   { font-size: 12.5px; color: var(--ink-3); margin-top: 2px; }

/* ── Envelopes grid ── */
.envelopes-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
@media (min-width: 640px) {
  .envelopes-grid { grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 12px; }
}
.envelope-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  text-decoration: none;
  transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
  position: relative;
  overflow: hidden;
}
@media (min-width: 640px) {
  .envelope-card { border-radius: 12px; padding: 16px; gap: 12px; }
}
.envelope-card:hover {
  border-color: var(--line-strong);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
.envelope-icon {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.envelope-name {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.envelope-over-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--danger-soft);
  color: var(--danger);
  border: 1px solid color-mix(in oklab, var(--danger) 30%, transparent);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  flex-shrink: 0;
  white-space: nowrap;
}

/* ── Bottom 2-col grid ── */
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  align-items: start;
}
@media (min-width: 1024px) {
  .bottom-grid { grid-template-columns: 1.4fr 1fr; gap: 18px; }
}

/* Transactions card — hauteur auto, pas d'étirement */
.recent-tx-card {
  display: flex;
  flex-direction: column;
}

/* ── Chart section ── */
.chart-section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.chart-legend {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-shrink: 0;
}
.chart-legend-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  color: var(--ink-3);
}
.chart-legend-dot {
  width: 8px; height: 8px;
  border-radius: 2px;
  flex-shrink: 0;
}
.chart-overflow-wrap {
  width: 100%;
  overflow: hidden;
}
.chart-overflow-wrap svg {
  display: block;
  width: 100%;
  height: auto;
}
.chart-tooltip {
  margin-top: 6px;
  padding: 8px 12px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
@media (min-width: 480px) {
  .chart-tooltip {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}
.chart-tooltip-month {
  font-size: 12px;
  font-weight: 500;
  color: var(--ink-2);
  text-transform: capitalize;
}
.chart-tooltip-values {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  flex-wrap: wrap;
}

/* ── Skeletons ── */
.skeleton-block {
  background: var(--surface-2);
  border-radius: 6px;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: .45; }
}
</style>
