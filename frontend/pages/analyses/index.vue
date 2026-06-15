<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { getMonthlySummary, getByCategory, getTransactions } = useTransactions()
const { getBudgets } = useBudgets()
const { currency, ensureProfileLoaded } = useUserProfile()

// ── Period selector ──────────────────────────────────────────
const period = ref(12)

// ── Date helpers ─────────────────────────────────────────────
const now = new Date()
const currentYear = now.getFullYear()
const currentMonth = now.getMonth() + 1
const lastYear = currentYear - 1

const MONTH_SHORT = ['janv.','févr.','mars','avr.','mai','juin','juil.','août','sept.','oct.','nov.','déc.']
const MONTH_LONG  = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']

function isoMonth(year: number, month: number) {
  return `${year}-${String(month).padStart(2, '0')}`
}

// ── Data ─────────────────────────────────────────────────────
const loading = ref(true)
const loadError = ref(false)

type MonthRecord = Record<number, { month: number; income: number; expense: number; net: number }>
const summaryCurrentYear = ref<MonthRecord | null>(null)
const summaryLastYear    = ref<MonthRecord | null>(null)

type CatRecord = { category_id: number; category_name: string; color: string; total: number; count: number }
const categoryExpenses = ref<CatRecord[]>([])
const budgetsList = ref<any[]>([])
const merchantTxns = ref<any[]>([])

// ── Load ─────────────────────────────────────────────────────
async function loadData() {
  loading.value = true
  loadError.value = false
  try {
    await ensureProfileLoaded()
    const monthStart = `${isoMonth(currentYear, currentMonth)}-01`
    const monthEnd = new Date(currentYear, currentMonth, 0).toISOString().split('T')[0]

    const [s1, s2, cats, txns, bud] = await Promise.all([
      getMonthlySummary(currentYear),
      getMonthlySummary(lastYear),
      getByCategory({ type: 'expense', start_date: monthStart, end_date: monthEnd }),
      getTransactions({ type: 'expense', start_date: monthStart, end_date: monthEnd, page_size: 500 }),
      getBudgets({ year: currentYear, month: currentMonth, period: 'monthly', is_active: true }),
    ])
    summaryCurrentYear.value = s1.data
    summaryLastYear.value    = s2.data
    categoryExpenses.value   = (cats.data || []).sort((a: CatRecord, b: CatRecord) => b.total - a.total)
    merchantTxns.value       = txns.data?.results || []
    budgetsList.value        = bud.data?.results || []
  } catch {
    loadError.value = true
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

// ── Build last-12-months array ────────────────────────────────
const last12Months = computed(() => {
  const arr: { year: number; month: number; label: string; inc: number; exp: number }[] = []
  for (let i = 11; i >= 0; i--) {
    const d = new Date(currentYear, currentMonth - 1 - i, 1)
    const y = d.getFullYear()
    const m = d.getMonth() + 1
    const src = y === currentYear ? summaryCurrentYear.value : summaryLastYear.value
    const row = src?.[m]
    arr.push({ year: y, month: m, label: MONTH_SHORT[d.getMonth()], inc: row?.income ?? 0, exp: row?.expense ?? 0 })
  }
  return arr
})

const chartData = computed(() => last12Months.value.slice(-period.value))

// ── KPIs ─────────────────────────────────────────────────────
const totalIncome  = computed(() => chartData.value.reduce((s, d) => s + d.inc, 0))
const totalExpense = computed(() => chartData.value.reduce((s, d) => s + d.exp, 0))
const savingsRate  = computed(() =>
  totalIncome.value > 0 ? ((totalIncome.value - totalExpense.value) / totalIncome.value * 100).toFixed(1) : '0.0'
)
const avgMonthlyExp = computed(() => period.value > 0 ? totalExpense.value / period.value : 0)

const bestMonth = computed(() => {
  let best = { label: '—', rate: 0 }
  for (const d of last12Months.value) {
    if (d.inc > 0) {
      const r = (d.inc - d.exp) / d.inc * 100
      if (r > best.rate) best = { label: d.label, rate: r }
    }
  }
  return best
})

const topCategoryName  = computed(() => categoryExpenses.value[0]?.category_name ?? '—')
const topCategoryTotal = computed(() => categoryExpenses.value[0]?.total ?? 0)
const currentMonthExpense = computed(() => summaryCurrentYear.value?.[currentMonth]?.expense ?? 0)

// ── Top merchants ────────────────────────────────────────────
const topMerchants = computed(() => {
  const map: Record<string, number> = {}
  for (const t of merchantTxns.value) {
    const key = t.description || '—'
    map[key] = (map[key] || 0) + Math.abs(parseFloat(t.amount) || 0)
  }
  return Object.entries(map).map(([name, total]) => ({ name, total })).sort((a, b) => b.total - a.total).slice(0, 8)
})

// ── Category chart helpers ────────────────────────────────────
const totalCatExpense = computed(() => categoryExpenses.value.reduce((s, c) => s + c.total, 0))

const budgetMap = computed(() => {
  const m: Record<number, number> = {}
  for (const b of budgetsList.value) {
    if (b.category_details?.id != null) m[b.category_details.id] = parseFloat(b.amount) || 0
  }
  return m
})

const topCategories = computed(() =>
  categoryExpenses.value.slice(0, 8).map(c => ({ ...c, budget: budgetMap.value[c.category_id] ?? 0 }))
)

// ── Savings rate per month ────────────────────────────────────
const savingsRates = computed(() =>
  last12Months.value.map(d => ({ label: d.label, rate: d.inc > 0 ? (d.inc - d.exp) / d.inc * 100 : 0 }))
)
const avgSavingsRate = computed(() => {
  const valid = savingsRates.value.filter(r => r.rate !== 0)
  return valid.length ? valid.reduce((s, r) => s + r.rate, 0) / valid.length : 0
})

// ── Chart hover states ────────────────────────────────────────
const barHov   = ref<number | null>(null)
const savHov   = ref<number | null>(null)
const donutHov = ref<number | null>(null)

// ── Bar chart geometry ────────────────────────────────────────
const BW = 800, BH = 200, BP = { l: 46, r: 14, t: 20, b: 28 }

const barMax = computed(() => {
  const m = Math.max(...chartData.value.map(d => Math.max(d.inc, d.exp))) * 1.1
  return m > 0 ? m : 1
})
function bX(i: number) {
  const gW = (BW - BP.l - BP.r) / (chartData.value.length || 1)
  return BP.l + i * gW + gW / 2
}
function bY(v: number) { return BP.t + (1 - v / barMax.value) * (BH - BP.t - BP.b) }

const barRects = computed(() => {
  const n = chartData.value.length || 1
  const gW = (BW - BP.l - BP.r) / n
  const bw = gW * 0.35, gap = gW * 0.08
  return chartData.value.map((d, i) => {
    const cx = bX(i)
    return {
      d, i, bw,
      incX: cx - bw - gap / 2, incY: bY(d.inc), incH: (BH - BP.t - BP.b) * (d.inc / barMax.value),
      expX: cx + gap / 2,      expY: bY(d.exp), expH: (BH - BP.t - BP.b) * (d.exp / barMax.value),
      zoneX: BP.l + i * gW, zoneW: gW,
    }
  })
})

const barLinePoints = computed(() =>
  chartData.value.map((d, i) => ({
    x: bX(i),
    y: bY(d.inc > 0 ? (d.inc - d.exp) / d.inc * barMax.value * 0.55 + barMax.value * 0.08 : barMax.value * 0.08),
  }))
)
const barLinePath = computed(() =>
  barLinePoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
)

// ── Savings line chart geometry ───────────────────────────────
const SW = 700, SH = 130, SP = { l: 38, r: 14, t: 18, b: 26 }

const savMax = computed(() => {
  const m = Math.max(...savingsRates.value.map(r => r.rate)) * 1.15
  return m > 0 ? m : 40
})
function sX(i: number) {
  const n = savingsRates.value.length
  return n > 1 ? SP.l + (i / (n - 1)) * (SW - SP.l - SP.r) : SW / 2
}
function sY(v: number) { return SP.t + (1 - v / savMax.value) * (SH - SP.t - SP.b) }

const savPath = computed(() =>
  savingsRates.value.map((r, i) => `${i === 0 ? 'M' : 'L'} ${sX(i).toFixed(1)} ${sY(r.rate).toFixed(1)}`).join(' ')
)
const savArea = computed(() => {
  const n = savingsRates.value.length
  return `${savPath.value} L ${sX(n - 1).toFixed(1)} ${SH - SP.b} L ${sX(0).toFixed(1)} ${SH - SP.b} Z`
})

// ── Donut ─────────────────────────────────────────────────────
const DS = 150, DSTK = 24
const DR = (DS - DSTK) / 2
const DC = 2 * Math.PI * DR

const donutSegs = computed(() => {
  if (!totalCatExpense.value) return []
  let offset = 0
  return categoryExpenses.value.slice(0, 6).map((c, i) => {
    const pct = (c.total / totalCatExpense.value) * 100
    const dash = (pct / 100) * DC
    const seg = { ...c, pct, dash, offset, i }
    offset += pct
    return seg
  })
})

// ── Formatters ────────────────────────────────────────────────
function fmt(v: number) {
  return `${v.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency.value}`
}
function fmtS(v: number) {
  const a = Math.abs(v)
  if (a >= 1000) return (v < 0 ? '−' : '') + (a / 1000).toFixed(a % 1000 === 0 ? 0 : 1) + 'k'
  return Math.round(v).toString()
}

const currentMonthLabel = computed(() => `${MONTH_LONG[currentMonth - 1]} ${currentYear}`)
</script>

<template>
  <div class="page-root fade-up">

    <!-- Header -->
    <PageHeader title="Analyses" subtitle="Tendances de revenus, dépenses et épargne">
      <template #actions>
        <div class="period-picker">
          <button v-for="p in [3, 6, 12]" :key="p" class="period-btn" :class="{ active: period === p }" @click="period = p">{{ p }} mois</button>
        </div>
      </template>
    </PageHeader>

    <!-- Loading -->
    <div v-if="loading" class="loading-wrap">
      <UIcon name="i-heroicons-arrow-path" class="spin" style="width:28px;height:28px;color:var(--ink-4);" />
    </div>

    <!-- Error -->
    <div v-else-if="loadError" class="section-card" style="text-align:center;padding:40px;">
      <UIcon name="i-heroicons-exclamation-circle" style="width:40px;height:40px;color:var(--danger);" />
      <p style="font-size:14px;color:var(--ink-3);margin:8px 0 0;">Impossible de charger les données</p>
      <button class="ds-btn ds-btn-secondary" style="margin-top:12px;" @click="loadData">Réessayer</button>
    </div>

    <template v-else>

      <!-- KPI Row -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon" style="background:color-mix(in oklab,var(--accent) 12%,var(--surface));color:var(--accent);border-color:color-mix(in oklab,var(--accent) 18%,transparent);">
            <UIcon name="i-heroicons-arrow-trending-up" style="width:14px;height:14px;" />
          </div>
          <div class="kpi-value mono">{{ savingsRate }}%</div>
          <div class="kpi-label">Taux d'épargne · {{ period }} mois</div>
          <div class="kpi-sub">{{ fmt(totalIncome - totalExpense) }} mis de côté</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:color-mix(in oklab,#a855f7 12%,var(--surface));color:#a855f7;border-color:color-mix(in oklab,#a855f7 18%,transparent);">
            <UIcon name="i-heroicons-arrow-trending-down" style="width:14px;height:14px;" />
          </div>
          <div class="kpi-value mono">{{ fmt(avgMonthlyExp) }}</div>
          <div class="kpi-label">Dépenses moy. / mois</div>
          <div class="kpi-sub">Sur {{ period }} mois · {{ fmt(totalExpense) }} total</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:color-mix(in oklab,#16a34a 12%,var(--surface));color:#16a34a;border-color:color-mix(in oklab,#16a34a 18%,transparent);">
            <UIcon name="i-heroicons-banknotes" style="width:14px;height:14px;" />
          </div>
          <div class="kpi-value mono">{{ bestMonth.rate.toFixed(0) }}% · {{ bestMonth.label }}</div>
          <div class="kpi-label">Meilleur mois · épargne</div>
          <div class="kpi-sub">Taux d'épargne le plus élevé sur 12 mois</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background:color-mix(in oklab,#f97316 12%,var(--surface));color:#f97316;border-color:color-mix(in oklab,#f97316 18%,transparent);">
            <UIcon name="i-heroicons-chart-bar" style="width:14px;height:14px;" />
          </div>
          <div class="kpi-value mono" style="font-size:18px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ topCategoryName }}</div>
          <div class="kpi-label">Principal poste · {{ currentMonthLabel }}</div>
          <div class="kpi-sub">
            {{ fmt(topCategoryTotal) }}
            <template v-if="currentMonthExpense > 0"> · {{ (topCategoryTotal / currentMonthExpense * 100).toFixed(0) }}% des dépenses</template>
          </div>
        </div>
      </div>

      <!-- Revenus vs Dépenses -->
      <div class="section-card">
        <div class="section-head">
          <div>
            <span class="section-title">Revenus vs Dépenses</span>
            <span class="section-sub">Par mois</span>
          </div>
          <div class="period-picker">
            <button v-for="p in [3, 6, 12]" :key="p" class="period-btn" :class="{ active: period === p }" @click="period = p">{{ p }} mois</button>
          </div>
        </div>

        <div v-if="chartData.length > 0" class="chart-scroll">
          <svg :viewBox="`0 0 ${BW} ${BH}`" style="width:100%;height:auto;display:block;min-width:320px;">
            <!-- Grid -->
            <line v-for="g in [0.25, 0.5, 0.75, 1]" :key="g" :x1="BP.l" :y1="bY(barMax * g)" :x2="BW - BP.r" :y2="bY(barMax * g)" stroke="var(--line)" stroke-width="1" stroke-dasharray="2 3" />
            <!-- Y labels -->
            <text v-for="g in [0, 0.5, 1]" :key="g" :x="BP.l - 6" :y="bY(barMax * (1 - g)) + 3" font-size="9.5" text-anchor="end" fill="var(--ink-3)" font-family="Geist Mono, monospace">{{ fmtS(barMax * (1 - g)) }}</text>
            <!-- Bars -->
            <g v-for="r in barRects" :key="r.i" @mouseenter="barHov = r.i" @mouseleave="barHov = null" style="cursor:default;">
              <rect :x="r.zoneX" :y="BP.t" :width="r.zoneW" :height="BH - BP.t - BP.b" :fill="barHov === r.i ? 'color-mix(in oklab,var(--accent) 4%,transparent)' : 'transparent'" />
              <rect :x="r.incX" :y="r.incY" :width="r.bw" :height="r.incH" :fill="barHov === r.i ? 'var(--accent)' : 'color-mix(in oklab,var(--accent) 55%,transparent)'" rx="2" style="transition:fill 0.15s;" />
              <rect :x="r.expX" :y="r.expY" :width="r.bw" :height="r.expH" :fill="barHov === r.i ? 'var(--danger)' : 'color-mix(in oklab,var(--danger) 55%,transparent)'" rx="2" style="transition:fill 0.15s;" />
              <text :x="bX(r.i)" :y="BH - 8" font-size="9.5" text-anchor="middle" :fill="barHov === r.i ? 'var(--ink)' : 'var(--ink-3)'" font-family="Geist Mono, monospace">{{ r.d.label }}</text>
            </g>
            <!-- Savings line -->
            <path :d="barLinePath" fill="none" stroke="#f59e0b" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="4 3" opacity="0.8" />
            <circle v-for="(p, i) in barLinePoints" :key="i" :cx="p.x" :cy="p.y" :r="barHov === i ? 4 : 2.5" fill="#f59e0b" stroke="var(--surface)" stroke-width="1.5" />
            <!-- Tooltip -->
            <template v-if="barHov !== null && chartData[barHov]">
              <rect :x="Math.min(BW - 122, Math.max(10, bX(barHov) - 56))" :y="BP.t - 2" width="116" height="78" rx="6" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="1" filter="drop-shadow(0 2px 6px rgba(0,0,0,0.1))" />
              <text :x="Math.min(BW - 122, Math.max(10, bX(barHov) - 56)) + 10" :y="BP.t + 14" font-size="10.5" font-weight="600" fill="var(--ink)" font-family="Geist, sans-serif">{{ chartData[barHov].label }}</text>
              <text :x="Math.min(BW - 122, Math.max(10, bX(barHov) - 56)) + 10" :y="BP.t + 30" font-size="9.5" fill="var(--ink-3)" font-family="Geist, sans-serif">Revenus</text>
              <text :x="Math.min(BW - 122, Math.max(10, bX(barHov) - 56)) + 106" :y="BP.t + 30" font-size="9.5" text-anchor="end" fill="var(--accent)" font-family="Geist Mono, monospace" font-weight="500">{{ fmtS(chartData[barHov].inc) }}</text>
              <text :x="Math.min(BW - 122, Math.max(10, bX(barHov) - 56)) + 10" :y="BP.t + 46" font-size="9.5" fill="var(--ink-3)" font-family="Geist, sans-serif">Dépenses</text>
              <text :x="Math.min(BW - 122, Math.max(10, bX(barHov) - 56)) + 106" :y="BP.t + 46" font-size="9.5" text-anchor="end" fill="var(--danger)" font-family="Geist Mono, monospace" font-weight="500">{{ fmtS(chartData[barHov].exp) }}</text>
              <line :x1="Math.min(BW - 122, Math.max(10, bX(barHov) - 56)) + 8" :y1="BP.t + 54" :x2="Math.min(BW - 122, Math.max(10, bX(barHov) - 56)) + 108" :y2="BP.t + 54" stroke="var(--line)" stroke-width="0.75" />
              <text :x="Math.min(BW - 122, Math.max(10, bX(barHov) - 56)) + 10" :y="BP.t + 68" font-size="9.5" fill="var(--ink-3)" font-family="Geist, sans-serif">Taux d'épargne</text>
              <text :x="Math.min(BW - 122, Math.max(10, bX(barHov) - 56)) + 106" :y="BP.t + 68" font-size="9.5" text-anchor="end" fill="#16a34a" font-family="Geist Mono, monospace" font-weight="600">{{ chartData[barHov].inc > 0 ? ((chartData[barHov].inc - chartData[barHov].exp) / chartData[barHov].inc * 100).toFixed(1) : '0.0' }}%</text>
            </template>
          </svg>
        </div>
        <div v-else class="empty-chart">Pas de données pour cette période</div>

        <div class="chart-legend">
          <span class="legend-item"><span class="legend-swatch" style="background:var(--accent);" />Revenus</span>
          <span class="legend-item"><span class="legend-swatch" style="background:var(--danger);" />Dépenses</span>
          <span class="legend-item"><span class="legend-dash" />Taux d'épargne</span>
        </div>
      </div>

      <!-- Donut + Category bars -->
      <div class="two-col-grid">

        <!-- Donut -->
        <div class="section-card">
          <div class="section-head">
            <span class="section-title">Répartition</span>
            <span class="section-sub">{{ currentMonthLabel }}</span>
          </div>
          <div v-if="donutSegs.length > 0" class="donut-wrap">
            <div class="donut-svg-wrap">
              <svg :width="DS" :height="DS" :viewBox="`0 0 ${DS} ${DS}`" style="transform:rotate(-90deg);display:block;flex-shrink:0;">
                <circle
                  v-for="seg in donutSegs" :key="seg.i"
                  :cx="DS / 2" :cy="DS / 2" :r="DR"
                  fill="none" :stroke="seg.color || 'var(--accent)'"
                  :stroke-width="donutHov === seg.i ? DSTK + 3 : DSTK"
                  :stroke-dasharray="`${seg.dash - 1} ${DC - seg.dash + 1}`"
                  :stroke-dashoffset="-seg.offset * (DC / 100)"
                  stroke-linecap="butt"
                  @mouseenter="donutHov = seg.i" @mouseleave="donutHov = null"
                  style="transition:stroke-width 0.15s,opacity 0.15s;cursor:pointer;"
                  :style="{ opacity: donutHov !== null && donutHov !== seg.i ? 0.45 : 1 }"
                />
              </svg>
              <div class="donut-center">
                <div class="mono" style="font-size:15px;font-weight:500;color:var(--ink);letter-spacing:-0.4px;">{{ fmt(totalCatExpense) }}</div>
                <div style="font-size:9px;color:var(--ink-4);margin-top:2px;text-transform:uppercase;letter-spacing:0.5px;">dépensé</div>
              </div>
            </div>
            <div class="donut-legend">
              <div v-for="seg in donutSegs" :key="seg.i" class="donut-row">
                <span class="donut-swatch" :style="{ background: seg.color || 'var(--accent)' }" />
                <span class="donut-name">{{ seg.category_name }}</span>
                <span class="mono donut-amt">{{ fmt(seg.total) }}</span>
                <span class="donut-pct">{{ seg.pct.toFixed(0) }}%</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-chart">Pas de dépenses ce mois</div>
        </div>

        <!-- Category bars -->
        <div class="section-card">
          <div class="section-head">
            <span class="section-title">Top catégories</span>
            <span class="section-sub">{{ currentMonthLabel }}</span>
          </div>
          <div class="hbars-wrap">
            <div v-for="cat in topCategories" :key="cat.category_id" class="hbar-row">
              <div class="hbar-label">{{ cat.category_name }}</div>
              <div style="flex:1;">
                <div class="hbar-track">
                  <div class="hbar-fill" :style="{
                    width: `${Math.min(100, topCategories[0]?.total ? (cat.total / topCategories[0].total) * 100 : 0)}%`,
                    background: cat.budget > 0 && cat.total > cat.budget ? 'var(--danger)' : (cat.color || 'var(--accent)'),
                  }" />
                  <div v-if="cat.budget > 0" class="hbar-budget" :style="{ left: `${Math.min(100, topCategories[0]?.total ? (cat.budget / topCategories[0].total) * 100 : 0)}%` }" />
                </div>
              </div>
              <div class="hbar-right">
                <span class="mono" :style="{ color: cat.budget > 0 && cat.total > cat.budget ? 'var(--danger)' : 'var(--ink)', fontSize: '12.5px', fontWeight: 500 }">{{ fmt(cat.total) }}</span>
                <span v-if="cat.budget > 0" style="font-size:10.5px;color:var(--ink-3);margin-left:4px;">{{ (cat.total / cat.budget * 100).toFixed(0) }}%</span>
              </div>
            </div>
            <div v-if="topCategories.length === 0" class="empty-chart">Aucune dépense ce mois</div>
          </div>
        </div>
      </div>

      <!-- Savings rate + Top merchants -->
      <div class="two-col-grid-rev">

        <!-- Savings line -->
        <div class="section-card">
          <div class="section-head">
            <span class="section-title">Taux d'épargne mensuel</span>
            <span class="section-sub">Revenus − Dépenses / Revenus · 12 mois</span>
          </div>
          <div class="chart-scroll">
            <svg :viewBox="`0 0 ${SW} ${SH}`" style="width:100%;height:auto;display:block;min-width:280px;">
              <defs>
                <linearGradient id="savGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0" stop-color="#16a34a" stop-opacity="0.2" />
                  <stop offset="1" stop-color="#16a34a" stop-opacity="0" />
                </linearGradient>
              </defs>
              <line v-for="g in [0.25, 0.5, 0.75, 1]" :key="g" :x1="SP.l" :y1="SP.t + g * (SH - SP.t - SP.b)" :x2="SW - SP.r" :y2="SP.t + g * (SH - SP.t - SP.b)" stroke="var(--line)" stroke-width="1" stroke-dasharray="2 3" />
              <text v-for="g in [0, 0.5, 1]" :key="g" :x="SP.l - 6" :y="sY(savMax * (1 - g)) + 3" font-size="9.5" text-anchor="end" fill="var(--ink-3)" font-family="Geist Mono, monospace">{{ (savMax * (1 - g)).toFixed(0) }}%</text>
              <line :x1="SP.l" :y1="sY(avgSavingsRate)" :x2="SW - SP.r" :y2="sY(avgSavingsRate)" stroke="#f59e0b" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.7" />
              <text :x="SW - SP.r - 4" :y="sY(avgSavingsRate) - 4" font-size="9" text-anchor="end" fill="#b45309" font-family="Geist, sans-serif">moy. {{ avgSavingsRate.toFixed(1) }}%</text>
              <path :d="savArea" fill="url(#savGrad)" />
              <path :d="savPath" fill="none" stroke="#16a34a" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" />
              <g v-for="(r, i) in savingsRates" :key="i" @mouseenter="savHov = i" @mouseleave="savHov = null" style="cursor:crosshair;">
                <rect :x="sX(i) - (SW - SP.l - SP.r) / savingsRates.length / 2" :y="SP.t" :width="(SW - SP.l - SP.r) / savingsRates.length" :height="SH - SP.t - SP.b" fill="transparent" />
                <circle :cx="sX(i)" :cy="sY(r.rate)" :r="savHov === i ? 5 : 3" fill="#16a34a" stroke="var(--surface)" :stroke-width="savHov === i ? 2 : 1.5" />
                <template v-if="savHov === i">
                  <line :x1="sX(i)" :y1="SP.t" :x2="sX(i)" :y2="SH - SP.b" stroke="#16a34a" stroke-width="1" stroke-dasharray="2 2" opacity="0.4" />
                  <rect :x="Math.min(SW - 96, sX(i) - 44)" :y="sY(r.rate) - 40" width="88" height="32" rx="5" fill="var(--surface)" stroke="var(--line-strong)" stroke-width="1" filter="drop-shadow(0 2px 4px rgba(0,0,0,0.08))" />
                  <text :x="Math.min(SW - 52, sX(i))" :y="sY(r.rate) - 24" font-size="10" text-anchor="middle" font-weight="600" fill="var(--ink)" font-family="Geist, sans-serif">{{ r.label }}</text>
                  <text :x="Math.min(SW - 52, sX(i))" :y="sY(r.rate) - 13" font-size="9.5" text-anchor="middle" fill="#16a34a" font-family="Geist Mono, monospace" font-weight="500">{{ r.rate.toFixed(1) }}%</text>
                </template>
              </g>
              <text v-for="(r, i) in savingsRates" :key="i" :x="sX(i)" :y="SH - 8" font-size="9.5" text-anchor="middle" :fill="savHov === i ? 'var(--ink)' : 'var(--ink-3)'" font-family="Geist Mono, monospace">{{ r.label }}</text>
            </svg>
          </div>
        </div>

        <!-- Top merchants -->
        <div class="section-card">
          <div class="section-head">
            <span class="section-title">Top marchands</span>
            <span class="section-sub">{{ currentMonthLabel }}</span>
          </div>
          <div v-if="topMerchants.length > 0" class="merchants-list">
            <div v-for="(m, i) in topMerchants" :key="m.name" class="merchant-row" :style="{ borderBottom: i < topMerchants.length - 1 ? '1px solid var(--line)' : 'none' }">
              <span class="mono merchant-rank">{{ String(i + 1).padStart(2, '0') }}</span>
              <div class="merchant-avatar" :style="{ background: `hsl(${(i * 47 + 210) % 360}, 62%, 94%)`, color: `hsl(${(i * 47 + 210) % 360}, 55%, 35%)` }">{{ m.name.charAt(0).toUpperCase() }}</div>
              <span class="merchant-name">{{ m.name }}</span>
              <span class="mono" style="font-size:12.5px;color:var(--ink);font-weight:500;flex-shrink:0;">{{ fmt(m.total) }}</span>
            </div>
          </div>
          <div v-else class="empty-chart">Aucune dépense ce mois</div>
        </div>
      </div>

      <!-- Observations -->
      <div>
        <div class="section-head" style="margin-bottom:12px;">
          <span class="section-title">Observations</span>
          <span class="section-sub">{{ currentMonthLabel }}</span>
        </div>
        <div class="insights-grid">
          <div class="insight-card insight-ok">
            <div class="insight-icon" style="color:#16a34a;border-color:color-mix(in oklab,#16a34a 20%,var(--line));">
              <UIcon name="i-heroicons-arrow-trending-up" style="width:14px;height:14px;" />
            </div>
            <div class="insight-body">
              <div class="insight-title">Taux d'épargne</div>
              <div class="insight-text">
                <template v-if="parseFloat(savingsRate) >= avgSavingsRate">
                  Votre taux d'épargne de <strong>{{ savingsRate }}%</strong> est supérieur à votre moyenne sur 12 mois ({{ avgSavingsRate.toFixed(1) }}%).
                </template>
                <template v-else>
                  Votre taux d'épargne de <strong>{{ savingsRate }}%</strong> est en dessous de votre moyenne sur 12 mois ({{ avgSavingsRate.toFixed(1) }}%).
                </template>
              </div>
            </div>
          </div>

          <div class="insight-card" :class="topCategories[0]?.budget > 0 && topCategories[0]?.total > topCategories[0]?.budget ? 'insight-warn' : 'insight-info'">
            <div class="insight-icon"
              :style="topCategories[0]?.budget > 0 && topCategories[0]?.total > topCategories[0]?.budget
                ? { color: '#b45309', borderColor: 'color-mix(in oklab,#f59e0b 24%,var(--line))' }
                : { color: 'var(--accent)', borderColor: 'color-mix(in oklab,var(--accent) 18%,var(--line))' }">
              <UIcon name="i-heroicons-shopping-cart" style="width:14px;height:14px;" />
            </div>
            <div class="insight-body">
              <div class="insight-title">{{ topCategoryName }}</div>
              <div class="insight-text">
                <template v-if="topCategories[0]?.budget > 0 && topCategories[0]?.total > topCategories[0]?.budget">
                  La catégorie <strong>{{ topCategoryName }}</strong> dépasse le budget de {{ ((topCategories[0].total / topCategories[0].budget - 1) * 100).toFixed(0) }}% ({{ fmt(topCategories[0].total) }} vs {{ fmt(topCategories[0].budget) }}).
                </template>
                <template v-else-if="topCategoryName !== '—'">
                  <strong>{{ topCategoryName }}</strong> est votre principale dépense ce mois ({{ fmt(topCategoryTotal) }}).
                </template>
                <template v-else>Aucune dépense enregistrée ce mois.</template>
              </div>
            </div>
          </div>

          <div class="insight-card insight-info">
            <div class="insight-icon" style="color:var(--accent);border-color:color-mix(in oklab,var(--accent) 18%,var(--line));">
              <UIcon name="i-heroicons-calendar-days" style="width:14px;height:14px;" />
            </div>
            <div class="insight-body">
              <div class="insight-title">Tendance sur {{ period }} mois</div>
              <div class="insight-text">
                Revenus moyens <strong>{{ fmt(totalIncome / period) }}</strong>/mois, dépenses <strong>{{ fmt(avgMonthlyExp) }}</strong>/mois — surplus de {{ fmt((totalIncome - totalExpense) / period) }}/mois.
              </div>
            </div>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp .4s cubic-bezier(.2,.7,.2,1) both; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Page root ───────────────────────────────────────────────── */
.page-root {
  padding: 16px 16px 80px;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
@media (min-width: 640px) { .page-root { padding: 20px 24px 60px; gap: 18px; } }



/* ── Period picker ───────────────────────────────────────────── */
.period-picker { display: flex; gap: 3px; padding: 3px; background: var(--surface); border: 1px solid var(--line); border-radius: 9px; box-shadow: var(--shadow-sm); }
.period-btn { height: 28px; padding: 0 12px; font-size: 12px; font-weight: 500; background: transparent; color: var(--ink-3); border: 1px solid transparent; border-radius: 6px; cursor: pointer; transition: all 0.15s; }
.period-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }

/* ── KPI grid ────────────────────────────────────────────────── */
.kpi-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
@media (min-width: 768px) { .kpi-grid { grid-template-columns: repeat(4, 1fr); } }
.kpi-card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 6px; }
.kpi-icon { width: 30px; height: 30px; border-radius: 8px; display: grid; place-items: center; border: 1px solid transparent; align-self: flex-start; }
.kpi-value { font-size: 22px; font-weight: 500; letter-spacing: -0.6px; color: var(--ink); line-height: 1.1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.kpi-label { font-size: 12px; color: var(--ink-3); }
.kpi-sub { font-size: 11.5px; color: var(--ink-4); padding-top: 6px; border-top: 1px solid var(--line); }

/* ── Section card ────────────────────────────────────────────── */
.section-card { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 18px 20px; box-shadow: var(--shadow-sm); }
.section-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.section-title { font-size: 14.5px; font-weight: 600; color: var(--ink); letter-spacing: -0.2px; }
.section-sub { font-size: 12px; color: var(--ink-3); margin-left: 8px; }

/* ── Chart ───────────────────────────────────────────────────── */
.chart-scroll { overflow-x: auto; }
.empty-chart { font-size: 13px; color: var(--ink-4); padding: 24px 0; text-align: center; }
.chart-legend { display: flex; gap: 16px; margin-top: 8px; flex-wrap: wrap; padding-left: 44px; }
.legend-item { display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; color: var(--ink-3); }
.legend-swatch { width: 16px; height: 3px; border-radius: 2px; flex-shrink: 0; }
.legend-dash { width: 16px; height: 0; border-bottom: 2px dashed #f59e0b; flex-shrink: 0; margin-bottom: 1px; }

/* ── Two-col grids ───────────────────────────────────────────── */
.two-col-grid, .two-col-grid-rev { display: grid; grid-template-columns: 1fr; gap: 16px; }
@media (min-width: 900px) {
  .two-col-grid     { grid-template-columns: 320px 1fr; }
  .two-col-grid-rev { grid-template-columns: 1fr 320px; }
}

/* ── Donut ───────────────────────────────────────────────────── */
.donut-wrap { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.donut-svg-wrap { position: relative; flex-shrink: 0; }
.donut-center { position: absolute; inset: 0; display: grid; place-items: center; pointer-events: none; text-align: center; }
.donut-legend { flex: 1; display: flex; flex-direction: column; gap: 10px; min-width: 140px; }
.donut-row { display: flex; align-items: center; gap: 8px; }
.donut-swatch { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
.donut-name { flex: 1; font-size: 12.5px; color: var(--ink-2); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.donut-amt { font-size: 12px; color: var(--ink); font-weight: 500; }
.donut-pct { font-size: 11px; color: var(--ink-4); min-width: 30px; text-align: right; }

/* ── H-bars ──────────────────────────────────────────────────── */
.hbars-wrap { display: flex; flex-direction: column; gap: 10px; }
.hbar-row { display: flex; align-items: center; gap: 10px; }
.hbar-label { min-width: 100px; max-width: 130px; font-size: 12px; color: var(--ink-2); font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hbar-track { height: 7px; border-radius: 4px; background: var(--surface-2); border: 1px solid var(--line); overflow: hidden; position: relative; }
.hbar-fill { position: absolute; inset: 0; height: 100%; border-radius: 4px; transition: width 0.5s cubic-bezier(.2,.7,.2,1); }
.hbar-budget { position: absolute; top: 0; bottom: 0; width: 1.5px; background: var(--ink-3); opacity: 0.5; }
.hbar-right { min-width: 80px; text-align: right; white-space: nowrap; flex-shrink: 0; }

/* ── Merchants ───────────────────────────────────────────────── */
.merchants-list { display: flex; flex-direction: column; }
.merchant-row { display: flex; align-items: center; gap: 10px; padding: 9px 0; }
.merchant-rank { width: 20px; font-size: 10.5px; color: var(--ink-4); font-weight: 500; text-align: right; flex-shrink: 0; }
.merchant-avatar { width: 28px; height: 28px; border-radius: 7px; flex-shrink: 0; border: 1px solid var(--line); display: grid; place-items: center; font-size: 11px; font-weight: 600; }
.merchant-name { flex: 1; font-size: 13px; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ── Insights ────────────────────────────────────────────────── */
.insights-grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
@media (min-width: 768px) { .insights-grid { grid-template-columns: repeat(3, 1fr); } }
.insight-card { padding: 14px 16px; border-radius: 10px; display: flex; gap: 12px; align-items: flex-start; border: 1px solid var(--line); }
.insight-ok   { background: color-mix(in oklab, #16a34a 8%, var(--surface)); border-color: color-mix(in oklab, #16a34a 18%, var(--line)); }
.insight-warn { background: color-mix(in oklab, #f59e0b 8%, var(--surface)); border-color: color-mix(in oklab, #f59e0b 22%, var(--line)); }
.insight-info { background: color-mix(in oklab, var(--accent) 7%, var(--surface)); border-color: color-mix(in oklab, var(--accent) 16%, var(--line)); }
.insight-icon { width: 28px; height: 28px; border-radius: 7px; background: var(--surface); border: 1px solid; display: grid; place-items: center; flex-shrink: 0; margin-top: 1px; }
.insight-body { flex: 1; }
.insight-title { font-size: 13px; font-weight: 600; color: var(--ink); margin-bottom: 3px; }
.insight-text { font-size: 12.5px; color: var(--ink-3); line-height: 1.5; }

/* ── Misc ────────────────────────────────────────────────────── */
.loading-wrap { display: flex; justify-content: center; padding: 60px 0; }
</style>
