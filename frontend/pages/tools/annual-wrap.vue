<template>
  <div>
    <!-- Header -->
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Bilan Annuel</h1>
        <p class="mt-1 text-gray-600 dark:text-gray-400">Vue d'ensemble de vos finances sur l'année</p>
      </div>

      <!-- Sélecteur année -->
      <div class="flex items-center gap-2">
        <UButton
          icon="i-heroicons-chevron-left"
          color="gray"
          variant="ghost"
          size="sm"
          aria-label="Année précédente"
          @click="selectedYear--"
        />
        <div class="text-base font-semibold text-gray-900 dark:text-white min-w-[60px] text-center">
          {{ selectedYear }}
        </div>
        <UButton
          icon="i-heroicons-chevron-right"
          color="gray"
          variant="ghost"
          size="sm"
          aria-label="Année suivante"
          :disabled="selectedYear >= currentYear"
          @click="selectedYear++"
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
      <!-- Cards ligne 1 : totaux annuels -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <UCard>
          <div class="flex items-center gap-3">
            <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <UIcon name="i-heroicons-arrow-trending-up" class="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Revenus totaux</p>
              <p class="text-xl font-bold text-green-600 dark:text-green-400">{{ formatAmount(totalIncome) }}</p>
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center gap-3">
            <div class="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <UIcon name="i-heroicons-arrow-trending-down" class="h-5 w-5 text-red-600 dark:text-red-400" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Dépenses totales</p>
              <p class="text-xl font-bold text-red-600 dark:text-red-400">{{ formatAmount(totalExpense) }}</p>
            </div>
          </div>
        </UCard>

        <UCard>
          <div class="flex items-center gap-3">
            <div :class="['p-2 rounded-lg', totalNet >= 0 ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-orange-100 dark:bg-orange-900/30']">
              <UIcon name="i-heroicons-scale" :class="['h-5 w-5', totalNet >= 0 ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400']" />
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Net annuel</p>
              <p :class="['text-xl font-bold', totalNet >= 0 ? 'text-blue-600 dark:text-blue-400' : 'text-orange-600 dark:text-orange-400']">
                {{ totalNet >= 0 ? '+' : '' }}{{ formatAmount(totalNet) }}
              </p>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Cards ligne 2 : moyennes mensuelles -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <UCard>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Moy. revenus / mois</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white">{{ formatAmount(avgIncome) }}</p>
          <p class="text-xs text-gray-400 mt-1">sur {{ monthsWithData }} mois</p>
        </UCard>

        <UCard>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Moy. dépenses / mois</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white">{{ formatAmount(avgExpense) }}</p>
          <p class="text-xs text-gray-400 mt-1">sur {{ monthsWithData }} mois</p>
        </UCard>

        <UCard>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Moy. épargne / mois</p>
          <p :class="['text-lg font-bold', avgNet >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400']">
            {{ avgNet >= 0 ? '+' : '' }}{{ formatAmount(avgNet) }}
          </p>
          <p class="text-xs text-gray-400 mt-1">sur {{ monthsWithData }} mois</p>
        </UCard>
      </div>

      <!-- Meilleur / Pire mois -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <UCard v-if="bestMonth">
          <div class="flex items-center gap-3">
            <span class="text-2xl">🏆</span>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Meilleur mois</p>
              <p class="text-base font-bold text-green-600 dark:text-green-400">
                {{ monthName(bestMonth.month) }} — +{{ formatAmount(bestMonth.net) }}
              </p>
            </div>
          </div>
        </UCard>

        <UCard v-if="worstMonth">
          <div class="flex items-center gap-3">
            <span class="text-2xl">⚠️</span>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Pire mois</p>
              <p :class="['text-base font-bold', worstMonth.net < 0 ? 'text-red-600 dark:text-red-400' : 'text-orange-600 dark:text-orange-400']">
                {{ monthName(worstMonth.month) }} — {{ worstMonth.net >= 0 ? '+' : '' }}{{ formatAmount(worstMonth.net) }}
              </p>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Graphique 12 mois -->
      <UCard class="mb-6">
        <template #header>
          <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <UIcon name="i-heroicons-chart-bar" class="h-4 w-4" />
            Revenus & dépenses par mois
          </h2>
        </template>
        <AnnualBarChart :data="chartData" :currency="currency" />
      </UCard>

      <!-- Top catégories annuelles -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <UCard>
          <template #header>
            <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-trending-down" class="h-4 w-4 text-red-500" />
              Top dépenses annuelles
            </h2>
          </template>

          <div v-if="topExpenses.length === 0" class="py-4 text-center text-gray-400 text-sm">
            Aucune dépense cette année
          </div>
          <div v-else class="space-y-3">
            <div v-for="cat in topExpenses" :key="cat.category_id" class="space-y-1">
              <div class="flex items-center justify-between text-sm">
                <span class="font-medium text-gray-700 dark:text-gray-300 truncate max-w-[60%]">{{ cat.category_name }}</span>
                <span class="text-gray-600 dark:text-gray-400">{{ formatAmount(cat.total) }}</span>
              </div>
              <div class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                <div
                  class="h-2 rounded-full bg-red-400 dark:bg-red-500 transition-all"
                  :style="{ width: catPercent(cat.total, topExpenses) + '%' }"
                />
              </div>
            </div>
          </div>
        </UCard>

        <UCard>
          <template #header>
            <h2 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <UIcon name="i-heroicons-arrow-trending-up" class="h-4 w-4 text-green-500" />
              Top revenus annuels
            </h2>
          </template>

          <div v-if="topIncomes.length === 0" class="py-4 text-center text-gray-400 text-sm">
            Aucun revenu cette année
          </div>
          <div v-else class="space-y-3">
            <div v-for="cat in topIncomes" :key="cat.category_id" class="space-y-1">
              <div class="flex items-center justify-between text-sm">
                <span class="font-medium text-gray-700 dark:text-gray-300 truncate max-w-[60%]">{{ cat.category_name }}</span>
                <span class="text-gray-600 dark:text-gray-400">{{ formatAmount(cat.total) }}</span>
              </div>
              <div class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
                <div
                  class="h-2 rounded-full bg-green-400 dark:bg-green-500 transition-all"
                  :style="{ width: catPercent(cat.total, topIncomes) + '%' }"
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

const { getMonthlySummary, getByCategory } = useTransactions()
const { currency, ensureProfileLoaded } = useUserProfile()

const currentYear = new Date().getFullYear()
const selectedYear = ref(currentYear)

const loading = ref(false)
const error = ref(false)

interface MonthEntry { month: number; income: number; expense: number; net: number }
const monthlyData = ref<MonthEntry[]>([])
const topExpenses = ref<Array<{ category_id: number; category_name: string; total: number }>>([])
const topIncomes = ref<Array<{ category_id: number; category_name: string; total: number }>>([])

const MONTHS_FR = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
const MONTHS_SHORT = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

const monthName = (m: number) => MONTHS_FR[m - 1] ?? `Mois ${m}`

const monthsWithData = computed(() => monthlyData.value.filter(m => m.income > 0 || m.expense > 0).length || 1)

const totalIncome = computed(() => monthlyData.value.reduce((s, m) => s + m.income, 0))
const totalExpense = computed(() => monthlyData.value.reduce((s, m) => s + m.expense, 0))
const totalNet = computed(() => totalIncome.value - totalExpense.value)

const avgIncome = computed(() => totalIncome.value / monthsWithData.value)
const avgExpense = computed(() => totalExpense.value / monthsWithData.value)
const avgNet = computed(() => totalNet.value / monthsWithData.value)

const bestMonth = computed(() => {
  if (!monthlyData.value.length) return null
  return [...monthlyData.value].sort((a, b) => b.net - a.net)[0]
})

const worstMonth = computed(() => {
  if (!monthlyData.value.length) return null
  return [...monthlyData.value].sort((a, b) => a.net - b.net)[0]
})

const chartData = computed(() =>
  monthlyData.value.map((m, i) => ({
    month: MONTHS_SHORT[m.month - 1] ?? `M${m.month}`,
    income: m.income,
    expense: m.expense,
  }))
)

const catPercent = (total: number, list: Array<{ total: number }>) => {
  const max = list[0]?.total ?? 0
  if (!max) return 0
  return Math.round((total / max) * 100)
}

const formatAmount = (val: number) => {
  return `${val.toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} ${currency.value}`
}

const loadData = async () => {
  loading.value = true
  error.value = false

  const startDate = `${selectedYear.value}-01-01`
  const endDate = `${selectedYear.value}-12-31`

  const [summaryRes, expCatRes, incCatRes] = await Promise.all([
    getMonthlySummary(selectedYear.value),
    getByCategory({ type: 'expense', start_date: startDate, end_date: endDate }),
    getByCategory({ type: 'income', start_date: startDate, end_date: endDate }),
  ])

  if (!summaryRes.success) {
    error.value = true
    loading.value = false
    return
  }

  // Build array of 12 months
  const data: MonthEntry[] = []
  for (let m = 1; m <= 12; m++) {
    const entry = summaryRes.data?.[m]
    data.push({
      month: m,
      income: entry?.income ?? 0,
      expense: entry?.expense ?? 0,
      net: entry?.net ?? 0,
    })
  }
  monthlyData.value = data

  topExpenses.value = (expCatRes.data ?? []).sort((a, b) => b.total - a.total).slice(0, 6)
  topIncomes.value = (incCatRes.data ?? []).sort((a, b) => b.total - a.total).slice(0, 6)

  loading.value = false
}

watch(selectedYear, loadData)

onMounted(async () => {
  await ensureProfileLoaded()
  await loadData()
})
</script>
