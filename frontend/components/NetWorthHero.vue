<template>
  <div class="nwh-root">
    <div class="nwh-grid">

      <!-- ── Left: total patrimony ─────────────────────────── -->
      <div class="nwh-left">
        <div class="nwh-label">
          <UIcon name="i-heroicons-building-library" style="width:14px;height:14px;color:var(--ink-4);" />
          Patrimoine net
        </div>

        <div class="nwh-total-row">
          <span class="mono nwh-total">{{ formatCurrencyDisplay(totalBalance) }}</span>
          <span
            class="nwh-delta-badge"
            :class="netChange >= 0 ? 'nwh-delta-badge--up' : 'nwh-delta-badge--down'"
          >
            <UIcon
              :name="netChange >= 0 ? 'i-heroicons-arrow-trending-up' : 'i-heroicons-arrow-trending-down'"
              style="width:12px;height:12px;"
            />
            {{ netChange >= 0 ? '+' : '' }}{{ changePct.toFixed(1) }}%
          </span>
        </div>

        <div class="nwh-subtitle">
          {{ netChange >= 0 ? '+' : '' }}{{ formatCurrencyDisplay(netChange) }} sur 30 jours · {{ accounts.length }} compte{{ accounts.length > 1 ? 's' : '' }}
        </div>

        <!-- Breakdown stacked bar -->
        <div class="nwh-breakdown">
          <div class="nwh-bar">
            <div
              v-for="bucket in buckets"
              :key="bucket.label"
              :style="{ width: `${bucket.pct}%`, background: bucket.color, transition: 'width 0.4s ease' }"
            />
          </div>
          <div class="nwh-legend">
            <div v-for="bucket in buckets" :key="bucket.label" class="nwh-legend-item">
              <span class="nwh-legend-dot" :style="{ background: bucket.color }" />
              <div class="nwh-legend-text">
                <span class="nwh-legend-label">{{ bucket.label }}</span>
                <span class="mono nwh-legend-value">{{ formatCurrencyDisplay(bucket.value) }} · {{ bucket.pct.toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Right: 12-month chart ─────────────────────────── -->
      <div class="nwh-right">
        <div class="nwh-chart-header">
          <span class="nwh-chart-label">Évolution 12 mois</span>
          <span class="mono nwh-chart-range" v-if="netWorthHistory.length >= 2">
            {{ fmtShort(histMin) }} – {{ fmtShort(histMax) }}
          </span>
        </div>

        <div v-if="isLoadingHistory" class="nwh-chart-loading">
          <div class="skeleton-block" style="height:100%;border-radius:6px;" />
        </div>
        <svg
          v-else-if="netWorthHistory.length >= 2"
          :viewBox="`0 0 ${W} ${H}`"
          style="width:100%;height:auto;display:block;"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id="netgrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stop-color="var(--accent)" stop-opacity="0.22" />
              <stop offset="1" stop-color="var(--accent)" stop-opacity="0" />
            </linearGradient>
          </defs>
          <path :d="chartArea" fill="url(#netgrad)" />
          <path :d="chartPath" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" />
          <!-- Last point highlight -->
          <circle
            :cx="xs(netWorthHistory.length - 1)"
            :cy="ys(netWorthHistory[netWorthHistory.length - 1])"
            r="4"
            fill="var(--accent)"
            stroke="var(--surface)"
            stroke-width="2"
          />
        </svg>
        <div v-else class="nwh-chart-empty">Pas encore de données</div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { Account } from '~/types';

const props = defineProps<{
  accounts: Account[];
  netWorthHistory: number[];
  isLoadingHistory: boolean;
}>();

/* ─── Injected helpers ─────────────────────────────────────── */
const formatCurrencyDisplay = inject<(amount: number, currency?: string) => string>('formatCurrencyDisplay')!;
const fmtShort = inject<(n: number) => string>('fmtShort')!;

/* ─── Chart dimensions ─────────────────────────────────────── */
const W = 760;
const H = 130;
const P = { l: 0, r: 0, t: 14, b: 4 };

/* ─── Totals ───────────────────────────────────────────────── */
const totalBalance = computed(() =>
  props.accounts.reduce((sum, a) => sum + parseFloat(a.current_balance || a.balance), 0)
);

// Approximate 30-day change: difference between last two history points
const netChange = computed(() => {
  if (props.netWorthHistory.length < 2) return 0;
  return props.netWorthHistory[11] - props.netWorthHistory[10];
});

const changePct = computed(() => {
  const prev = totalBalance.value - netChange.value;
  if (prev === 0) return 0;
  return (netChange.value / prev) * 100;
});

/* ─── Breakdown buckets ────────────────────────────────────── */
const buckets = computed(() => {
  const total = totalBalance.value;
  return [
    { label: 'Liquide',         types: ['checking', 'cash'],   color: '#2563eb' },
    { label: 'Épargne',         types: ['savings'],             color: '#16a34a' },
    { label: 'Investissements', types: ['investment'],          color: '#7c3aed' },
  ].map(b => {
    const value = props.accounts
      .filter(a => b.types.includes(a.account_type))
      .reduce((sum, a) => sum + parseFloat(a.current_balance || a.balance), 0);
    return {
      ...b,
      value,
      pct: total === 0 ? 0 : (value / total) * 100,
    };
  }).filter(b => b.value > 0);
});

/* ─── Chart calculations ───────────────────────────────────── */
const histMin = computed(() => Math.min(...props.netWorthHistory));
const histMax = computed(() => Math.max(...props.netWorthHistory));

const xs = (i: number) => (i / (props.netWorthHistory.length - 1)) * (W - P.l - P.r);
const ys = (v: number) => {
  const span = Math.max(1, histMax.value - histMin.value);
  return P.t + (1 - (v - histMin.value) / span) * (H - P.t - P.b);
};

const chartPath = computed(() =>
  props.netWorthHistory
    .map((v, i) => `${i === 0 ? 'M' : 'L'} ${xs(i).toFixed(1)} ${ys(v).toFixed(1)}`)
    .join(' ')
);

const chartArea = computed(() => {
  const last = props.netWorthHistory.length - 1;
  return `${chartPath.value} L ${xs(last)} ${H} L 0 ${H} Z`;
});
</script>

<style scoped>
.nwh-root {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 24px 28px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.nwh-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}
@media (min-width: 768px) {
  .nwh-grid { grid-template-columns: 1fr 1fr; gap: 32px; }
}

/* ── Left ── */
.nwh-left {
  display: flex;
  flex-direction: column;
}
.nwh-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 500;
}
.nwh-total-row {
  display: flex;
  align-items: baseline;
  gap: 14px;
  margin-top: 6px;
  flex-wrap: wrap;
}
.nwh-total {
  font-size: clamp(32px, 5vw, 48px);
  font-weight: 500;
  letter-spacing: -2px;
  color: var(--ink);
  line-height: 1;
}
.nwh-delta-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
}
.nwh-delta-badge--up {
  background: color-mix(in oklab, #16a34a 14%, transparent);
  color: #16a34a;
  border: 1px solid color-mix(in oklab, #16a34a 25%, transparent);
}
.nwh-delta-badge--down {
  background: var(--danger-soft);
  color: var(--danger);
  border: 1px solid color-mix(in oklab, var(--danger) 25%, transparent);
}
.nwh-subtitle {
  font-size: 13px;
  color: var(--ink-3);
  margin-top: 8px;
}

/* Breakdown */
.nwh-breakdown {
  margin-top: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.nwh-bar {
  display: flex;
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  background: var(--surface-2);
  border: 1px solid var(--line);
}
.nwh-legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.nwh-legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.nwh-legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  flex-shrink: 0;
}
.nwh-legend-text {
  display: flex;
  flex-direction: column;
}
.nwh-legend-label { font-size: 11.5px; color: var(--ink-3); line-height: 1.2; }
.nwh-legend-value { font-size: 12.5px; font-weight: 500; color: var(--ink); line-height: 1.2; }

/* ── Right ── */
.nwh-right {
  display: flex;
  flex-direction: column;
}
.nwh-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}
.nwh-chart-label {
  font-size: 12px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 500;
}
.nwh-chart-range {
  font-size: 11px;
  color: var(--ink-3);
}
.nwh-chart-loading {
  flex: 1;
  min-height: 100px;
}
.nwh-chart-empty {
  font-size: 12px;
  color: var(--ink-4);
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
