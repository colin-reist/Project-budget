<script setup lang="ts">
import type { Budget, Category } from '~/types'

definePageMeta({
  middleware: 'auth'
})

const { getBudgets, createBudget, updateBudget, deleteBudget, getBudgetsSummary, toggleBudgetActive } = useBudgets()
const { getCategories } = useCategories()
const toast = useToast()

// State
const budgets = ref<Budget[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const showModal = ref(false)
const editingBudget = ref<Budget | null>(null)
const summary = ref({
  total_budgets: 0,
  total_amount: 0,
  total_spent: 0,
  total_remaining: 0,
  over_budget_count: 0,
  alert_count: 0,
  percentage_used: 0
})

// Form
const form = ref({
  name: '',
  category: '',
  amount: '',
  period: 'monthly' as 'weekly' | 'monthly' | 'yearly',
  start_date: new Date().toISOString().split('T')[0],
  end_date: '',
  alert_threshold: 80,
  is_active: true
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

const openModal = (budget?: Budget) => {
  if (budget) {
    editingBudget.value = budget
    form.value = {
      name: budget.name,
      category: budget.category.toString(),
      amount: budget.amount,
      period: budget.period,
      start_date: budget.start_date,
      end_date: budget.end_date || '',
      alert_threshold: budget.alert_threshold,
      is_active: budget.is_active
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
      is_active: true
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingBudget.value = null
}

const handleSubmit = async () => {
  loading.value = true

  const budgetData: any = {
    name: form.value.name,
    category: parseInt(form.value.category),
    amount: form.value.amount,
    period: form.value.period,
    start_date: form.value.start_date,
    alert_threshold: form.value.alert_threshold,
    is_active: form.value.is_active
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
      description: editingBudget.value ? 'Budget mis à jour' : 'Budget créé',
      color: 'green'
    })
    closeModal()
    await fetchBudgets()
    await fetchSummary()
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Une erreur est survenue',
      color: 'red'
    })
  }
}

const handleDelete = async (budget: Budget) => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer ce budget ?')) return

  loading.value = true
  const result = await deleteBudget(budget.id)
  loading.value = false

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

// Lifecycle
onMounted(() => {
  fetchBudgets()
  fetchCategories()
  fetchSummary()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold">Budgets</h1>
      <UButton @click="openModal()" icon="i-heroicons-plus" size="lg">
        Nouveau budget
      </UButton>
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

    <!-- Budgets Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <UCard v-for="budget in budgets" :key="budget.id">
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
              <span class="text-sm font-semibold">
                {{ (budget.spent_amount ?? 0).toFixed(2) }} / {{ parseFloat(budget.amount).toFixed(2) }} CHF
              </span>
            </div>
            <UProgress
              :value="budget.percentage_used ?? 0"
              :color="getProgressColor(budget.percentage_used ?? 0)"
              size="md"
            />
            <p class="mt-1 text-xs text-gray-500">
              {{ (budget.percentage_used ?? 0).toFixed(1) }}% utilisé
            </p>
          </div>

          <!-- Remaining -->
          <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
            <span class="text-sm text-gray-600">Restant</span>
            <span class="text-lg font-bold" :class="(budget.remaining_amount ?? 0) >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ (budget.remaining_amount ?? 0).toFixed(2) }} CHF
            </span>
          </div>

          <!-- Alerts -->
          <div v-if="budget.is_over_budget" class="bg-red-50 border border-red-200 rounded-lg p-3">
            <div class="flex items-center">
              <UIcon name="i-heroicons-exclamation-circle" class="h-5 w-5 text-red-600 mr-2" />
              <span class="text-sm text-red-700">Budget dépassé !</span>
            </div>
          </div>
          <div v-else-if="budget.is_alert_triggered" class="bg-orange-50 border border-orange-200 rounded-lg p-3">
            <div class="flex items-center">
              <UIcon name="i-heroicons-exclamation-triangle" class="h-5 w-5 text-orange-600 mr-2" />
              <span class="text-sm text-orange-700">
                Attention : {{ budget.alert_threshold }}% atteint
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
          <div class="flex gap-2 pt-2">
            <UButton
              size="sm"
              color="gray"
              variant="ghost"
              icon="i-heroicons-pencil"
              @click="openModal(budget)"
            >
              Modifier
            </UButton>
            <UButton
              size="sm"
              color="red"
              variant="ghost"
              icon="i-heroicons-trash"
              @click="handleDelete(budget)"
            >
              Supprimer
            </UButton>
          </div>
        </div>
      </UCard>

      <UCard v-if="budgets.length === 0 && !loading" class="col-span-full">
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
          <UFormGroup label="Nom du budget" required>
            <UInput
              v-model="form.name"
              placeholder="Ex: Budget alimentation mensuel"
              required
            />
          </UFormGroup>

          <!-- Category -->
          <UFormGroup label="Catégorie" required>
            <USelectMenu
              v-model="form.category"
              :options="categories"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner une catégorie"
            />
          </UFormGroup>

          <!-- Amount -->
          <UFormGroup label="Montant (CHF)" required>
            <UInput
              v-model="form.amount"
              type="number"
              step="0.01"
              placeholder="0.00"
              required
            />
          </UFormGroup>

          <!-- Period -->
          <UFormGroup label="Période" required>
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
            <UFormGroup label="Date de début" required>
              <UInput v-model="form.start_date" type="date" required />
            </UFormGroup>
            <UFormGroup label="Date de fin (optionnelle)">
              <UInput v-model="form.end_date" type="date" />
            </UFormGroup>
          </div>

          <!-- Alert Threshold -->
          <UFormGroup label="Seuil d'alerte (%)">
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
  </div>
</template>
