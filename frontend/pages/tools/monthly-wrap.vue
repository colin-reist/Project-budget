<template>
  <div>
    <!-- Header -->
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Review Mensuel</h1>
        <p class="mt-1 text-gray-600 dark:text-gray-400">Bilan financier du mois sélectionné</p>
      </div>

      <!-- Sélecteur mois/année -->
      <div class="flex items-center gap-2">
        <UButton
          icon="i-heroicons-chevron-left"
          color="gray"
          variant="ghost"
          size="sm"
          aria-label="Mois précédent"
          @click="prevMonth"
        />
        <div class="text-base font-semibold text-gray-900 dark:text-white min-w-[140px] text-center">
          {{ monthLabel }}
        </div>
        <UButton
          icon="i-heroicons-chevron-right"
          color="gray"
          variant="ghost"
          size="sm"
          aria-label="Mois suivant"
          :disabled="isCurrentMonth"
          @click="nextMonth"
        />
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-400" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="flex flex-col items-center py-16 gap-4">
      <UIcon name="i-heroicons-exclamation-circle" class="h-12 w-12 text-red-400" />
      <p class="text-gray-500">Impossible de charger les données</p>
      <UButton size="sm" variant="soft" @click="loadData">Réessayer</UButton>
    </div>

    <template v-else>
      <!-- Cards ligne 1 : revenus, dépenses, net -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <UCard>
          <div class="flex items-center gap-3">
            <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <UIcon name="i-heroicons-arrow-trending-up" class="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Revenus</p>
              <p class="text-xl font-bold text-green-600 dark:text-green-400">{{ formatAmount(stats?.income.total ?? 0) }}</p>
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center gap-3">
            <div class="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <UIcon name="i-heroicons-arrow-trending-down" class="h-5 w-5 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Dépenses</p>
              <p class="text-xl font-bold text-red-600 dark:text-red-400">{{ formatAmount(stats?.expense.total ?? 0) }}</p>
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center gap-3">
            <div :class="['p-2 rounded-lg', net >= 0 ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-orange-100 dark:bg-orange-900/30']">
              <UIcon name="i-heroicons-scale" :class="['h-5 w-5', net >= 0 ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400']" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Net du mois</p>
              <p :class="['text-xl font-bold', net >= 0 ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400']">
                {{ net >= 0 ? '+' : '' }}{{ formatAmount(net) }}
              </p>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Bannière épargne -->
      <div v-if="net > 0" class="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start gap-3">
        <span class="text-2xl">💡</span>
        <div>
          <p class="font-semibold text-green-800 dark:text-green-300">
            Tu pourrais mettre {{ formatAmount(net) }} en épargne ce mois
          </p>
          <p class="text-sm text-green-700 dark:text-green-400 mt-1">
            Soit {{ savingsRate }}% de tes revenus — félicitations !
          </p>
        </div>
      </div>

      <!-- Cards ligne 2 : moy/jour, nb transactions, vs mois précédent -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <UCard>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Dépenses / jour</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white">{{ formatAmount(avgPerDay) }}</p>
          <p class="text-xs text-gray-400 mt-1">sur {{ daysInMonth }} jours</p>
        </UCard>

        <UCard>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Transactions</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white">{{ totalTransactions }}</p>
          <p class="text-xs text-gray-400 mt-1">ce mois-ci</p>
        </UCard>

        <UCard>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">vs mois précédent</p>
          <template v-if="prevStats">
            <p :class="['text-lg font-bold', expenseChange >= 0 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">
              {{ expenseChange >= 0 ? '+' : '' }}{{ expenseChange.toFixed(0) }}% dépenses
            </p>
            <p class="text-xs text-gray-400 mt-1">
              {{ prevMonthLabel }}
            </p>
          </template>
          <p v-else class="text-sm text-gray-400">Pas de données</p>
        </UCard>
      </div>

      <!-- Évolution du solde net -->
      <UCard class="mb-6">
        <template #header>
          <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <UIcon name="i-heroicons-chart-bar" class="h-4 w-4 text-blue-500" />
            Évolution du solde net
          </h2>
        </template>
        <div v-if="balanceSeries.length === 0" class="py-8 text-center text-gray-400 text-sm">Aucune donnée</div>
        <div v-else class="relative" style="height: 160px;">
          <svg width="100%" height="160" viewBox="0 0 1000 160" preserveAspectRatio="none" class="overflow-visible">
            <defs>
              <linearGradient id="balanceGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.02"/>
              </linearGradient>
            </defs>
            <g>
              <!-- Ligne zéro -->
              <line :x1="30" :x2="970" :y1="zeroY()" :y2="zeroY()" stroke="#e5e7eb" stroke-width="1.5" stroke-dasharray="6,4" />
              <!-- Aire sous la courbe -->
              <path :d="areaPath()" fill="url(#balanceGrad)" />
              <!-- Courbe -->
              <polyline :points="linePoints()" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" />
              <!-- Point final -->
              <circle
                v-if="balanceSeries.length"
                :cx="xVB(balanceSeries[balanceSeries.length - 1].day)"
                :cy="yPx(balanceSeries[balanceSeries.length - 1].value)"
                r="5"
                :fill="balanceSeries[balanceSeries.length - 1].value >= 0 ? '#3b82f6' : '#ef4444'"
                stroke="white" stroke-width="2.5"
              />
            </g>
          </svg>
          <!-- Labels en overlay HTML (évite la distortion du viewBox) -->
          <div class="absolute inset-0 pointer-events-none flex flex-col justify-between text-xs text-gray-400 py-1 pl-1">
            <span>{{ formatShort(seriesMax) }}</span>
            <span>{{ formatShort(seriesMin) }}</span>
          </div>
          <div
            class="absolute right-2 text-xs font-semibold pointer-events-none"
            :style="{ top: (yPx(balanceSeries[balanceSeries.length - 1].value) / 160 * 100) + '%', transform: 'translateY(-150%)' }"
            :class="balanceSeries[balanceSeries.length - 1].value >= 0 ? 'text-blue-500' : 'text-red-500'"
          >
            {{ formatShort(balanceSeries[balanceSeries.length - 1].value) }}
          </div>
        </div>
        <!-- Axe des dates -->
        <div class="relative mt-1 text-xs text-gray-400">
          <span class="absolute left-0">1</span>
          <span class="absolute" :style="{ left: xPct(Math.ceil(daysInMonth / 4)) + '%' }">{{ Math.ceil(daysInMonth / 4) }}</span>
          <span class="absolute" :style="{ left: xPct(Math.ceil(daysInMonth / 2)) + '%' }">{{ Math.ceil(daysInMonth / 2) }}</span>
          <span class="absolute" :style="{ left: xPct(Math.ceil(daysInMonth * 3 / 4)) + '%' }">{{ Math.ceil(daysInMonth * 3 / 4) }}</span>
          <span class="absolute right-0">{{ daysInMonth }}</span>
        </div>
        <p class="text-xs text-gray-400 mt-4 text-center">Flux net cumulatif sur le mois (revenus − dépenses)</p>
      </UCard>

      <!-- État des budgets -->
      <UCard v-if="budgetData.length > 0" class="mb-6">
        <template #header>
          <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <UIcon name="i-heroicons-chart-bar-square" class="h-4 w-4 text-purple-500" />
            État des budgets
          </h2>
        </template>
        <div class="space-y-3">
          <div v-for="(b, i) in budgetData" :key="i" class="space-y-1">
            <div class="flex items-center justify-between text-sm">
              <span class="font-medium text-gray-700 dark:text-gray-300 flex items-center gap-1.5 truncate max-w-[55%]">
                <UIcon
                  :name="b.is_over ? 'i-heroicons-exclamation-circle' : 'i-heroicons-check-circle'"
                  :class="b.is_over ? 'text-red-500' : 'text-green-500'"
                  class="h-4 w-4 flex-shrink-0"
                />
                {{ b.category_name }}
                <UBadge v-if="b.unbudgeted" color="gray" variant="subtle" size="xs">hors budget</UBadge>
              </span>
              <span class="text-gray-600 dark:text-gray-400 text-right">
                <span :class="b.is_over ? 'text-red-600 font-semibold' : 'text-gray-700 dark:text-gray-300'">
                  {{ formatAmount(b.reel) }}
                </span>
                <span v-if="b.prevu > 0" class="text-gray-400"> / {{ formatAmount(b.prevu) }}</span>
              </span>
            </div>
            <div v-if="b.prevu > 0" class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-1.5">
              <div
                class="h-1.5 rounded-full transition-all"
                :class="b.is_over ? 'bg-red-500' : (b.reel / b.prevu > 0.8 ? 'bg-orange-400' : 'bg-green-500')"
                :style="{ width: Math.min(100, b.prevu > 0 ? (b.reel / b.prevu * 100) : 0) + '%' }"
              />
            </div>
          </div>
        </div>
      </UCard>

      <!-- Top dépenses par catégorie -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <UCard>
          <template #header>
            <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-trending-down" class="h-4 w-4 text-red-500" />
              Top dépenses
            </h2>
          </template>

          <div v-if="topExpenses.length === 0" class="py-4 text-center text-gray-400 text-sm">
            Aucune dépense ce mois
          </div>
          <div v-else class="space-y-3">
            <div v-for="cat in topExpenses" :key="cat.category_id" class="space-y-1">
              <div class="flex items-center justify-between text-sm">
                <span class="font-medium text-gray-700 dark:text-gray-300 truncate max-w-[60%]">{{ cat.category_name }}</span>
                <span class="text-gray-600 dark:text-gray-400">{{ formatAmount(cat.total) }} ({{ categoryPercent(cat.total, 'expense') }}%)</span>
              </div>
              <div class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                <div
                  class="h-2 rounded-full bg-red-400 dark:bg-red-500 transition-all"
                  :style="{ width: categoryPercent(cat.total, 'expense') + '%' }"
                />
              </div>
            </div>
          </div>
        </UCard>

        <!-- Top revenus par catégorie -->
        <UCard>
          <template #header>
            <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-trending-up" class="h-4 w-4 text-green-500" />
              Top revenus
            </h2>
          </template>

          <div v-if="topIncomes.length === 0" class="py-4 text-center text-gray-400 text-sm">
            Aucun revenu ce mois
          </div>
          <div v-else class="space-y-3">
            <div v-for="cat in topIncomes" :key="cat.category_id" class="space-y-1">
              <div class="flex items-center justify-between text-sm">
                <span class="font-medium text-gray-700 dark:text-gray-300 truncate max-w-[60%]">{{ cat.category_name }}</span>
                <span class="text-gray-600 dark:text-gray-400">{{ formatAmount(cat.total) }} ({{ categoryPercent(cat.total, 'income') }}%)</span>
              </div>
              <div class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                <div
                  class="h-2 rounded-full bg-green-400 dark:bg-green-500 transition-all"
                  :style="{ width: categoryPercent(cat.total, 'income') + '%' }"
                />
              </div>
            </div>
          </div>
        </UCard>
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
