<template>
  <div>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Calculateur d'objectif d'épargne
      </h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">
        Planifiez l'achat d'un objet en calculant votre épargne nécessaire
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Wizard -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Étape 1 : Informations sur l'objet -->
        <UCard>
          <template #header>
            <div class="flex items-center gap-2">
              <UBadge :color="step >= 1 ? 'primary' : 'gray'" variant="solid" size="sm">1</UBadge>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">L'objet</h2>
            </div>
          </template>

          <div class="space-y-4">
            <UFormGroup label="Nom de l'objet" required :error="formErrors.label">
              <UInput
                v-model="form.label"
                placeholder="Ex: MacBook Pro M4"
                icon="i-heroicons-shopping-bag"
              />
            </UFormGroup>

            <UFormGroup label="Prix total (CHF)" required :error="formErrors.target_amount">
              <UInput
                v-model="form.target_amount"
                type="number"
                step="0.01"
                placeholder="0.00"
                icon="i-heroicons-banknotes"
              />
            </UFormGroup>

            <UFormGroup label="URL du produit (optionnel)">
              <UInput
                v-model="form.product_url"
                type="url"
                placeholder="https://..."
                icon="i-heroicons-link"
              />
            </UFormGroup>

            <div class="flex justify-end">
              <UButton @click="goToStep2" :disabled="!form.label || !form.target_amount">
                Continuer
              </UButton>
            </div>
          </div>
        </UCard>

        <!-- Étape 2 : Mode de calcul -->
        <UCard v-if="step >= 2">
          <template #header>
            <div class="flex items-center gap-2">
              <UBadge :color="step >= 2 ? 'primary' : 'gray'" variant="solid" size="sm">2</UBadge>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Mode de calcul</h2>
            </div>
          </template>

          <div class="space-y-4">
            <!-- Sélection du mode -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button
                type="button"
                @click="form.mode = 'A'"
                :class="[
                  'p-4 border-2 rounded-lg cursor-pointer transition-colors text-left w-full',
                  form.mode === 'A'
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                ]"
                :aria-pressed="form.mode === 'A'"
              >
                <p class="font-semibold text-gray-900 dark:text-white">Mode A</p>
                <p class="text-sm text-gray-500">Je connais ma capacité d'épargne</p>
              </button>
              <button
                type="button"
                @click="form.mode = 'B'"
                :class="[
                  'p-4 border-2 rounded-lg cursor-pointer transition-colors text-left w-full',
                  form.mode === 'B'
                    ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                ]"
                :aria-pressed="form.mode === 'B'"
              >
                <p class="font-semibold text-gray-900 dark:text-white">Mode B</p>
                <p class="text-sm text-gray-500">Je connais ma date cible</p>
              </button>
            </div>

            <!-- Mode A : Épargne connue -->
            <div v-if="form.mode === 'A'" class="space-y-4">
              <UFormGroup label="Montant que vous pouvez épargner" required>
                <UInput
                  v-model="form.saving_amount"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  icon="i-heroicons-banknotes"
                />
              </UFormGroup>
              <UFormGroup label="Fréquence" required>
                <USelectMenu
                  v-model="form.saving_frequency"
                  :options="frequencyOptions"
                  option-attribute="label"
                  value-attribute="value"
                />
              </UFormGroup>
            </div>

            <!-- Mode B : Date cible -->
            <div v-if="form.mode === 'B'" class="space-y-4">
              <UFormGroup label="Date cible" required>
                <UInput
                  v-model="form.target_date"
                  type="date"
                  :min="minDate"
                />
              </UFormGroup>
              <UFormGroup label="Fréquence d'épargne" required>
                <USelectMenu
                  v-model="form.saving_frequency"
                  :options="frequencyOptions"
                  option-attribute="label"
                  value-attribute="value"
                />
              </UFormGroup>
            </div>

            <div class="flex justify-between">
              <UButton variant="soft" @click="step = 1">Retour</UButton>
              <UButton
                @click="handleCalculate"
                :loading="calculating"
                :disabled="!canCalculate"
              >
                Calculer
              </UButton>
            </div>
          </div>
        </UCard>

        <!-- Étape 3 : Résultat -->
        <UCard v-if="step >= 3 && result">
          <template #header>
            <div class="flex items-center gap-2">
              <UBadge color="green" variant="solid" size="sm">3</UBadge>
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Résultat</h2>
            </div>
          </template>

          <div class="space-y-4">
            <!-- Résumé -->
            <div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <div v-if="result.calculated_result?.mode === 'date_calculated'">
                <p class="text-sm text-gray-600 dark:text-gray-400">Date d'achat estimée</p>
                <p class="text-2xl font-bold text-green-600 dark:text-green-400">
                  {{ formatDateDisplay(result.calculated_result.target_date!) }}
                </p>
                <p class="text-sm text-gray-500 mt-1">
                  soit {{ result.calculated_result.periods_needed }} {{ frequencyLabel(form.saving_frequency) }}(s)
                  de {{ formatCurrency(parseFloat(form.saving_amount)) }}
                </p>
              </div>
              <div v-else-if="result.calculated_result?.mode === 'amount_calculated'">
                <p class="text-sm text-gray-600 dark:text-gray-400">Montant à épargner par {{ frequencyLabel(form.saving_frequency) }}</p>
                <p class="text-2xl font-bold text-green-600 dark:text-green-400">
                  {{ formatCurrency(result.calculated_result.saving_amount!) }}
                </p>
                <p class="text-sm text-gray-500 mt-1">
                  pendant {{ result.calculated_result.periods_needed }} {{ frequencyLabel(form.saving_frequency) }}(s)
                </p>
              </div>
            </div>

            <!-- Budgets liés -->
            <div v-if="result.linked_budgets && result.linked_budgets.length > 0" class="space-y-2">
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Budgets liés :</p>
              <div v-for="b in result.linked_budgets" :key="b.id" class="flex items-center gap-2 text-sm">
                <UIcon name="i-heroicons-check-circle" class="h-4 w-4 text-green-500" />
                <span>{{ b.name }} - {{ formatCurrency(b.amount) }}</span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-2">
              <UButton
                @click="handleCreateBudget"
                :loading="creatingBudget"
                icon="i-heroicons-plus-circle"
                :disabled="budgetCreated"
              >
                {{ budgetCreated ? 'Budget créé' : 'Créer le budget automatiquement' }}
              </UButton>
              <UButton variant="soft" @click="resetForm">
                Nouveau calcul
              </UButton>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Sidebar : Liste des objectifs existants -->
      <div>
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Mes objectifs</h3>
          </template>

          <div v-if="loadingGoals" class="flex justify-center py-4">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin h-6 w-6 text-gray-400" />
          </div>

          <div v-else-if="goalsError" class="text-center py-4">
            <UIcon name="i-heroicons-exclamation-circle" class="h-8 w-8 text-red-400 mx-auto mb-2" />
            <p class="text-sm text-gray-500 mb-2">Impossible de charger les objectifs</p>
            <UButton size="xs" variant="soft" @click="fetchGoals">Réessayer</UButton>
          </div>

          <div v-else-if="goals.length === 0" class="text-center py-4 text-gray-500 text-sm">
            Aucun objectif d'épargne
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="goal in goals"
              :key="goal.id"
              class="p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="font-medium text-sm text-gray-900 dark:text-white">{{ goal.label }}</span>
                <UBadge
                  :color="goal.status === 'active' ? 'blue' : goal.status === 'reached' ? 'green' : 'gray'"
                  variant="subtle"
                  size="xs"
                >
                  {{ goal.status_display }}
                </UBadge>
              </div>
              <p class="text-sm text-gray-500">{{ formatCurrency(parseFloat(goal.target_amount)) }}</p>
              <div class="flex justify-end mt-2">
                <UButton
                  size="xs"
                  color="red"
                  variant="ghost"
                  icon="i-heroicons-trash"
                  aria-label="Supprimer l'objectif"
                  @click="handleDeleteGoal(goal.id)"
                />
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </div>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer l'objectif"
      message="Êtes-vous sûr de vouloir supprimer cet objectif d'épargne ?"
      confirm-label="Supprimer"
      @confirm="executeDeleteGoal"
    />
  </div>
</template>

<script setup lang="ts">
import type { SavingsGoal } from '~/types'

definePageMeta({
  middleware: 'auth'
})

const { createSavingsGoal, getSavingsGoals, deleteSavingsGoal, createBudgetFromGoal } = useSavingsGoals()
const toast = useToast()

// State
const step = ref(1)
const calculating = ref(false)
const creatingBudget = ref(false)
const budgetCreated = ref(false)
const loadingGoals = ref(false)
const goalsError = ref(false)
const result = ref<SavingsGoal | null>(null)
const goals = ref<SavingsGoal[]>([])
const formErrors = ref<Record<string, string>>({})

const form = ref({
  label: '',
  target_amount: '',
  product_url: '',
  mode: 'A' as 'A' | 'B',
  saving_amount: '',
  saving_frequency: 'monthly',
  target_date: '',
})

const frequencyOptions = [
  { label: 'Par jour', value: 'daily' },
  { label: 'Par semaine', value: 'weekly' },
  { label: 'Par mois', value: 'monthly' },
  { label: 'Par an', value: 'yearly' },
]

const minDate = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
})

const canCalculate = computed(() => {
  if (form.value.mode === 'A') {
    return !!form.value.saving_amount && parseFloat(form.value.saving_amount) > 0
  }
  return !!form.value.target_date
})

const goToStep2 = () => {
  formErrors.value = {}
  if (!form.value.label) {
    formErrors.value.label = 'Le nom est requis'
    return
  }
  if (!form.value.target_amount || parseFloat(form.value.target_amount) <= 0) {
    formErrors.value.target_amount = 'Le prix doit être positif'
    return
  }
  step.value = 2
}

const handleCalculate = async () => {
  calculating.value = true

  const payload: any = {
    label: form.value.label,
    target_amount: form.value.target_amount,
    product_url: form.value.product_url || null,
    saving_frequency: form.value.saving_frequency,
  }

  if (form.value.mode === 'A') {
    payload.saving_amount = form.value.saving_amount
  } else {
    payload.target_date = form.value.target_date
  }

  const res = await createSavingsGoal(payload)
  calculating.value = false

  if (res.success && res.data) {
    result.value = res.data
    step.value = 3
    budgetCreated.value = false
    await fetchGoals()
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de créer l\'objectif', color: 'red' })
  }
}

const handleCreateBudget = async () => {
  if (!result.value) return
  creatingBudget.value = true

  const res = await createBudgetFromGoal(result.value.id)
  creatingBudget.value = false

  if (res.success) {
    budgetCreated.value = true
    toast.add({ title: 'Budget créé', description: res.data?.message || 'Budget créé avec succès', color: 'green' })
    // Refresh pour voir linked_budgets
    const updated = await useSavingsGoals().getSavingsGoal(result.value.id)
    if (updated.success && updated.data) {
      result.value = updated.data
    }
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de créer le budget', color: 'red' })
  }
}

const resetForm = () => {
  step.value = 1
  result.value = null
  budgetCreated.value = false
  formErrors.value = {}
  form.value = {
    label: '',
    target_amount: '',
    product_url: '',
    mode: 'A',
    saving_amount: '',
    saving_frequency: 'monthly',
    target_date: '',
  }
}

const fetchGoals = async () => {
  loadingGoals.value = true
  goalsError.value = false
  const res = await getSavingsGoals()
  if (res.success && res.data) {
    goals.value = res.data.results
  } else {
    goalsError.value = true
  }
  loadingGoals.value = false
}

// Confirm modal state
const showConfirmDelete = ref(false)
const goalToDelete = ref<number | null>(null)

const handleDeleteGoal = (id: number) => {
  goalToDelete.value = id
  showConfirmDelete.value = true
}

const executeDeleteGoal = async () => {
  if (goalToDelete.value === null) return
  const res = await deleteSavingsGoal(goalToDelete.value)
  goalToDelete.value = null
  if (res.success) {
    toast.add({ title: 'Supprimé', description: 'Objectif supprimé', color: 'green' })
    await fetchGoals()
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-CH', {
    style: 'currency',
    currency: 'CHF'
  }).format(amount)
}

const formatDateDisplay = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const frequencyLabel = (freq: string) => {
  const map: Record<string, string> = {
    daily: 'jour',
    weekly: 'semaine',
    monthly: 'mois',
    yearly: 'année',
  }
  return map[freq] || freq
}

onMounted(() => {
  fetchGoals()
})
</script>
