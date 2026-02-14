<template>
  <div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl mx-auto">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Profil et Configuration
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Configurez votre profil financier
        </p>
      </div>

      <!-- Financial Profile Card -->
      <UCard class="mb-6">
        <template #header>
          <div class="flex items-center">
            <UIcon name="i-heroicons-banknotes" class="h-6 w-6 text-primary-600 mr-2" />
            <h2 class="text-xl font-semibold">Informations financières</h2>
          </div>
        </template>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Monthly Income -->
          <UFormGroup label="Revenu mensuel" required>
            <UInput
              v-model="form.monthly_income"
              type="number"
              step="0.01"
              placeholder="0.00"
              icon="i-heroicons-currency-dollar"
              required
            >
              <template #trailing>
                <span class="text-gray-500">CHF</span>
              </template>
            </UInput>
            <template #help>
              <p class="text-sm text-gray-500">
                Votre revenu mensuel total disponible pour vos budgets. Cela vous aidera à suivre combien vous pouvez encore allouer à vos budgets.
              </p>
            </template>
          </UFormGroup>

          <!-- Currency -->
          <UFormGroup label="Devise" required>
            <USelectMenu
              v-model="form.currency"
              :options="[
                { label: 'Franc Suisse (CHF)', value: 'CHF' },
                { label: 'Euro (EUR)', value: 'EUR' },
                { label: 'Dollar US (USD)', value: 'USD' },
                { label: 'Livre Sterling (GBP)', value: 'GBP' }
              ]"
              option-attribute="label"
              value-attribute="value"
            />
          </UFormGroup>

          <!-- Salary Day -->
          <UFormGroup label="Jour de versement du salaire">
            <UInput
              v-model="form.salary_day"
              type="number"
              min="1"
              max="28"
              placeholder="25"
              icon="i-heroicons-calendar"
            />
            <template #help>
              <p class="text-sm text-gray-500">
                Jour du mois où votre salaire est versé (1-28). Utilisé pour créer la transaction récurrente à la bonne date.
              </p>
            </template>
          </UFormGroup>

          <!-- Available Budget Info (if profile exists) -->
          <div v-if="profile && profile.available_budget_info" class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h3 class="font-semibold text-blue-900 dark:text-blue-200 mb-3">Aperçu de votre budget</h3>
            <div class="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p class="text-gray-600 dark:text-gray-400">Revenu mensuel</p>
                <p class="font-bold text-gray-900 dark:text-white">{{ profile.available_budget_info.monthly_income.toFixed(2) }} CHF</p>
              </div>
              <div>
                <p class="text-gray-600 dark:text-gray-400">Budget alloué</p>
                <p class="font-bold text-blue-600">{{ profile.available_budget_info.total_allocated.toFixed(2) }} CHF</p>
              </div>
              <div>
                <p class="text-gray-600 dark:text-gray-400">Budget disponible</p>
                <p class="font-bold" :class="profile.available_budget_info.available >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ profile.available_budget_info.available.toFixed(2) }} CHF
                </p>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-between items-center pt-4">
            <UButton
              v-if="form.monthly_income && parseFloat(form.monthly_income) > 0"
              :icon="salaryTransactionCreated ? 'i-heroicons-check-circle' : 'i-heroicons-arrow-path'"
              :color="salaryTransactionCreated ? 'green' : 'blue'"
              :variant="salaryTransactionCreated ? 'soft' : 'soft'"
              @click="createRecurringSalary"
              :loading="creatingRecurring"
              :disabled="salaryTransactionCreated"
            >
              {{ salaryTransactionCreated ? '✓ Transaction créée' : 'Créer transaction récurrente pour mon salaire' }}
            </UButton>
            <div v-else></div>
            <UButton type="submit" :loading="loading" size="lg">
              Enregistrer
            </UButton>
          </div>
        </form>
      </UCard>

      <!-- User Info Card -->
      <UCard>
        <template #header>
          <div class="flex items-center">
            <UIcon name="i-heroicons-user" class="h-6 w-6 text-primary-600 mr-2" />
            <h2 class="text-xl font-semibold">Informations du compte</h2>
          </div>
        </template>

        <div class="space-y-4">
          <div>
            <p class="text-sm text-gray-500">Nom d'utilisateur</p>
            <p class="font-medium">{{ user?.username }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Email</p>
            <p class="font-medium">{{ user?.email }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Membre depuis</p>
            <p class="font-medium">{{ formatDate(user?.date_joined) }}</p>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const { getProfile, updateProfile } = useUserProfile()
const { user } = useAuth()
const toast = useToast()

// State
const loading = ref(false)
const profile = ref<any>(null)
const form = ref({
  monthly_income: '',
  currency: 'CHF',
  salary_day: null as number | null
})
const creatingRecurring = ref(false)

// Fetch profile
const fetchProfile = async () => {
  const result = await getProfile()
  if (result.success && result.data) {
    profile.value = result.data
    form.value.monthly_income = result.data.monthly_income
    form.value.currency = result.data.currency
    form.value.salary_day = result.data.salary_day
  }
}

// Submit form
const handleSubmit = async () => {
  loading.value = true

  const result = await updateProfile({
    monthly_income: form.value.monthly_income,
    currency: form.value.currency,
    salary_day: form.value.salary_day ? parseInt(form.value.salary_day.toString()) : null
  })

  loading.value = false

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Profil mis à jour avec succès',
      color: 'green'
    })
    await fetchProfile()
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Une erreur est survenue lors de la mise à jour du profil',
      color: 'red'
    })
  }
}

// Créer transaction récurrente pour salaire
const salaryTransactionCreated = ref(false)

const createRecurringSalary = async () => {
  if (salaryTransactionCreated.value) {
    toast.add({
      title: 'Déjà créée',
      description: 'La transaction récurrente existe déjà',
      color: 'blue'
    })
    return
  }

  creatingRecurring.value = true
  const { apiFetch } = useApi()

  try {
    const response = await apiFetch('/api/v1/auth/profile/setup_recurring_salary/', {
      method: 'POST',
      body: {
        amount: form.value.monthly_income
      }
    })

    salaryTransactionCreated.value = true

    toast.add({
      title: '✅ Transaction créée !',
      description: 'Votre salaire mensuel récurrent a été configuré avec succès',
      color: 'green',
      timeout: 5000
    })
  } catch (error: any) {
    toast.add({
      title: 'Erreur',
      description: error.data?.error || 'Impossible de créer la transaction récurrente',
      color: 'red',
      timeout: 5000
    })
  } finally {
    creatingRecurring.value = false
  }
}

// Format date
const formatDate = (dateString: string | undefined) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// Load profile on mount
onMounted(() => {
  fetchProfile()
})
</script>
