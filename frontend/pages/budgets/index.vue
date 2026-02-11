<script setup lang="ts">
import type { Budget, Category } from '~/types'

definePageMeta({
  middleware: 'auth'
})

const { getBudgets, createBudget, updateBudget, deleteBudget, getBudgetsSummary, toggleBudgetActive } = useBudgets()
const { getCategories } = useCategories()
const { getProfile, updateProfile } = useUserProfile()
const { getTransactions } = useTransactions()
const { getAccounts } = useAccounts()
const toast = useToast()

// State
const budgets = ref<Budget[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const showModal = ref(false)
const showIncomeModal = ref(false)
const showTransactionsModal = ref(false)
const editingBudget = ref<Budget | null>(null)
const selectedBudget = ref<Budget | null>(null)
const budgetTransactions = ref<any[]>([])
const summary = ref({
  total_budgets: 0,
  total_amount: 0,
  total_spent: 0,
  total_remaining: 0,
  over_budget_count: 0,
  alert_count: 0,
  percentage_used: 0
})
const userProfile = ref<any>(null)
const incomeForm = ref({
  monthly_income: ''
})
const formErrors = ref<Record<string, string>>({})
const incomeFormErrors = ref<Record<string, string>>({})

// Form
const form = ref({
  name: '',
  category: '',
  amount: '',
  period: 'monthly' as 'weekly' | 'monthly' | 'yearly',
  start_date: new Date().toISOString().split('T')[0],
  end_date: '',
  alert_threshold: 80,
  is_active: true,
  is_savings_goal: false
})

// Methods
const fetchBudgets = async () => {
  loading.value = true
  const result = await getBudgets()
  if (result.success && result.data) {
    budgets.value = result.data.results
  }
  loading.value = false
}

const fetchCategories = async () => {
  const result = await getCategories({ type: 'expense' })
  if (result.success && result.data) {
    categories.value = result.data.results
  }
}

const fetchSummary = async () => {
  const result = await getBudgetsSummary()
  if (result.success && result.data) {
    summary.value = result.data
  }
}

const fetchProfile = async () => {
  const result = await getProfile()
  if (result.success && result.data) {
    userProfile.value = result.data
  }
}

const openModal = (budget?: Budget) => {
  formErrors.value = {} // Reset errors
  if (budget) {
    editingBudget.value = budget
    form.value = {
      name: budget.name,
      category: budget.category ? budget.category.toString() : '',
      amount: budget.amount,
      period: budget.period,
      start_date: budget.start_date,
      end_date: budget.end_date || '',
      alert_threshold: budget.alert_threshold,
      is_active: budget.is_active,
      is_savings_goal: budget.is_savings_goal || false
    }
  } else {
    editingBudget.value = null
    form.value = {
      name: '',
      category: '',
      amount: '',
      period: 'monthly',
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
      alert_threshold: 80,
      is_active: true,
      is_savings_goal: false
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingBudget.value = null
  formErrors.value = {} // Reset errors
}

const handleSubmit = async () => {
  loading.value = true
  formErrors.value = {} // Reset errors

  const budgetData: any = {
    name: form.value.name,
    amount: form.value.amount,
    period: form.value.period,
    start_date: form.value.start_date,
    alert_threshold: form.value.alert_threshold,
    is_active: form.value.is_active,
    is_savings_goal: form.value.is_savings_goal
  }

  // Ajouter la catégorie seulement si ce n'est pas un objectif d'épargne
  if (!form.value.is_savings_goal && form.value.category) {
    budgetData.category = parseInt(form.value.category)
  }

  if (form.value.end_date) {
    budgetData.end_date = form.value.end_date
  }

  let result
  if (editingBudget.value) {
    result = await updateBudget(editingBudget.value.id, budgetData)
  } else {
    result = await createBudget(budgetData)
  }

  loading.value = false

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: editingBudget.value ? (form.value.is_savings_goal ? 'Objectif d\'épargne mis à jour' : 'Budget mis à jour') : (form.value.is_savings_goal ? 'Objectif d\'épargne créé' : 'Budget créé'),
      color: 'green'
    })
    closeModal()
    await fetchBudgets()
    await fetchSummary()
    await fetchProfile()
  } else {
    // Parse validation errors
    if (result.error?.data) {
      const errors = result.error.data
      // Convert error arrays to strings
      Object.keys(errors).forEach(key => {
        if (Array.isArray(errors[key])) {
          formErrors.value[key] = errors[key][0]
        } else if (typeof errors[key] === 'string') {
          formErrors.value[key] = errors[key]
        }
      })

      // Show first error in toast
      const firstError = Object.values(formErrors.value)[0]
      toast.add({
        title: 'Erreur de validation',
        description: firstError || 'Veuillez vérifier les champs du formulaire',
        color: 'red'
      })
    } else {
      toast.add({
        title: 'Erreur',
        description: 'Une erreur est survenue',
        color: 'red'
      })
    }
  }
}

// Confirm modal state
const showConfirmDelete = ref(false)
const budgetToDelete = ref<Budget | null>(null)

const handleDelete = (budget: Budget) => {
  budgetToDelete.value = budget
  showConfirmDelete.value = true
}

const executeDelete = async () => {
  if (!budgetToDelete.value) return

  loading.value = true
  const result = await deleteBudget(budgetToDelete.value.id)
  loading.value = false
  budgetToDelete.value = null

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Budget supprimé',
      color: 'green'
    })
    await fetchBudgets()
    await fetchSummary()
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Impossible de supprimer le budget',
      color: 'red'
    })
  }
}

const handleToggleActive = async (budget: Budget) => {
  const result = await toggleBudgetActive(budget.id)
  if (result.success) {
    await fetchBudgets()
    await fetchSummary()
  }
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 100) return 'red'
  if (percentage >= 80) return 'orange'
  if (percentage >= 60) return 'yellow'
  return 'green'
}

// Computed
const regularBudgets = computed(() => budgets.value.filter(b => !b.is_savings_goal))
const savingsGoals = computed(() => budgets.value.filter(b => b.is_savings_goal))

// View budget transactions
const viewBudgetTransactions = async (budget: Budget) => {
  selectedBudget.value = budget
  loading.value = true

  try {
    // Calculer la période du budget
    const today = new Date()
    let startDate: Date
    let endDate: Date

    if (budget.period === 'weekly') {
      const dayOfWeek = today.getDay()
      const diff = dayOfWeek === 0 ? 6 : dayOfWeek - 1
      startDate = new Date(today)
      startDate.setDate(today.getDate() - diff)
      endDate = new Date(startDate)
      endDate.setDate(startDate.getDate() + 6)
    } else if (budget.period === 'monthly') {
      startDate = new Date(today.getFullYear(), today.getMonth(), 1)
      endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0)
    } else { // yearly
      startDate = new Date(today.getFullYear(), 0, 1)
      endDate = new Date(today.getFullYear(), 11, 31)
    }

    // Limiter par les dates du budget si définies
    if (budget.start_date && new Date(budget.start_date) > startDate) {
      startDate = new Date(budget.start_date)
    }
    if (budget.end_date && new Date(budget.end_date) < endDate) {
      endDate = new Date(budget.end_date)
    }

    // Ne pas inclure les dates futures
    if (endDate > today) {
      endDate = today
    }

    if (budget.is_savings_goal) {
      // Pour les objectifs d'épargne: récupérer les transferts vers comptes épargne
      const accountsResult = await getAccounts({ account_type: 'savings', is_active: true })
      const savingsAccountIds = accountsResult.data?.results.map((a: any) => a.id) || []

      // Récupérer tous les transferts
      const result = await getTransactions({
        type: 'transfer',
        ordering: '-date'
      })

      if (result.success && result.data) {
        // Filtrer les transferts vers comptes épargne dans la période
        budgetTransactions.value = result.data.results.filter((t: any) => {
          const transDate = new Date(t.date)
          return t.destination_account &&
                 savingsAccountIds.includes(t.destination_account) &&
                 transDate >= startDate &&
                 transDate <= endDate
        })
      }
    } else {
      // Pour les budgets normaux: récupérer les dépenses de la catégorie
      const result = await getTransactions({
        type: 'expense',
        category: budget.category,
        ordering: '-date'
      })

      if (result.success && result.data) {
        // Filtrer par période
        budgetTransactions.value = result.data.results.filter((t: any) => {
          const transDate = new Date(t.date)
          return transDate >= startDate && transDate <= endDate
        })
      }
    }

    showTransactionsModal.value = true
  } catch (error) {
    console.error('Error fetching budget transactions:', error)
    toast.add({
      title: 'Erreur',
      description: 'Impossible de charger les transactions',
      color: 'red'
    })
  } finally {
    loading.value = false
  }
}

const closeTransactionsModal = () => {
  showTransactionsModal.value = false
  selectedBudget.value = null
  budgetTransactions.value = []
}

const formatCurrency = (amount: number | string) => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('fr-CH', {
    style: 'currency',
    currency: 'CHF'
  }).format(num)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const openIncomeModal = () => {
  incomeFormErrors.value = {} // Reset errors
  if (userProfile.value) {
    incomeForm.value.monthly_income = userProfile.value.monthly_income
  }
  showIncomeModal.value = true
}

const closeIncomeModal = () => {
  showIncomeModal.value = false
  incomeFormErrors.value = {} // Reset errors
}

const handleIncomeUpdate = async () => {
  loading.value = true
  incomeFormErrors.value = {} // Reset errors

  const result = await updateProfile({
    monthly_income: incomeForm.value.monthly_income
  })

  loading.value = false

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Revenu mensuel mis à jour',
      color: 'green'
    })
    closeIncomeModal()
    await fetchProfile()
    await fetchSummary()
  } else {
    // Parse validation errors
    if (result.error?.data) {
      const errors = result.error.data
      // Convert error arrays to strings
      Object.keys(errors).forEach(key => {
        if (Array.isArray(errors[key])) {
          incomeFormErrors.value[key] = errors[key][0]
        } else if (typeof errors[key] === 'string') {
          incomeFormErrors.value[key] = errors[key]
        }
      })

      // Show first error in toast
      const firstError = Object.values(incomeFormErrors.value)[0]
      toast.add({
        title: 'Erreur de validation',
        description: firstError || 'Veuillez vérifier les champs du formulaire',
        color: 'red'
      })
    } else {
      toast.add({
        title: 'Erreur',
        description: 'Impossible de mettre à jour le revenu',
        color: 'red'
      })
    }
  }
}

// Lifecycle
onMounted(() => {
  fetchBudgets()
  fetchCategories()
  fetchSummary()
  fetchProfile()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Budgets</h1>
      <UButton @click="openModal()" icon="i-heroicons-plus" size="lg">
        Nouveau budget
      </UButton>
    </div>

    <!-- Available Budget Info -->
    <div v-if="userProfile && userProfile.available_budget_info" class="mb-6">
      <UCard class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 border-2 border-primary-200 dark:border-primary-800">
        <template #header>
          <div class="flex justify-between items-center">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Vue d'ensemble du budget</h2>
            <UButton
              icon="i-heroicons-pencil"
              size="sm"
              color="primary"
              variant="ghost"
              @click="openIncomeModal"
            >
              Modifier le revenu
            </UButton>
          </div>
        </template>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- Revenu mensuel -->
          <div class="flex items-center space-x-4">
            <div class="flex-shrink-0">
              <div class="h-12 w-12 rounded-full bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center">
                <UIcon name="i-heroicons-banknotes" class="h-6 w-6 text-primary-600" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Revenu mensuel</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">
                {{ userProfile.available_budget_info.monthly_income.toFixed(2) }} CHF
              </p>
            </div>
          </div>

          <!-- Budget alloué -->
          <div class="flex items-center space-x-4">
            <div class="flex-shrink-0">
              <div class="h-12 w-12 rounded-full bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center">
                <UIcon name="i-heroicons-chart-pie" class="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Budget alloué</p>
              <p class="text-2xl font-bold text-blue-600">
                {{ userProfile.available_budget_info.total_allocated.toFixed(2) }} CHF
              </p>
              <p class="text-xs text-gray-500">
                {{ userProfile.available_budget_info.percentage_allocated.toFixed(1) }}% du revenu
              </p>
            </div>
          </div>

          <!-- Objectifs d'épargne -->
          <div v-if="userProfile.available_budget_info.total_savings_goal > 0" class="flex items-center space-x-4">
            <div class="flex-shrink-0">
              <div class="h-12 w-12 rounded-full bg-green-100 dark:bg-green-900/40 flex items-center justify-center">
                <UIcon name="i-heroicons-currency-dollar" class="h-6 w-6 text-green-600" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Objectif d'épargne</p>
              <p class="text-2xl font-bold text-green-600">
                {{ userProfile.available_budget_info.total_savings_goal.toFixed(2) }} CHF
              </p>
              <p class="text-xs text-gray-500">
                Mensuel
              </p>
            </div>
          </div>

          <!-- Budget disponible -->
          <div class="flex items-center space-x-4">
            <div class="flex-shrink-0">
              <div class="h-12 w-12 rounded-full flex items-center justify-center" :class="userProfile.available_budget_info.available >= 0 ? 'bg-teal-100 dark:bg-teal-900/40' : 'bg-red-100 dark:bg-red-900/40'">
                <UIcon name="i-heroicons-wallet" class="h-6 w-6" :class="userProfile.available_budget_info.available >= 0 ? 'text-teal-600' : 'text-red-600'" />
              </div>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Budget disponible</p>
              <p class="text-2xl font-bold" :class="userProfile.available_budget_info.available >= 0 ? 'text-teal-600' : 'text-red-600'">
                {{ userProfile.available_budget_info.available.toFixed(2) }} CHF
              </p>
              <p class="text-xs" :class="userProfile.available_budget_info.available >= 0 ? 'text-teal-600' : 'text-red-600'">
                {{ userProfile.available_budget_info.available >= 0 ? 'Encore disponible' : 'Dépassement du revenu' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Warning si pas de revenu configuré -->
        <div v-if="userProfile.monthly_income === 0 || userProfile.monthly_income === '0.00'" class="mt-4 p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
          <div class="flex items-center">
            <UIcon name="i-heroicons-exclamation-triangle" class="h-5 w-5 text-orange-600 mr-2" />
            <div class="flex-1">
              <span class="text-sm text-orange-700 dark:text-orange-400">Configurez votre revenu mensuel pour suivre votre budget disponible</span>
            </div>
            <NuxtLink to="/profile" class="text-sm font-medium text-orange-600 hover:text-orange-500">
              Configurer →
            </NuxtLink>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <UCard>
        <div class="text-sm text-gray-500">Budgets actifs</div>
        <div class="text-2xl font-bold">{{ summary.total_budgets }}</div>
        <div class="text-xs text-gray-400">Total des budgets</div>
      </UCard>
      <UCard>
        <div class="text-sm text-gray-500">Budget total</div>
        <div class="text-2xl font-bold text-blue-600">{{ (summary.total_amount ?? 0).toFixed(2) }} CHF</div>
        <div class="text-xs text-gray-400">Montant alloué</div>
      </UCard>
      <UCard>
        <div class="text-sm text-gray-500">Dépensé</div>
        <div class="text-2xl font-bold text-red-600">{{ (summary.total_spent ?? 0).toFixed(2) }} CHF</div>
        <div class="text-xs text-gray-400">{{ (summary.percentage_used ?? 0).toFixed(1) }}% utilisé</div>
      </UCard>
      <UCard>
        <div class="text-sm text-gray-500">Alertes</div>
        <div class="text-2xl font-bold text-orange-600">{{ summary.alert_count }}</div>
        <div class="text-xs text-gray-400">{{ summary.over_budget_count }} dépassés</div>
      </UCard>
    </div>

    <!-- Savings Goals Section -->
    <div v-if="savingsGoals.length > 0" class="mb-8">
      <h2 class="text-2xl font-bold mb-4 flex items-center">
        <UIcon name="i-heroicons-currency-dollar" class="h-6 w-6 text-green-600 mr-2" />
        Objectifs d'épargne
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UCard v-for="budget in savingsGoals" :key="budget.id" class="border-2 border-green-200 dark:border-green-800">
          <template #header>
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <UIcon name="i-heroicons-banknotes" class="h-5 w-5 text-green-600" />
                  <h3 class="text-lg font-semibold">{{ budget.name }}</h3>
                </div>
                <p class="text-sm text-gray-500">
                  Épargne • {{ budget.period_display }}
                </p>
              </div>
              <UBadge
                :color="budget.is_active ? 'green' : 'gray'"
                variant="subtle"
                class="cursor-pointer"
                @click="handleToggleActive(budget)"
              >
                {{ budget.is_active ? 'Actif' : 'Inactif' }}
              </UBadge>
            </div>
          </template>

          <div class="space-y-4">
            <!-- Progress -->
            <div>
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm text-gray-600 dark:text-gray-400">Épargné</span>
                <div class="text-right">
                  <div class="text-sm font-semibold">
                    {{ (budget.spent_amount ?? 0).toFixed(2) }} / {{ parseFloat(budget.amount).toFixed(2) }} CHF
                  </div>
                  <div v-if="(budget.projected_amount ?? 0) !== (budget.spent_amount ?? 0)" class="text-xs text-green-600 dark:text-green-400">
                    Projeté: {{ (budget.projected_amount ?? 0).toFixed(2) }} CHF
                  </div>
                </div>
              </div>
              <UProgress
                :value="budget.percentage_used ?? 0"
                :color="getProgressColor(budget.percentage_used ?? 0)"
                size="md"
              />
              <p class="mt-1 text-xs text-gray-500">
                {{ (budget.percentage_used ?? 0).toFixed(1) }}% de l'objectif
                <span v-if="(budget.projected_percentage_used ?? 0) !== (budget.percentage_used ?? 0)" class="text-green-600 dark:text-green-400">
                  ({{ (budget.projected_percentage_used ?? 0).toFixed(1) }}% projeté)
                </span>
              </p>
            </div>

            <!-- Remaining -->
            <div class="flex justify-between items-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <span class="text-sm text-gray-600 dark:text-gray-400">Encore à épargner</span>
              <div class="text-right">
                <div class="text-lg font-bold" :class="(budget.remaining_amount ?? 0) >= 0 ? 'text-gray-900 dark:text-white' : 'text-green-600'">
                  {{ Math.abs(budget.remaining_amount ?? 0).toFixed(2) }} CHF
                </div>
                <div v-if="(budget.projected_remaining_amount ?? 0) !== (budget.remaining_amount ?? 0)"
                     class="text-xs text-green-600 dark:text-green-400">
                  {{ Math.abs(budget.projected_remaining_amount ?? 0).toFixed(2) }} CHF projeté
                </div>
              </div>
            </div>

            <!-- Success Message -->
            <div v-if="(budget.percentage_used ?? 0) >= 100" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
              <div class="flex items-center">
                <UIcon name="i-heroicons-check-circle" class="h-5 w-5 text-green-600 mr-2" />
                <span class="text-sm text-green-700 dark:text-green-400">Objectif atteint! 🎉</span>
              </div>
            </div>
            <div v-else-if="(budget.projected_percentage_used ?? 0) >= 100 && (budget.percentage_used ?? 0) < 100" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
              <div class="flex items-center">
                <UIcon name="i-heroicons-information-circle" class="h-5 w-5 text-green-600 mr-2" />
                <span class="text-sm text-green-700 dark:text-green-400">Avec les transferts futurs, vous atteindrez votre objectif! 🎯</span>
              </div>
            </div>

            <!-- Period -->
            <div class="text-xs text-gray-500">
              Période: {{ new Date(budget.start_date).toLocaleDateString('fr-FR') }}
              <template v-if="budget.end_date">
                - {{ new Date(budget.end_date).toLocaleDateString('fr-FR') }}
              </template>
            </div>

            <!-- Actions -->
            <div class="flex flex-wrap gap-2 pt-2">
              <UButton
                size="sm"
                color="primary"
                variant="soft"
                icon="i-heroicons-list-bullet"
                @click="viewBudgetTransactions(budget)"
              >
                Voir les transactions
              </UButton>
              <UButton
                size="sm"
                color="gray"
                variant="ghost"
                icon="i-heroicons-pencil"
                @click.stop="openModal(budget)"
              >
                Modifier
              </UButton>
              <UButton
                size="sm"
                color="red"
                variant="ghost"
                icon="i-heroicons-trash"
                @click.stop="handleDelete(budget)"
              >
                Supprimer
              </UButton>
            </div>
          </div>
        </UCard>
      </div>
    </div>

    <!-- Regular Budgets Section -->
    <div v-if="regularBudgets.length > 0" class="mb-8">
      <h2 class="text-2xl font-bold mb-4">Budgets de dépenses</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UCard v-for="budget in regularBudgets" :key="budget.id">
        <template #header>
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h3 class="text-lg font-semibold">{{ budget.name }}</h3>
              <p class="text-sm text-gray-500">
                {{ budget.category_details?.name }} • {{ budget.period_display }}
              </p>
            </div>
            <UBadge
              :color="budget.is_active ? 'green' : 'gray'"
              variant="subtle"
              class="cursor-pointer"
              @click="handleToggleActive(budget)"
            >
              {{ budget.is_active ? 'Actif' : 'Inactif' }}
            </UBadge>
          </div>
        </template>

        <div class="space-y-4">
          <!-- Progress -->
          <div>
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm text-gray-600">Dépensé</span>
              <div class="text-right">
                <div class="text-sm font-semibold">
                  {{ (budget.spent_amount ?? 0).toFixed(2) }} / {{ parseFloat(budget.amount).toFixed(2) }} CHF
                </div>
                <div v-if="(budget.projected_amount ?? 0) !== (budget.spent_amount ?? 0)" class="text-xs text-blue-600 dark:text-blue-400">
                  Projeté: {{ (budget.projected_amount ?? 0).toFixed(2) }} CHF
                </div>
              </div>
            </div>
            <UProgress
              :value="budget.percentage_used ?? 0"
              :color="getProgressColor(budget.percentage_used ?? 0)"
              size="md"
            />
            <p class="mt-1 text-xs text-gray-500">
              {{ (budget.percentage_used ?? 0).toFixed(1) }}% utilisé
              <span v-if="(budget.projected_percentage_used ?? 0) !== (budget.percentage_used ?? 0)" class="text-blue-600 dark:text-blue-400">
                ({{ (budget.projected_percentage_used ?? 0).toFixed(1) }}% projeté)
              </span>
            </p>
          </div>

          <!-- Remaining -->
          <div class="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <span class="text-sm text-gray-600 dark:text-gray-400">Restant</span>
            <div class="text-right">
              <div class="text-lg font-bold" :class="(budget.remaining_amount ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ (budget.remaining_amount ?? 0) < 0 ? '−' : '' }}{{ Math.abs(budget.remaining_amount ?? 0).toFixed(2) }} CHF
              </div>
              <div v-if="(budget.projected_remaining_amount ?? 0) !== (budget.remaining_amount ?? 0)"
                   class="text-xs"
                   :class="(budget.projected_remaining_amount ?? 0) >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                {{ (budget.projected_remaining_amount ?? 0).toFixed(2) }} CHF projeté
              </div>
            </div>
          </div>

          <!-- Alerts -->
          <div v-if="budget.is_over_budget" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
            <div class="flex items-center">
              <UIcon name="i-heroicons-exclamation-circle" class="h-5 w-5 text-red-600 mr-2" />
              <span class="text-sm text-red-700 dark:text-red-400">Budget dépassé !</span>
            </div>
          </div>
          <div v-else-if="budget.is_projected_over_budget && !budget.is_over_budget" class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3">
            <div class="flex items-center">
              <UIcon name="i-heroicons-exclamation-triangle" class="h-5 w-5 text-orange-600 mr-2" />
              <span class="text-sm text-orange-700 dark:text-orange-400">
                Attention : avec les paiements futurs, ce budget sera dépassé
              </span>
            </div>
          </div>
          <div v-else-if="budget.is_alert_triggered" class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3">
            <div class="flex items-center">
              <UIcon name="i-heroicons-exclamation-triangle" class="h-5 w-5 text-orange-600 mr-2" />
              <span class="text-sm text-orange-700 dark:text-orange-400">
                Attention : {{ budget.alert_threshold }}% atteint
              </span>
            </div>
          </div>
          <div v-else-if="(budget.projected_percentage_used ?? 0) >= (budget.alert_threshold ?? 80) && !(budget.is_alert_triggered)" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
            <div class="flex items-center">
              <UIcon name="i-heroicons-information-circle" class="h-5 w-5 text-yellow-600 mr-2" />
              <span class="text-sm text-yellow-700 dark:text-yellow-400">
                Avec les paiements futurs, le seuil de {{ budget.alert_threshold }}% sera atteint
              </span>
            </div>
          </div>

          <!-- Period -->
          <div class="text-xs text-gray-500">
            Période: {{ new Date(budget.start_date).toLocaleDateString('fr-FR') }}
            <template v-if="budget.end_date">
              - {{ new Date(budget.end_date).toLocaleDateString('fr-FR') }}
            </template>
          </div>

          <!-- Actions -->
          <div class="flex flex-wrap gap-2 pt-2">
            <UButton
              size="sm"
              color="primary"
              variant="soft"
              icon="i-heroicons-list-bullet"
              @click="viewBudgetTransactions(budget)"
            >
              Voir les transactions
            </UButton>
            <UButton
              size="sm"
              color="gray"
              variant="ghost"
              icon="i-heroicons-pencil"
              @click.stop="openModal(budget)"
            >
              Modifier
            </UButton>
            <UButton
              size="sm"
              color="red"
              variant="ghost"
              icon="i-heroicons-trash"
              @click.stop="handleDelete(budget)"
            >
              Supprimer
            </UButton>
          </div>
        </div>
      </UCard>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="budgets.length === 0 && !loading">
      <UCard class="col-span-full">
        <div class="text-center py-12">
          <UIcon name="i-heroicons-chart-bar" class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium">Aucun budget</h3>
          <p class="mt-1 text-sm text-gray-500">
            Commencez par créer votre premier budget
          </p>
          <div class="mt-6">
            <UButton @click="openModal()">
              Nouveau budget
            </UButton>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Budget Modal -->
    <UModal v-model="showModal" :ui="{ width: 'sm:max-w-lg' }">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ editingBudget ? 'Modifier le budget' : 'Nouveau budget' }}
          </h3>
        </template>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Name -->
          <UFormGroup label="Nom du budget" required :error="formErrors.name">
            <UInput
              v-model="form.name"
              placeholder="Ex: Budget alimentation mensuel"
              required
            />
          </UFormGroup>

          <!-- Category (only for regular budgets) -->
          <UFormGroup v-if="!form.is_savings_goal" label="Catégorie" required :error="formErrors.category">
            <USelectMenu
              v-model="form.category"
              :options="categories"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner une catégorie"
            />
          </UFormGroup>

          <!-- Info for savings goals -->
          <div v-if="form.is_savings_goal" class="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <div class="flex items-start">
              <UIcon name="i-heroicons-information-circle" class="h-5 w-5 text-green-600 mr-2 mt-0.5" />
              <div class="text-sm text-green-700 dark:text-green-400">
                <p class="font-medium">Objectif d'épargne</p>
                <p class="mt-1">Ce budget suivra automatiquement vos transferts vers vos comptes épargne. Aucune catégorie n'est nécessaire.</p>
              </div>
            </div>
          </div>

          <!-- Amount -->
          <UFormGroup label="Montant (CHF)" required :error="formErrors.amount">
            <UInput
              v-model="form.amount"
              type="number"
              step="0.01"
              placeholder="0.00"
              required
            />
          </UFormGroup>

          <!-- Period -->
          <UFormGroup label="Période" required :error="formErrors.period">
            <USelectMenu
              v-model="form.period"
              :options="[
                { label: 'Hebdomadaire', value: 'weekly' },
                { label: 'Mensuel', value: 'monthly' },
                { label: 'Annuel', value: 'yearly' }
              ]"
              option-attribute="label"
              value-attribute="value"
            />
          </UFormGroup>

          <!-- Dates -->
          <div class="grid grid-cols-2 gap-4">
            <UFormGroup label="Date de début" required :error="formErrors.start_date">
              <UInput v-model="form.start_date" type="date" required />
            </UFormGroup>
            <UFormGroup label="Date de fin (optionnelle)" :error="formErrors.end_date">
              <UInput v-model="form.end_date" type="date" />
            </UFormGroup>
          </div>

          <!-- Alert Threshold -->
          <UFormGroup label="Seuil d'alerte (%)" :error="formErrors.alert_threshold">
            <UInput
              v-model.number="form.alert_threshold"
              type="number"
              min="0"
              max="100"
              placeholder="80"
            />
            <template #help>
              <p class="text-xs text-gray-500">
                Vous serez alerté lorsque ce pourcentage du budget sera atteint
              </p>
            </template>
          </UFormGroup>

          <!-- Active -->
          <UFormGroup>
            <UCheckbox v-model="form.is_active" label="Budget actif" />
          </UFormGroup>

          <!-- Savings Goal -->
          <UFormGroup>
            <UCheckbox v-model="form.is_savings_goal" label="Objectif d'épargne" />
            <template #help>
              <p class="text-xs text-gray-500">
                Si coché, ce budget suivra vos transferts vers vos comptes épargne au lieu des dépenses par catégorie
              </p>
            </template>
          </UFormGroup>

          <!-- Actions -->
          <div class="flex justify-end gap-2 pt-4">
            <UButton color="gray" variant="ghost" @click="closeModal">
              Annuler
            </UButton>
            <UButton type="submit" :loading="loading">
              {{ editingBudget ? 'Mettre à jour' : 'Créer' }}
            </UButton>
          </div>
        </form>
      </UCard>
    </UModal>

    <!-- Income Modal -->
    <UModal v-model="showIncomeModal" :ui="{ width: 'sm:max-w-md' }">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">Modifier le revenu mensuel</h3>
        </template>

        <form @submit.prevent="handleIncomeUpdate" class="space-y-4">
          <UFormGroup label="Revenu mensuel" required :error="incomeFormErrors.monthly_income">
            <UInput
              v-model="incomeForm.monthly_income"
              type="number"
              step="0.01"
              placeholder="0.00"
              icon="i-heroicons-banknotes"
              required
            >
              <template #trailing>
                <span class="text-gray-500">CHF</span>
              </template>
            </UInput>
            <template #help>
              <p class="text-xs text-gray-500">
                Votre revenu mensuel total disponible pour vos budgets
              </p>
            </template>
          </UFormGroup>

          <div class="flex justify-end gap-2 pt-4">
            <UButton color="gray" variant="ghost" @click="closeIncomeModal">
              Annuler
            </UButton>
            <UButton type="submit" :loading="loading">
              Enregistrer
            </UButton>
          </div>
        </form>
      </UCard>
    </UModal>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer le budget"
      :message="`Êtes-vous sûr de vouloir supprimer le budget « ${budgetToDelete?.name} » ?`"
      confirm-label="Supprimer"
      @confirm="executeDelete"
    />

    <!-- Transactions Modal -->
    <UModal v-model="showTransactionsModal" :ui="{ width: 'sm:max-w-2xl' }">
      <UCard>
        <template #header>
          <div>
            <h3 class="text-lg font-semibold">
              {{ selectedBudget?.is_savings_goal ? 'Transferts d\'épargne' : 'Transactions du budget' }}
            </h3>
            <p class="text-sm text-gray-500 mt-1">
              {{ selectedBudget?.name }} - {{ selectedBudget?.period_display }}
            </p>
          </div>
        </template>

        <div v-if="budgetTransactions.length === 0" class="text-center py-8">
          <UIcon name="i-heroicons-inbox" class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">Aucune transaction</h3>
          <p class="mt-1 text-sm text-gray-500">
            {{ selectedBudget?.is_savings_goal ? 'Aucun transfert vers l\'épargne pour cette période' : 'Aucune dépense dans cette catégorie pour cette période' }}
          </p>
        </div>

        <div v-else class="space-y-3">
          <!-- Transaction List -->
          <div v-for="transaction in budgetTransactions" :key="transaction.id" class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors">
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <UIcon
                    :name="transaction.type === 'transfer' ? 'i-heroicons-arrow-right-circle' : 'i-heroicons-shopping-cart'"
                    :class="transaction.type === 'transfer' ? 'text-blue-600' : 'text-red-600'"
                    class="h-5 w-5"
                  />
                  <h4 class="font-medium text-gray-900 dark:text-white">
                    {{ transaction.description || (transaction.type === 'transfer' ? 'Transfert' : 'Dépense') }}
                  </h4>
                </div>

                <div class="mt-1 text-sm text-gray-500">
                  <p>{{ formatDate(transaction.date) }}</p>
                  <p v-if="transaction.account_details" class="mt-1">
                    Compte: {{ transaction.account_details.name }}
                    <span v-if="transaction.destination_account_details">
                      → {{ transaction.destination_account_details.name }}
                    </span>
                  </p>
                  <p v-if="transaction.category_details" class="mt-1">
                    Catégorie: {{ transaction.category_details.name }}
                  </p>
                </div>
              </div>

              <div class="text-right">
                <p class="text-lg font-bold" :class="transaction.type === 'transfer' ? 'text-blue-600' : 'text-red-600'">
                  {{ formatCurrency(transaction.amount) }}
                </p>
              </div>
            </div>

            <p v-if="transaction.notes" class="mt-2 text-sm text-gray-600 dark:text-gray-400 italic">
              {{ transaction.notes }}
            </p>
          </div>

          <!-- Total -->
          <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
            <div class="flex justify-between items-center">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ selectedBudget?.is_savings_goal ? 'Total épargné' : 'Total dépensé' }}
              </span>
              <span class="text-xl font-bold" :class="selectedBudget?.is_savings_goal ? 'text-green-600' : 'text-red-600'">
                {{ formatCurrency(budgetTransactions.reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)) }}
              </span>
            </div>
            <p class="text-xs text-gray-500 mt-1 text-right">
              {{ budgetTransactions.length }} transaction{{ budgetTransactions.length > 1 ? 's' : '' }}
            </p>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end">
            <UButton color="gray" @click="closeTransactionsModal">
              Fermer
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>
