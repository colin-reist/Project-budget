<template>
  <div class="adp-root">

    <!-- ── Header ──────────────────────────────────────────── -->
    <div
      class="adp-header"
      :style="{
        background: `linear-gradient(135deg, color-mix(in oklab, ${color} 10%, var(--surface)) 0%, var(--surface) 60%)`,
      }"
    >
      <div class="adp-header-left">
        <div
          class="adp-account-icon"
          :style="{
            background: `color-mix(in oklab, ${color} 14%, var(--surface))`,
            color,
            border: `1px solid color-mix(in oklab, ${color} 22%, transparent)`,
          }"
        >
          <UIcon :name="accountIconName" style="width:22px;height:22px;" />
        </div>
        <div>
          <div class="adp-account-name">{{ account.name }}</div>
          <div class="adp-account-sub">{{ account.account_type_display }}</div>
        </div>
      </div>
      <div class="adp-header-actions">
        <button class="adp-action-btn" @click="emit('edit')">
          <UIcon name="i-heroicons-pencil" style="width:13px;height:13px;" />
          <span class="hidden sm:inline">Modifier</span>
        </button>
        <button
          class="adp-action-btn"
          :style="{ color: account.is_active ? '#f59e0b' : 'var(--success)' }"
          @click="emit('toggle-active')"
        >
          <UIcon name="i-heroicons-power" style="width:13px;height:13px;" />
          <span class="hidden sm:inline">{{ account.is_active ? 'Désactiver' : 'Activer' }}</span>
        </button>
        <button class="adp-action-btn adp-action-btn--danger" @click="emit('delete')">
          <UIcon name="i-heroicons-trash" style="width:13px;height:13px;" />
        </button>
      </div>
    </div>

    <!-- ── Stats row ────────────────────────────────────────── -->
    <div class="adp-stats">
      <!-- Main balance (wider column) -->
      <div class="adp-stat adp-stat--main">
        <div class="adp-stat-label">Solde actuel</div>
        <div class="mono adp-stat-value adp-stat-value--large">{{ formatCurrencyDisplay(currentBalance) }}</div>
      </div>
      <!-- Income this month -->
      <div class="adp-stat">
        <div class="adp-stat-label">Revenus du mois</div>
        <div class="mono adp-stat-value" style="color:#16a34a;">
          <template v-if="isLoading">—</template>
          <template v-else>+{{ formatCurrencyDisplay(detailIncome) }}</template>
        </div>
      </div>
      <!-- Expenses this month -->
      <div class="adp-stat">
        <div class="adp-stat-label">Dépenses du mois</div>
        <div class="mono adp-stat-value">
          <template v-if="isLoading">—</template>
          <template v-else>−{{ formatCurrencyDisplay(detailExpense) }}</template>
        </div>
      </div>
      <!-- Transfers this month -->
      <div class="adp-stat">
        <div class="adp-stat-label">Transferts</div>
        <div class="mono adp-stat-value" style="color:var(--accent);">
          <template v-if="isLoading">—</template>
          <template v-else>{{ detailTransfer >= 0 ? '+' : '−' }}{{ formatCurrencyDisplay(Math.abs(detailTransfer)) }}</template>
        </div>
      </div>
    </div>

    <!-- ── Chart + recent transactions ──────────────────────── -->
    <div class="adp-bottom">

      <!-- Balance evolution chart -->
      <div class="adp-chart-section">
        <div class="adp-section-header">
          <span class="adp-section-title">Évolution du solde</span>
          <div class="adp-range-picker">
            <button
              v-for="(r, i) in rangeOptions"
              :key="r"
              class="adp-range-btn"
              :class="{ 'adp-range-btn--active': activeRange === i }"
              @click="activeRange = i"
            >{{ r }}</button>
          </div>
        </div>

        <div v-if="isLoading" class="adp-chart-loading">
          <div class="skeleton-block" style="height:100%;border-radius:6px;" />
        </div>
        <template v-else-if="chartHistory.length >= 2">
          <svg
            :viewBox="`0 0 ${CW} ${CH}`"
            style="width:100%;height:auto;display:block;"
          >
            <defs>
              <linearGradient :id="`balgrad-${gradId}`" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" :stop-color="color" stop-opacity="0.18" />
                <stop offset="1" :stop-color="color" stop-opacity="0" />
              </linearGradient>
            </defs>
            <!-- Grid lines -->
            <line
              v-for="(g, i) in [0.25, 0.5, 0.75]"
              :key="i"
              :x1="CP.l" :y1="CP.t + g * (CH - CP.t - CP.b)"
              :x2="CW - CP.r" :y2="CP.t + g * (CH - CP.t - CP.b)"
              stroke="var(--line)" stroke-width="1" stroke-dasharray="2 3"
            />
            <!-- Y labels -->
            <text
              v-for="(g, i) in [0, 0.5, 1]"
              :key="i"
              :x="CP.l - 6"
              :y="cy(chartMax - g * chartSpan) + 3"
              font-size="9.5"
              text-anchor="end"
              fill="var(--ink-3)"
              font-family="'Geist Mono', monospace"
            >{{ fmtShort(chartMax - g * chartSpan) }}</text>
            <!-- X labels (month names) -->
            <text
              v-for="(m, i) in visibleMonthLabels"
              :key="i"
              :x="cx(i)"
              :y="CH - 8"
              font-size="9.5"
              text-anchor="middle"
              fill="var(--ink-3)"
              font-family="'Geist Mono', monospace"
            >{{ m }}</text>
            <!-- Area fill -->
            <path :d="chartArea" :fill="`url(#balgrad-${gradId})`" />
            <!-- Line -->
            <path :d="chartPath" fill="none" :stroke="color" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />
            <!-- Hover zones + points -->
            <g v-for="(v, i) in chartHistory" :key="i">
              <rect
                :x="cx(i) - (CW - CP.l - CP.r) / chartHistory.length / 2"
                :y="CP.t"
                :width="(CW - CP.l - CP.r) / chartHistory.length"
                :height="CH - CP.t - CP.b"
                fill="transparent"
                style="cursor:crosshair;"
                @mouseenter="hoveredIndex = i"
                @mouseleave="hoveredIndex = chartHistory.length - 1"
              />
              <line
                v-if="hoveredIndex === i"
                :x1="cx(i)" :y1="CP.t"
                :x2="cx(i)" :y2="CH - CP.b"
                :stroke="color" stroke-width="1" stroke-dasharray="2 2" opacity="0.5"
              />
              <circle
                :cx="cx(i)" :cy="cy(v)"
                :r="hoveredIndex === i ? 4.5 : 2.4"
                :fill="color"
                stroke="var(--surface)"
                :stroke-width="hoveredIndex === i ? 2 : 1.5"
              />
            </g>
          </svg>
          <!-- Tooltip below chart -->
          <div class="adp-chart-tooltip">
            <span style="font-weight:500;">{{ visibleMonthLabels[hoveredIndex] }} {{ currentYear }}</span>
            <span class="mono" style="color:var(--ink);font-weight:500;">
              {{ formatCurrencyDisplay(chartHistory[hoveredIndex] ?? 0) }}
            </span>
          </div>
        </template>
        <div v-else class="adp-empty-msg">Pas encore de données d'historique.</div>
      </div>

      <!-- Recent transactions -->
      <div class="adp-txn-section">
        <div class="adp-section-header">
          <span class="adp-section-title">Transactions récentes</span>
          <NuxtLink to="/transactions" class="adp-see-all">
            Tout
            <UIcon name="i-heroicons-chevron-right" style="width:11px;height:11px;" />
          </NuxtLink>
        </div>

        <div v-if="isLoading" class="adp-txn-loading">
          <div v-for="i in 4" :key="i" class="skeleton-block" style="height:36px;border-radius:6px;margin-bottom:6px;" />
        </div>
        <div v-else-if="currentMonthTxns.length === 0" class="adp-empty-msg">
          Aucune transaction ce mois-ci.
        </div>
        <div v-else class="adp-txn-list">
          <div
            v-for="(txn, i) in currentMonthTxns.slice(0, 6)"
            :key="txn.id"
            class="adp-txn-row"
            :style="{ borderBottom: i === Math.min(currentMonthTxns.length, 6) - 1 ? 'none' : '1px solid var(--line)' }"
          >
            <div
              class="adp-txn-icon"
              :style="{
                color: txn.type === 'income' ? '#16a34a' : txn.type === 'transfer' ? 'var(--accent)' : 'var(--ink-2)',
              }"
            >
              <UIcon :name="txnIcon(txn)" style="width:13px;height:13px;" />
            </div>
            <div class="adp-txn-info">
              <div class="adp-txn-desc">{{ txn.description || 'Transaction' }}</div>
              <div class="mono adp-txn-date">{{ formatDate(txn.date) }}</div>
            </div>
            <span
              class="mono adp-txn-amount"
              :style="{ color: txn.type === 'income' ? '#16a34a' : 'var(--ink)' }"
            >
              {{ txn.type === 'income' ? '+' : txn.type === 'expense' ? '−' : '±' }}{{ formatCurrencyDisplay(Math.abs(parseFloat(txn.amount))) }}
            </span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { Account, Transaction } from '~/types';

const props = defineProps<{
  account: Account;
  transactions: Transaction[];
  balanceHistory: number[];
  isLoading: boolean;
  currentYear: number;
  currentMonth: number;
}>();

const emit = defineEmits<{
  edit: [];
  'toggle-active': [];
  delete: [];
}>();

/* ─── Injected helpers ─────────────────────────────────────── */
const formatCurrencyDisplay = inject<(amount: number, currency?: string) => string>('formatCurrencyDisplay')!;
const fmtShort = inject<(n: number) => string>('fmtShort')!;
const accountColor = inject<(type: string) => string>('accountColor')!;
const accountIcon = inject<(type: string) => string>('accountIcon')!;

/* ─── Chart config ─────────────────────────────────────────── */
const CW = 720;
const CH = 220;
const CP = { l: 44, r: 14, t: 24, b: 30 };
const rangeOptions = ['1M', '3M', '6M', '12M'];
const activeRange = ref(3); // default to 12M
const hoveredIndex = ref(0);

/* ─── Derived values ───────────────────────────────────────── */
const color = computed(() => accountColor(props.account.account_type));
const accountIconName = computed(() => accountIcon(props.account.account_type));
const gradId = computed(() => props.account.id.toString());

const currentBalance = computed(() =>
  parseFloat(props.account.current_balance || props.account.balance)
);

/* ─── Month labels (last 12 months from current) ───────────── */
const ALL_MONTHS_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];

const allMonthLabels = computed(() => {
  return Array.from({ length: 12 }, (_, i) => {
    let m = props.currentMonth - 11 + i;
    while (m <= 0) m += 12;
    while (m > 12) m -= 12;
    return ALL_MONTHS_FR[m - 1];
  });
});

/* ─── Range-sliced history ─────────────────────────────────── */
const rangeCounts = [1, 3, 6, 12];
const chartHistory = computed(() => {
  const count = rangeCounts[activeRange.value];
  return props.balanceHistory.slice(12 - count);
});
const visibleMonthLabels = computed(() => {
  const count = rangeCounts[activeRange.value];
  return allMonthLabels.value.slice(12 - count);
});

// Initialize hovered index when history changes
watch(chartHistory, (h) => { hoveredIndex.value = h.length - 1; }, { immediate: true });

/* ─── Chart math ───────────────────────────────────────────── */
const chartMin = computed(() => Math.min(...chartHistory.value));
const chartMax = computed(() => Math.max(...chartHistory.value));
const chartSpan = computed(() => Math.max(1, chartMax.value - chartMin.value));

const cx = (i: number) =>
  CP.l + (i / Math.max(1, chartHistory.value.length - 1)) * (CW - CP.l - CP.r);

const cy = (v: number) =>
  CP.t + (1 - (v - chartMin.value) / chartSpan.value) * (CH - CP.t - CP.b);

const chartPath = computed(() =>
  chartHistory.value
    .map((v, i) => `${i === 0 ? 'M' : 'L'} ${cx(i).toFixed(1)} ${cy(v).toFixed(1)}`)
    .join(' ')
);
const chartArea = computed(() => {
  const last = chartHistory.value.length - 1;
  return `${chartPath.value} L ${cx(last)} ${CH - CP.b} L ${cx(0)} ${CH - CP.b} Z`;
});

/* ─── Current month transactions ───────────────────────────── */
const currentMonthTxns = computed(() => {
  const pad = (n: number) => String(n).padStart(2, '0');
  const prefix = `${props.currentYear}-${pad(props.currentMonth)}`;
  return props.transactions.filter(t => t.date.startsWith(prefix));
});

/* ─── Monthly stats ────────────────────────────────────────── */
const detailIncome = computed(() =>
  currentMonthTxns.value
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + parseFloat(t.amount), 0)
);
const detailExpense = computed(() =>
  currentMonthTxns.value
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + parseFloat(t.amount), 0)
);
const detailTransfer = computed(() =>
  currentMonthTxns.value
    .filter(t => t.type === 'transfer')
    .reduce((sum, t) => sum + parseFloat(t.amount), 0)
);

/* ─── Helpers ──────────────────────────────────────────────── */
/**
 * Returns an appropriate icon name based on the transaction's category or type.
 */
const txnIcon = (t: Transaction): string => {
  if (t.category_details?.icon) return t.category_details.icon;
  if (t.type === 'income') return 'i-heroicons-arrow-down-left';
  if (t.type === 'transfer') return 'i-heroicons-arrows-right-left';
  return 'i-heroicons-arrow-up-right';
};

/**
 * Format ISO date string to short locale date (e.g. "12.05.2026").
 */
const formatDate = (iso: string): string => {
  const d = new Date(iso);
  return new Intl.DateTimeFormat('fr-CH', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(d);
};
</script>

<style scoped>
.adp-root {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

/* ── Header ── */
.adp-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.adp-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.adp-account-icon {
  width: 44px;
  height: 44px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.adp-account-name {
  font-size: 17px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.2px;
}
.adp-account-sub {
  font-size: 12.5px;
  color: var(--ink-3);
  margin-top: 2px;
}
.adp-header-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.adp-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 34px;
  padding: 0 12px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--ink-2);
  background: var(--surface);
  border: 1px solid var(--line-strong);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
  font-family: inherit;
}
.adp-action-btn:hover {
  background: var(--surface-2);
  border-color: var(--line-strong);
}
.adp-action-btn--danger {
  color: var(--danger);
}
.adp-action-btn--danger:hover {
  background: var(--danger-soft);
  border-color: color-mix(in oklab, var(--danger) 30%, transparent);
}

/* ── Stats row ── */
.adp-stats {
  padding: 20px 24px;
  border-bottom: 1px solid var(--line);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px 24px;
}
@media (min-width: 768px) {
  .adp-stats { grid-template-columns: 1.4fr 1fr 1fr 1fr; }
}
.adp-stat {}
.adp-stat-label {
  font-size: 11px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 500;
}
.adp-stat-value {
  font-size: 18px;
  font-weight: 500;
  color: var(--ink);
  margin-top: 2px;
  line-height: 1.2;
}
.adp-stat-value--large {
  font-size: 28px;
  letter-spacing: -0.8px;
  line-height: 1.1;
}
@media (min-width: 768px) {
  .adp-stat-value--large { font-size: 30px; }
}

/* ── Bottom grid ── */
.adp-bottom {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
}
@media (min-width: 768px) {
  .adp-bottom { grid-template-columns: 1.4fr 1fr; }
}

.adp-chart-section {
  padding: 20px 24px;
  border-bottom: 1px solid var(--line);
}
@media (min-width: 768px) {
  .adp-chart-section {
    border-bottom: none;
    border-right: 1px solid var(--line);
  }
}
.adp-txn-section {
  padding: 20px 24px;
}

.adp-section-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
}
.adp-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
}

/* Range picker */
.adp-range-picker {
  display: flex;
  gap: 2px;
  padding: 3px;
  background: var(--surface-2);
  border-radius: 6px;
  border: 1px solid var(--line);
}
.adp-range-btn {
  height: 22px;
  padding: 0 8px;
  font-size: 11px;
  font-weight: 500;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--ink-3);
  font-family: inherit;
  transition: background 0.12s, color 0.12s;
}
.adp-range-btn--active {
  background: var(--surface);
  border: 1px solid var(--line-strong);
  color: var(--ink);
}

/* Chart */
.adp-chart-loading {
  height: 160px;
}
.adp-chart-tooltip {
  margin-top: 6px;
  padding: 8px 12px;
  background: var(--surface-2);
  border-radius: 8px;
  border: 1px solid var(--line);
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--ink-2);
}

/* See all link */
.adp-see-all {
  font-size: 12px;
  color: var(--accent);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  text-decoration: none;
}
.adp-see-all:hover { text-decoration: underline; }

/* Transactions */
.adp-txn-loading { display: flex; flex-direction: column; gap: 6px; }
.adp-txn-list { display: flex; flex-direction: column; }
.adp-txn-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
}
.adp-txn-icon {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.adp-txn-info { flex: 1; min-width: 0; }
.adp-txn-desc { font-size: 12.5px; font-weight: 500; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.adp-txn-date { font-size: 10.5px; color: var(--ink-3); }
.adp-txn-amount { font-size: 12.5px; font-weight: 500; flex-shrink: 0; }

.adp-empty-msg {
  font-size: 12px;
  color: var(--ink-3);
  text-align: center;
  padding: 24px 0;
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
