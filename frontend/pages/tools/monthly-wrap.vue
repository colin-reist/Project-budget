<template>
  <div class="page-root fade-up">

    <!-- ── Header ──────────────────────────────────────────────── -->
    <PageHeader title="Review Mensuel" subtitle="Bilan financier du mois sélectionné">
      <template #actions>
        <MonthNavigation
          :model-value="{ year: selectedYear, month: selectedMonth }"
          @update:model-value="({ year: y, month: m }) => { selectedYear.value = y; selectedMonth.value = m; loadData() }"
        />
      </template>
    </PageHeader>

    <!-- ── Loading ─────────────────────────────────────────────── -->
    <div v-if="loading" class="loading-wrap">
      <UIcon name="i-heroicons-arrow-path" class="spin" style="width:28px;height:28px;color:var(--ink-4);" />
    </div>

    <!-- ── Error ───────────────────────────────────────────────── -->
    <div v-else-if="error" class="error-wrap section-card">
      <UIcon name="i-heroicons-exclamation-circle" style="width:40px;height:40px;color:var(--danger);" />
      <p style="font-size:14px;color:var(--ink-3);margin:8px 0 0;">Impossible de charger les données</p>
      <button class="ds-btn ds-btn-secondary" style="margin-top:12px;" @click="loadData">Réessayer</button>
    </div>

    <template v-else>

      <!-- ── Stat cards ligne 1 : revenus, dépenses, net ─────── -->
      <div class="hero-grid">

        <!-- Revenus -->
        <div class="stat-card stat-card--income">
          <div class="stat-label">
            <UIcon name="i-heroicons-arrow-trending-up" style="width:14px;height:14px;" />
            Revenus
          </div>
          <div class="mono stat-amount" style="color:var(--success);">
            {{ formatAmount(stats?.income.total ?? 0) }}
          </div>
          <div class="stat-count">{{ stats?.income.count ?? 0 }} transaction(s)</div>
        </div>

        <!-- Dépenses -->
        <div class="stat-card stat-card--expense">
          <div class="stat-label">
            <UIcon name="i-heroicons-arrow-trending-down" style="width:14px;height:14px;" />
            Dépenses
          </div>
          <div class="mono stat-amount" style="color:var(--danger);">
            {{ formatAmount(stats?.expense.total ?? 0) }}
          </div>
          <div class="stat-count">{{ stats?.expense.count ?? 0 }} transaction(s)</div>
        </div>

        <!-- Net -->
        <div class="stat-card" :class="net >= 0 ? 'stat-card--net-pos' : 'stat-card--net-neg'">
          <div class="stat-label">
            <UIcon name="i-heroicons-scale" style="width:14px;height:14px;" />
            Net du mois
          </div>
          <div class="mono stat-amount" :style="{ color: net >= 0 ? 'var(--accent)' : '#f59e0b' }">
            {{ net >= 0 ? '+' : '' }}{{ formatAmount(net) }}
          </div>
          <div class="stat-count">{{ net >= 0 ? 'Excédent' : 'Déficit' }}</div>
        </div>

      </div>

      <!-- ── Bannière épargne ─────────────────────────────────── -->
      <div v-if="net > 0" class="savings-banner">
        <span style="font-size:22px;line-height:1;flex-shrink:0;">💡</span>
        <div>
          <p class="savings-banner-title">Tu pourrais mettre {{ formatAmount(net) }} en épargne ce mois</p>
          <p class="savings-banner-sub">Soit {{ savingsRate }}% de tes revenus — félicitations !</p>
        </div>
      </div>

      <!-- ── Mini-cards ligne 2 ──────────────────────────────── -->
      <div class="mini-grid">

        <!-- Dépenses/jour -->
        <div class="mini-card">
          <div class="mini-label">Dépenses / jour</div>
          <div class="mono mini-value">{{ formatAmount(avgPerDay) }}</div>
          <div class="mini-sub">sur {{ daysInMonth }} jours</div>
        </div>

        <!-- Nb transactions -->
        <div class="mini-card">
          <div class="mini-label">Transactions</div>
          <div class="mono mini-value">{{ totalTransactions }}</div>
          <div class="mini-sub">ce mois-ci</div>
        </div>

        <!-- vs mois précédent -->
        <div class="mini-card">
          <div class="mini-label">vs mois précédent</div>
          <template v-if="prevStats">
            <div
              class="mono mini-value"
              :style="{ color: expenseChange >= 0 ? 'var(--danger)' : 'var(--success)' }"
            >
              {{ expenseChange >= 0 ? '+' : '' }}{{ expenseChange.toFixed(0) }}% dépenses
            </div>
            <div class="mini-sub">{{ prevMonthLabel }}</div>
          </template>
          <div v-else class="mini-sub" style="margin-top:4px;">Pas de données</div>
        </div>

      </div>

      <!-- ── Évolution du solde net ───────────────────────────── -->
      <div class="section-card">
        <div class="section-header" style="margin-bottom:12px;">
          <div>
            <div class="section-title">
              <UIcon name="i-heroicons-chart-bar" style="width:15px;height:15px;color:var(--accent);vertical-align:middle;" />
              Évolution du solde net
            </div>
            <div class="section-sub">Flux net cumulatif sur le mois (revenus − dépenses)</div>
          </div>
        </div>

        <div v-if="balanceSeries.length === 0" class="empty-chart">Aucune donnée</div>
        <div v-else class="chart-wrap">
          <svg width="100%" height="160" viewBox="0 0 1000 160" preserveAspectRatio="none" style="overflow:visible;">
            <defs>
              <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="var(--primary-500)" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="var(--primary-500)" stop-opacity="0.02"/>
              </linearGradient>
            </defs>
            <!-- Ligne zéro -->
            <line :x1="30" :x2="970" :y1="zeroY()" :y2="zeroY()" stroke="var(--line)" stroke-width="1.5" stroke-dasharray="6,4" />
            <!-- Aire -->
            <path :d="areaPath()" fill="url(#balanceGrad)" />
            <!-- Courbe -->
            <polyline :points="linePoints()" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" />
            <!-- Point final -->
            <circle
              v-if="balanceSeries.length"
              :cx="xVB(balanceSeries[balanceSeries.length - 1].day)"
              :cy="yPx(balanceSeries[balanceSeries.length - 1].value)"
              r="5"
              :fill="balanceSeries[balanceSeries.length - 1].value >= 0 ? 'var(--accent)' : 'var(--danger)'"
              stroke="var(--surface)" stroke-width="2.5"
            />
          </svg>
          <!-- Labels min/max en overlay -->
          <div class="chart-labels-y">
            <span>{{ formatShort(seriesMax) }}</span>
            <span>{{ formatShort(seriesMin) }}</span>
          </div>
          <!-- Valeur finale flottante -->
          <div
            class="mono chart-final-label"
            :style="{
              top: (yPx(balanceSeries[balanceSeries.length - 1].value) / 160 * 100) + '%',
              color: balanceSeries[balanceSeries.length - 1].value >= 0 ? 'var(--accent)' : 'var(--danger)',
            }"
          >
            {{ formatShort(balanceSeries[balanceSeries.length - 1].value) }}
          </div>
        </div>

        <!-- Axe des dates -->
        <div class="chart-axis-x">
          <span style="position:absolute;left:0;">1</span>
          <span style="position:absolute;" :style="{ left: xPct(Math.ceil(daysInMonth / 4)) + '%' }">{{ Math.ceil(daysInMonth / 4) }}</span>
          <span style="position:absolute;" :style="{ left: xPct(Math.ceil(daysInMonth / 2)) + '%' }">{{ Math.ceil(daysInMonth / 2) }}</span>
          <span style="position:absolute;" :style="{ left: xPct(Math.ceil(daysInMonth * 3 / 4)) + '%' }">{{ Math.ceil(daysInMonth * 3 / 4) }}</span>
          <span style="position:absolute;right:0;">{{ daysInMonth }}</span>
        </div>
      </div>

      <!-- ── État des budgets ─────────────────────────────────── -->
      <div v-if="budgetData.length > 0" class="section-card">
        <div class="section-header">
          <div>
            <div class="section-title">
              <UIcon name="i-heroicons-chart-bar-square" style="width:15px;height:15px;color:#a855f7;vertical-align:middle;" />
              État des budgets
            </div>
          </div>
        </div>
        <div class="budget-list">
          <div v-for="(b, i) in budgetData" :key="i" class="budget-row">
            <div class="budget-row-top">
              <div class="budget-row-name">
                <UIcon
                  :name="b.is_over ? 'i-heroicons-exclamation-circle' : 'i-heroicons-check-circle'"
                  :style="{ color: b.is_over ? 'var(--danger)' : 'var(--success)' }"
                  style="width:14px;height:14px;flex-shrink:0;"
                />
                <span>{{ b.category_name }}</span>
                <span v-if="b.unbudgeted" class="ds-badge ds-badge-neutral" style="font-size:10px;">hors budget</span>
              </div>
              <div class="budget-row-amounts mono">
                <span :style="{ color: b.is_over ? 'var(--danger)' : 'var(--ink)', fontWeight: b.is_over ? 600 : 400 }">
                  {{ formatAmount(b.reel) }}
                </span>
                <span v-if="b.prevu > 0" style="color:var(--ink-4);"> / {{ formatAmount(b.prevu) }}</span>
              </div>
            </div>
            <div v-if="b.prevu > 0" class="ds-progress" style="margin-top:6px;">
              <div
                class="ds-progress-bar"
                :class="b.is_over ? 'over' : (b.reel / b.prevu > 0.8 ? 'warn' : '')"
                :style="{ width: Math.min(100, b.prevu > 0 ? (b.reel / b.prevu * 100) : 0) + '%' }"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- ── Top dépenses + Top revenus ─────────────────────── -->
      <div class="top-grid">

        <!-- Top dépenses -->
        <div class="section-card">
          <div class="section-header" style="margin-bottom:14px;">
            <div class="section-title">
              <UIcon name="i-heroicons-arrow-trending-down" style="width:14px;height:14px;color:var(--danger);vertical-align:middle;" />
              Top dépenses
            </div>
          </div>
          <div v-if="topExpenses.length === 0" class="empty-chart">Aucune dépense ce mois</div>
          <div v-else class="top-list">
            <div v-for="cat in topExpenses" :key="cat.category_id" class="top-row">
              <div class="top-row-head">
                <span class="top-row-name">{{ cat.category_name }}</span>
                <span class="mono top-row-amount">{{ formatAmount(cat.total) }} <span style="color:var(--ink-4);">({{ categoryPercent(cat.total, 'expense') }}%)</span></span>
              </div>
              <div class="ds-progress">
                <div
                  class="ds-progress-bar"
                  style="background:var(--danger);"
                  :style="{ width: categoryPercent(cat.total, 'expense') + '%' }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Top revenus -->
        <div class="section-card">
          <div class="section-header" style="margin-bottom:14px;">
            <div class="section-title">
              <UIcon name="i-heroicons-arrow-trending-up" style="width:14px;height:14px;color:var(--success);vertical-align:middle;" />
              Top revenus
            </div>
          </div>
          <div v-if="topIncomes.length === 0" class="empty-chart">Aucun revenu ce mois</div>
          <div v-else class="top-list">
            <div v-for="cat in topIncomes" :key="cat.category_id" class="top-row">
              <div class="top-row-head">
                <span class="top-row-name">{{ cat.category_name }}</span>
                <span class="mono top-row-amount">{{ formatAmount(cat.total) }} <span style="color:var(--ink-4);">({{ categoryPercent(cat.total, 'income') }}%)</span></span>
              </div>
              <div class="ds-progress">
                <div
                  class="ds-progress-bar"
                  style="background:var(--success);"
                  :style="{ width: categoryPercent(cat.total, 'income') + '%' }"
                />
              </div>
            </div>
          </div>
        </div>

      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { getStatistics, getByCategory, getTransactions } = useTransactions()
const { getDashboardData } = useBudgets()
const { currency, ensureProfileLoaded } = useUserProfile()

// État du sélecteur
const now = new Date()
const selectedYear = ref(now.getFullYear())
const selectedMonth = ref(now.getMonth() + 1) // 1-12

// Données
const loading = ref(false)
const error = ref(false)
const stats = ref<{ income: { total: number; count: number }; expense: { total: number; count: number }; net: number } | null>(null)
const prevStats = ref<{ income: { total: number; count: number }; expense: { total: number; count: number }; net: number } | null>(null)
const topExpenses = ref<Array<{ category_id: number; category_name: string; total: number }>>([])
const topIncomes = ref<Array<{ category_id: number; category_name: string; total: number }>>([])
const budgetData = ref<Array<{ category_name: string; prevu: number; reel: number; ecart: number; is_over: boolean; unbudgeted: boolean; is_mandatory_savings?: boolean }>>([])
const monthTransactions = ref<Array<{ date: string; type: string; amount: string }>>([])

// Évolution du solde
const balanceSeries = computed(() => {
  const days = daysInMonth.value
  const dailyNet: Record<string, number> = {}
  for (const t of monthTransactions.value) {
    if (t.type === 'transfer') continue
    const day = t.date.slice(0, 10)
    const amount = parseFloat(t.amount)
    dailyNet[day] = (dailyNet[day] || 0) + (t.type === 'income' ? amount : -amount)
  }
  const points: { day: number; value: number }[] = []
  let cumul = 0
  for (let d = 1; d <= days; d++) {
    const key = `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    cumul += dailyNet[key] || 0
    points.push({ day: d, value: cumul })
  }
  return points
})

const MONTHS_FR = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

const monthLabel = computed(() => `${MONTHS_FR[selectedMonth.value - 1]} ${selectedYear.value}`)
const prevMonthLabel = computed(() => {
  const d = new Date(selectedYear.value, selectedMonth.value - 2, 1)
  return `${MONTHS_FR[d.getMonth()]} ${d.getFullYear()}`
})

const isCurrentMonth = computed(() => selectedYear.value === now.getFullYear() && selectedMonth.value === now.getMonth() + 1)

const net = computed(() => stats.value?.net ?? 0)
const savingsRate = computed(() => {
  const income = stats.value?.income.total ?? 0
  if (!income) return 0
  return Math.round((net.value / income) * 100)
})

const daysInMonth = computed(() => new Date(selectedYear.value, selectedMonth.value, 0).getDate())

const avgPerDay = computed(() => {
  const expense = stats.value?.expense.total ?? 0
  return expense / daysInMonth.value
})

const totalTransactions = computed(() => {
  return (stats.value?.income.count ?? 0) + (stats.value?.expense.count ?? 0)
})

const expenseChange = computed(() => {
  const curr = stats.value?.expense.total ?? 0
  const prev = prevStats.value?.expense.total ?? 0
  if (!prev) return 0
  return ((curr - prev) / prev) * 100
})

const categoryPercent = (total: number, type: 'income' | 'expense') => {
  const base = type === 'expense' ? (stats.value?.expense.total ?? 0) : (stats.value?.income.total ?? 0)
  if (!base) return 0
  return Math.round((total / base) * 100)
}

const formatAmount = (val: number) => {
  return `${val.toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} ${currency.value}`
}

const formatShort = (val: number) => {
  const abs = Math.abs(val)
  const sign = val < 0 ? '-' : ''
  if (abs >= 1000) return `${sign}${(abs / 1000).toFixed(1)}k`
  return `${sign}${Math.round(abs)}`
}

// SVG chart helpers
const CHART_H = 140
const CHART_PAD_TOP = 10
const CHART_PAD_BOT = 10
const seriesMin = computed(() => Math.min(0, ...balanceSeries.value.map(p => p.value)))
const seriesMax = computed(() => Math.max(0, ...balanceSeries.value.map(p => p.value)))
const seriesRange = computed(() => seriesMax.value - seriesMin.value || 1)

const xPct = (day: number) => {
  const total = daysInMonth.value
  return 3 + ((day - 1) / (total - 1 || 1)) * 94
}
const xVB = (day: number) => xPct(day) * 10
const yPx = (value: number) => {
  const ratio = (seriesMax.value - value) / seriesRange.value
  return CHART_PAD_TOP + ratio * (CHART_H - CHART_PAD_TOP - CHART_PAD_BOT)
}
const zeroY = () => yPx(0)
const linePoints = () => balanceSeries.value.map(p => `${xVB(p.day)},${yPx(p.value)}`).join(' ')
const areaPath = () => {
  if (!balanceSeries.value.length) return ''
  const pts = balanceSeries.value
  const first = pts[0]
  const last = pts[pts.length - 1]
  const z = zeroY()
  const line = pts.map(p => `${xVB(p.day)},${yPx(p.value)}`).join(' L ')
  return `M ${xVB(first.day)},${z} L ${line} L ${xVB(last.day)},${z} Z`
}

const dateRange = (year: number, month: number) => {
  const start = `${year}-${String(month).padStart(2, '0')}-01`
  const lastDay = new Date(year, month, 0).getDate()
  const end = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
  return { start, end }
}

const loadData = async () => {
  loading.value = true
  error.value = false

  const { start, end } = dateRange(selectedYear.value, selectedMonth.value)

  // Mois précédent
  const prevDate = new Date(selectedYear.value, selectedMonth.value - 2, 1)
  const prevRange = dateRange(prevDate.getFullYear(), prevDate.getMonth() + 1)

  const [statsRes, prevStatsRes, expCatRes, incCatRes, budgetRes, txRes] = await Promise.all([
    getStatistics({ start_date: start, end_date: end }),
    getStatistics({ start_date: prevRange.start, end_date: prevRange.end }),
    getByCategory({ type: 'expense', start_date: start, end_date: end }),
    getByCategory({ type: 'income', start_date: start, end_date: end }),
    getDashboardData({ year: selectedYear.value, month: selectedMonth.value }),
    getTransactions({ start_date: start, end_date: end, ordering: 'date', page_size: 500 }),
  ])

  if (!statsRes.success) {
    error.value = true
    loading.value = false
    return
  }

  stats.value = statsRes.data
  prevStats.value = prevStatsRes.success ? prevStatsRes.data : null
  topExpenses.value = (expCatRes.data ?? []).slice(0, 5).sort((a, b) => b.total - a.total)
  topIncomes.value = (incCatRes.data ?? []).slice(0, 5).sort((a, b) => b.total - a.total)
  budgetData.value = budgetRes.success ? (budgetRes.data?.categories ?? []) : []
  monthTransactions.value = txRes.data?.results ?? []

  loading.value = false
}

const prevMonth = () => {
  if (selectedMonth.value === 1) {
    selectedMonth.value = 12
    selectedYear.value--
  } else {
    selectedMonth.value--
  }
}

const nextMonth = () => {
  if (isCurrentMonth.value) return
  if (selectedMonth.value === 12) {
    selectedMonth.value = 1
    selectedYear.value++
  } else {
    selectedMonth.value++
  }
}

watch([selectedMonth, selectedYear], loadData)

onMounted(async () => {
  await ensureProfileLoaded()
  await loadData()
})
</script>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp .4s cubic-bezier(.2,.7,.2,1) both; }

/* ── Root ── */
.page-root {
  padding: 16px 16px 80px;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
@media (min-width: 640px) {
  .page-root { padding: 20px 24px 40px; gap: 18px; }
}

/* ── States ── */
.loading-wrap {
  display: flex;
  justify-content: center;
  padding: 64px 0;
}
.error-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px;
  text-align: center;
}

/* ── Hero grid ── */
.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
@media (min-width: 480px) { .hero-grid { grid-template-columns: 1fr 1fr; } }
@media (min-width: 768px) { .hero-grid { grid-template-columns: 1fr 1fr 1fr; gap: 14px; } }

/* ── Stat cards ── */
.stat-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: var(--shadow-sm);
}
@media (min-width: 640px) { .stat-card { padding: 20px 24px; } }

.stat-card--income { border-color: color-mix(in oklab, var(--success) 25%, var(--line)); }
.stat-card--expense { border-color: color-mix(in oklab, var(--danger) 25%, var(--line)); }
.stat-card--net-pos { border-color: color-mix(in oklab, var(--accent) 25%, var(--line)); }
.stat-card--net-neg { border-color: color-mix(in oklab, #f59e0b 30%, var(--line)); }

.stat-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 500;
  margin-bottom: 8px;
}
.stat-amount {
  font-size: 22px;
  font-weight: 500;
  letter-spacing: -0.5px;
  line-height: 1.1;
}
@media (min-width: 640px) { .stat-amount { font-size: 26px; } }
.stat-count { font-size: 12px; color: var(--ink-4); margin-top: 4px; }

/* ── Savings banner ── */
.savings-banner {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: var(--success-soft);
  border: 1px solid color-mix(in oklab, var(--success) 30%, transparent);
  border-radius: var(--radius-lg);
}
.savings-banner-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--success);
  margin: 0;
}
.savings-banner-sub { font-size: 13px; color: var(--success); margin: 4px 0 0; opacity: 0.8; }

/* ── Mini grid ── */
.mini-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
@media (min-width: 640px) { .mini-grid { grid-template-columns: 1fr 1fr 1fr; gap: 14px; } }

.mini-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  box-shadow: var(--shadow-sm);
}
.mini-label { font-size: 11.5px; color: var(--ink-3); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500; }
.mini-value { font-size: 18px; font-weight: 500; color: var(--ink); margin-top: 6px; letter-spacing: -0.3px; }
.mini-sub { font-size: 11px; color: var(--ink-4); margin-top: 3px; }

/* ── Section cards ── */
.section-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: var(--shadow-sm);
}
@media (min-width: 640px) { .section-card { padding: 20px 24px; } }

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.2px;
  display: flex;
  align-items: center;
  gap: 7px;
}
.section-sub { font-size: 12.5px; color: var(--ink-3); margin-top: 2px; }

/* ── SVG chart ── */
.chart-wrap {
  position: relative;
  height: 160px;
}
.chart-labels-y {
  position: absolute;
  inset: 0;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 11px;
  color: var(--ink-4);
  font-family: 'Geist Mono', ui-monospace, monospace;
  padding: 2px 0 2px 2px;
}
.chart-final-label {
  position: absolute;
  right: 8px;
  font-size: 11px;
  font-weight: 600;
  pointer-events: none;
  transform: translateY(-150%);
}
.chart-axis-x {
  position: relative;
  margin-top: 6px;
  height: 14px;
  font-size: 11px;
  color: var(--ink-4);
  font-family: 'Geist Mono', ui-monospace, monospace;
}
.empty-chart {
  padding: 32px 0;
  text-align: center;
  font-size: 13px;
  color: var(--ink-4);
}

/* ── Budget list ── */
.budget-list { display: flex; flex-direction: column; gap: 12px; }
.budget-row { }
.budget-row-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 13.5px;
}
.budget-row-name {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--ink-2);
  font-weight: 500;
  min-width: 0;
  overflow: hidden;
}
.budget-row-name span:first-of-type {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.budget-row-amounts { font-size: 13px; white-space: nowrap; flex-shrink: 0; }

/* Custom warn bar (not in global DS) */
.ds-progress-bar.warn { background: linear-gradient(90deg, #f59e0b, #fb923c); }

/* ── Top grid ── */
.top-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}
@media (min-width: 768px) { .top-grid { grid-template-columns: 1fr 1fr; } }

.top-list { display: flex; flex-direction: column; gap: 14px; }
.top-row { }
.top-row-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}
.top-row-name {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--ink-2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.top-row-amount { font-size: 12.5px; color: var(--ink); white-space: nowrap; flex-shrink: 0; }
</style>
