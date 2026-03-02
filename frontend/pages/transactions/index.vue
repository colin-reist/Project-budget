<script setup lang="ts">
import type { Transaction, Account, Category } from '~/types'
import type { StandardError } from '~/types/errors'

definePageMeta({
  middleware: 'auth'
})

const { getTransactions, createTransaction, updateTransaction, deleteTransaction, getStatistics } = useTransactions()
const { getAccounts } = useAccounts()
const { getCategories } = useCategories()
const { getErrorForField, formatForToast } = useErrorHandler()
const { currency, ensureProfileLoaded } = useUserProfile()
const toast = useToast()

// State
const transactions = ref<Transaction[]>([])
const accounts = ref<Account[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const loadError = ref(false)
const showModal = ref(false)
const editingTransaction = ref<Transaction | null>(null)
const formErrors = ref<StandardError | null>(null)
const stats = ref({
  income: { total: 0, count: 0 },
  expense: { total: 0, count: 0 },
  transfer: { total: 0, count: 0 },
  net: 0
})

// Month navigation
const currentMonthDate = ref(new Date())
const currentMonthKey = computed(() => {
  const d = currentMonthDate.value
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
})
const currentMonthLabel = computed(() =>
  currentMonthDate.value.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
)
const goToPrevMonth = () => {
  const d = new Date(currentMonthDate.value)
  d.setMonth(d.getMonth() - 1)
  currentMonthDate.value = d
}
const goToNextMonth = () => {
  const d = new Date(currentMonthDate.value)
  d.setMonth(d.getMonth() + 1)
  currentMonthDate.value = d
}
const isCurrentMonth = computed(() => {
  const now = new Date()
  return currentMonthDate.value.getMonth() === now.getMonth() &&
         currentMonthDate.value.getFullYear() === now.getFullYear()
})

// Filters
const filters = ref({
  type: '' as '' | 'income' | 'expense' | 'transfer',
  account: '',
  category: '',
  search: ''
})

// Form
const form = ref({
  type: 'expense' as 'income' | 'expense' | 'transfer',
  account: '',
  category: '',
  destination_account: '',
  amount: '',
  description: '',
  date: new Date().toISOString().split('T')[0],
  notes: '',
  is_recurring: false,
  recurrence_frequency: '',
  recurrence_interval: 1,
  recurrence_end_date: ''
})

// Reset category when transaction type changes
watch(() => form.value.type, () => {
  form.value.category = ''
  form.value.destination_account = ''
})

// Computed
const filteredTransactions = computed(() => {
  return transactions.value.filter(t => {
    // Filter by selected month
    if (!t.date.startsWith(currentMonthKey.value)) return false
    if (filters.value.type && t.type !== filters.value.type) return false
    if (filters.value.account && t.account !== parseInt(filters.value.account)) return false
    if (filters.value.category && t.category !== parseInt(filters.value.category)) return false
    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      return t.description.toLowerCase().includes(search) ||
             t.notes?.toLowerCase().includes(search)
    }
    return true
  })
})

const today = new Date().toISOString().split('T')[0]

const monthTotals = computed(() => {
  let totalIncome = 0
  let totalExpense = 0
  for (const t of filteredTransactions.value) {
    if (t.type === 'income') totalIncome += parseFloat(t.amount)
    else if (t.type === 'expense') totalExpense += parseFloat(t.amount)
  }
  return { totalIncome, totalExpense, net: totalIncome - totalExpense }
})

const incomeCategories = computed(() => categories.value.filter(c => c.type === 'income'))
const expenseCategories = computed(() => categories.value.filter(c => c.type === 'expense'))
const availableCategories = computed(() => {
  if (form.value.type === 'income') return incomeCategories.value
  if (form.value.type === 'expense') return expenseCategories.value
  return []
})

// Methods
const fetchTransactions = async () => {
  loading.value = true
  loadError.value = false
  const result = await getTransactions({ ordering: '-date,-created_at' })
  if (result.success && result.data) {
    transactions.value = result.data.results
  } else {
    loadError.value = true
  }
  loading.value = false
}

const fetchAccounts = async () => {
  const result = await getAccounts()
  if (result.success && result.data) {
    accounts.value = result.data.results
  }
}

const fetchCategories = async () => {
  const result = await getCategories()
  if (result.success && result.data) {
    categories.value = result.data.results
  }
}

const fetchStats = async () => {
  const result = await getStatistics()
  if (result.success && result.data) {
    stats.value = result.data
  }
}

const openModal = (transaction?: Transaction) => {
  if (transaction) {
    editingTransaction.value = transaction
    // Si on a les détails de catégorie et qu'elle ne correspond pas au type, on réinitialise
    const catDetails = transaction.category_details
    const catMismatch = catDetails != null && catDetails.type !== transaction.type
    form.value = {
      type: transaction.type,
      account: transaction.account.toString(),
      category: catMismatch ? '' : (transaction.category?.toString() || ''),
      destination_account: transaction.destination_account?.toString() || '',
      amount: transaction.amount,
      description: transaction.description,
      date: transaction.date,
      notes: transaction.notes || '',
      is_recurring: transaction.is_recurring,
      recurrence_frequency: transaction.recurrence_frequency || '',
      recurrence_interval: transaction.recurrence_interval,
      recurrence_end_date: transaction.recurrence_end_date || ''
    }
  } else {
    editingTransaction.value = null
    form.value = {
      type: 'expense',
      account: '',
      category: '',
      destination_account: '',
      amount: '',
      description: '',
      date: new Date().toISOString().split('T')[0],
      notes: '',
      is_recurring: false,
      recurrence_frequency: '',
      recurrence_interval: 1,
      recurrence_end_date: ''
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingTransaction.value = null
  formErrors.value = null
}

const handleSubmit = async () => {
  loading.value = true
  formErrors.value = null

  const transactionData: any = {
    type: form.value.type,
    account: parseInt(form.value.account),
    amount: form.value.amount,
    description: form.value.description,
    date: form.value.date,
    is_recurring: form.value.is_recurring
  }

  // Add category for income/expense
  if (form.value.type !== 'transfer' && form.value.category) {
    transactionData.category = parseInt(form.value.category)
  }

  // Add destination account for transfer
  if (form.value.type === 'transfer' && form.value.destination_account) {
    transactionData.destination_account = parseInt(form.value.destination_account)
  }

  // Add optional fields
  if (form.value.notes) transactionData.notes = form.value.notes
  if (form.value.is_recurring) {
    transactionData.recurrence_frequency = form.value.recurrence_frequency
    transactionData.recurrence_interval = form.value.recurrence_interval
    if (form.value.recurrence_end_date) {
      transactionData.recurrence_end_date = form.value.recurrence_end_date
    }
  }

  let result
  if (editingTransaction.value) {
    result = await updateTransaction(editingTransaction.value.id, transactionData)
  } else {
    result = await createTransaction(transactionData)
  }

  loading.value = false

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: editingTransaction.value ? 'Transaction mise à jour' : 'Transaction créée',
      color: 'green'
    })
    closeModal()
    await fetchTransactions()
    await fetchStats()
  } else if (result.error) {
    // Capturer les erreurs pour affichage au niveau des champs
    formErrors.value = result.error

    // Afficher un toast avec les erreurs formatées
    const errorMessage = formatForToast(result.error)
    toast.add({
      title: 'Erreur',
      description: errorMessage,
      color: 'red'
    })
  }
}

// Confirm modal state
const showConfirmDelete = ref(false)
const transactionToDelete = ref<Transaction | null>(null)

const handleDelete = (transaction: Transaction) => {
  transactionToDelete.value = transaction
  showConfirmDelete.value = true
}

const executeDelete = async () => {
  if (!transactionToDelete.value) return

  loading.value = true
  const result = await deleteTransaction(transactionToDelete.value.id)
  loading.value = false
  transactionToDelete.value = null

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Transaction supprimée',
      color: 'green'
    })
    await fetchTransactions()
    await fetchStats()
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Impossible de supprimer la transaction',
      color: 'red'
    })
  }
}

const getTransactionColor = (type: string) => {
  switch (type) {
    case 'income': return 'green'
    case 'expense': return 'red'
    case 'transfer': return 'blue'
    default: return 'gray'
  }
}

// Lifecycle
onMounted(async () => {
  await ensureProfileLoaded()
  fetchTransactions()
  fetchAccounts()
  fetchCategories()
  fetchStats()
})
</script>

<template>
  <div class="container mx-auto px-4 py-6 sm:py-8">
    <div class="flex justify-between items-center mb-6 sm:mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold">Transactions</h1>
      <UButton icon="i-heroicons-plus" size="lg" class="sm:hidden" aria-label="Nouvelle transaction" @click="openModal()" />
      <UButton icon="i-heroicons-plus" size="lg" class="hidden sm:inline-flex" @click="openModal()">
        Nouvelle transaction
      </UButton>
    </div>

    <!-- Statistics Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
      <UCard>
        <div class="text-sm text-gray-500">Revenus</div>
        <div class="text-2xl font-bold text-green-600">{{ formatCurrency(stats.income.total) }}</div>
        <div class="text-xs text-gray-400">{{ stats.income.count }} transactions</div>
      </UCard>
      <UCard>
        <div class="text-sm text-gray-500">Dépenses</div>
        <div class="text-2xl font-bold text-red-600">{{ formatCurrency(stats.expense.total) }}</div>
        <div class="text-xs text-gray-400">{{ stats.expense.count }} transactions</div>
      </UCard>
      <UCard>
        <div class="text-sm text-gray-500">Transferts</div>
        <div class="text-2xl font-bold text-blue-600">{{ formatCurrency(stats.transfer.total) }}</div>
        <div class="text-xs text-gray-400">{{ stats.transfer.count }} transactions</div>
      </UCard>
      <UCard>
        <div class="text-sm text-gray-500">Solde net</div>
        <div class="text-2xl font-bold" :class="stats.net >= 0 ? 'text-green-600' : 'text-red-600'">
          {{ stats.net >= 0 ? '+' : '' }}{{ formatCurrency(Math.abs(stats.net)) }}
        </div>
        <div class="text-xs text-gray-400">Revenus - Dépenses</div>
      </UCard>
    </div>

    <!-- Filters -->
    <UCard class="mb-4 sm:mb-6">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <USelectMenu
          v-model="filters.type"
          :options="[
            { label: 'Tous les types', value: '' },
            { label: 'Revenus', value: 'income' },
            { label: 'Dépenses', value: 'expense' },
            { label: 'Transferts', value: 'transfer' }
          ]"
          option-attribute="label"
          value-attribute="value"
          placeholder="Type"
        />
        <USelectMenu
          v-model="filters.account"
          :options="[{ id: '', name: 'Tous les comptes' }, ...accounts]"
          option-attribute="name"
          value-attribute="id"
          placeholder="Compte"
        />
        <USelectMenu
          v-model="filters.category"
          :options="[{ id: '', name: 'Toutes les catégories' }, ...categories]"
          option-attribute="name"
          value-attribute="id"
          placeholder="Catégorie"
        />
        <UInput v-model="filters.search" placeholder="Rechercher..." icon="i-heroicons-magnifying-glass" class="col-span-2 md:col-span-1" />
      </div>
    </UCard>

    <!-- Month Navigator -->
    <div class="flex items-center justify-between mb-4">
      <UButton icon="i-heroicons-chevron-left" color="gray" variant="ghost" size="lg" @click="goToPrevMonth" aria-label="Mois précédent" />
      <div class="text-center">
        <div class="font-semibold text-lg capitalize">{{ currentMonthLabel }}</div>
        <div v-if="monthTotals.totalIncome > 0 || monthTotals.totalExpense > 0" class="flex items-center justify-center gap-3 text-xs mt-0.5">
          <span v-if="monthTotals.totalIncome > 0" class="text-green-600">+{{ formatCurrency(monthTotals.totalIncome) }}</span>
          <span v-if="monthTotals.totalExpense > 0" class="text-red-600">-{{ formatCurrency(monthTotals.totalExpense) }}</span>
          <span :class="monthTotals.net >= 0 ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'">
            = {{ formatCurrency(monthTotals.net) }}
          </span>
        </div>
      </div>
      <UButton icon="i-heroicons-chevron-right" color="gray" variant="ghost" size="lg" :disabled="isCurrentMonth" @click="goToNextMonth" aria-label="Mois suivant" />
    </div>

    <!-- Transactions List -->
    <UCard>
      <!-- Loading State -->
      <div v-if="loading" class="space-y-4">
        <div v-for="i in 5" :key="i" class="py-4 flex items-center justify-between">
          <div class="flex items-center gap-4 flex-1">
            <USkeleton class="h-12 w-12 rounded-full" />
            <div class="space-y-2 flex-1">
              <USkeleton class="h-4 w-48" />
              <USkeleton class="h-3 w-32" />
              <USkeleton class="h-3 w-24" />
            </div>
            <USkeleton class="h-6 w-24" />
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="loadError">
        <EmptyState
          icon="i-heroicons-exclamation-circle"
          color="red"
          title="Impossible de charger les transactions"
          description="Vérifiez votre connexion internet et réessayez."
          button-text="Réessayer"
          button-icon="i-heroicons-arrow-path"
          @action="fetchTransactions(); fetchStats()"
        />
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredTransactions.length === 0">
        <EmptyState
          icon="i-heroicons-arrows-right-left"
          color="purple"
          title="Aucune transaction trouvée"
          description="Commencez à suivre vos finances en créant votre première transaction. Revenus, dépenses ou transferts, tout est possible!"
          button-text="Créer une transaction"
          @action="openModal()"
        />
      </div>

      <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="transaction in filteredTransactions"
          :key="transaction.id"
          class="py-3 sm:py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800/50 px-4 -mx-4 transition-colors"
          :class="transaction.date > today ? 'opacity-70' : ''"
        >
          <div class="flex items-center gap-3 sm:gap-4 flex-1 min-w-0">
            <div
              class="w-10 h-10 sm:w-12 sm:h-12 rounded-full flex-shrink-0 flex items-center justify-center relative"
              :class="`bg-${getTransactionColor(transaction.type)}-100 dark:bg-${getTransactionColor(transaction.type)}-900/30`"
            >
              <UIcon
                :name="transaction.type === 'income' ? 'i-heroicons-arrow-down-circle' : transaction.type === 'expense' ? 'i-heroicons-arrow-up-circle' : 'i-heroicons-arrow-right-circle'"
                :class="`text-${getTransactionColor(transaction.type)}-600 text-lg sm:text-xl`"
              />
              <UIcon
                v-if="transaction.date > today"
                name="i-heroicons-clock"
                class="absolute -bottom-0.5 -right-0.5 text-amber-500 bg-white dark:bg-gray-900 rounded-full text-xs"
              />
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-medium text-sm sm:text-base truncate">{{ transaction.description }}</div>
              <div class="text-xs sm:text-sm text-gray-500 truncate">
                {{ transaction.account_details?.name }}
                <template v-if="transaction.type === 'transfer' && transaction.destination_account_details">
                  → {{ transaction.destination_account_details.name }}
                </template>
                <template v-else-if="transaction.category_details">
                  · {{ transaction.category_details.name }}
                </template>
              </div>
              <div class="text-xs text-gray-400">{{ new Date(transaction.date + 'T00:00:00').toLocaleDateString('fr-FR') }}</div>
            </div>
            <div class="text-right flex-shrink-0 ml-2">
              <div
                class="text-base sm:text-lg font-semibold"
                :class="`text-${getTransactionColor(transaction.type)}-600`"
              >
                {{ transaction.type === 'expense' ? '-' : '+' }}{{ transaction.amount }} {{ transaction.account_details?.currency }}
              </div>
            </div>
          </div>
          <div class="flex gap-1 ml-2 sm:ml-4 flex-shrink-0">
            <UButton
              icon="i-heroicons-pencil"
              size="sm"
              color="gray"
              variant="ghost"
              class="min-h-[40px] min-w-[40px]"
              aria-label="Modifier la transaction"
              @click="openModal(transaction)"
            />
            <UButton
              icon="i-heroicons-trash"
              size="sm"
              color="red"
              variant="ghost"
              class="min-h-[40px] min-w-[40px]"
              aria-label="Supprimer la transaction"
              @click="handleDelete(transaction)"
            />
          </div>
        </div>
      </div>
    </UCard>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer la transaction"
      :message="`Supprimer la transaction « ${transactionToDelete?.description || 'Sans description'} » de ${transactionToDelete?.amount} ?`"
      confirm-label="Supprimer"
      @confirm="executeDelete"
    />

    <!-- Transaction Modal -->
    <UModal v-model="showModal" :ui="{ width: 'sm:max-w-2xl' }">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ editingTransaction ? 'Modifier la transaction' : 'Nouvelle transaction' }}
          </h3>
        </template>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Type -->
          <UFormGroup label="Type" required>
            <USelectMenu
              v-model="form.type"
              :options="[
                { label: 'Revenu', value: 'income' },
                { label: 'Dépense', value: 'expense' },
                { label: 'Transfert', value: 'transfer' }
              ]"
              option-attribute="label"
              value-attribute="value"
            />
          </UFormGroup>

          <!-- Account -->
          <UFormGroup label="Compte" required>
            <USelectMenu
              v-model="form.account"
              :options="accounts"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner un compte"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'account')" />
          </UFormGroup>

          <!-- Category (for income/expense) -->
          <UFormGroup v-if="form.type !== 'transfer'" label="Catégorie" required>
            <USelectMenu
              v-model="form.category"
              :options="availableCategories"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner une catégorie"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'category')" />
          </UFormGroup>

          <!-- Destination Account (for transfer) -->
          <UFormGroup v-if="form.type === 'transfer'" label="Compte destination" required>
            <USelectMenu
              v-model="form.destination_account"
              :options="accounts.filter(a => a.id.toString() !== form.account)"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner un compte"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'destination_account')" />
          </UFormGroup>

          <!-- Amount -->
          <UFormGroup label="Montant" required>
            <UInput
              v-model="form.amount"
              type="number"
              step="0.01"
              placeholder="0.00"
              required
            />
            <FormFieldError :error="getErrorForField(formErrors, 'amount')" />
          </UFormGroup>

          <!-- Description -->
          <UFormGroup label="Description">
            <UInput
              v-model="form.description"
              placeholder="Description de la transaction"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'description')" />
          </UFormGroup>

          <!-- Date -->
          <UFormGroup label="Date" required>
            <UInput v-model="form.date" type="date" required />
            <FormFieldError :error="getErrorForField(formErrors, 'date')" />
          </UFormGroup>

          <!-- Notes -->
          <UFormGroup label="Notes">
            <UTextarea v-model="form.notes" placeholder="Notes additionnelles..." />
          </UFormGroup>

          <!-- Recurring -->
          <UFormGroup>
            <UCheckbox v-model="form.is_recurring" label="Transaction récurrente" />
          </UFormGroup>

          <!-- Recurrence settings -->
          <template v-if="form.is_recurring">
            <div class="grid grid-cols-2 gap-4">
              <UFormGroup label="Fréquence">
                <USelectMenu
                  v-model="form.recurrence_frequency"
                  :options="[
                    { label: 'Quotidien', value: 'daily' },
                    { label: 'Hebdomadaire', value: 'weekly' },
                    { label: 'Mensuel', value: 'monthly' },
                    { label: 'Annuel', value: 'yearly' }
                  ]"
                  option-attribute="label"
                  value-attribute="value"
                />
              </UFormGroup>
              <UFormGroup label="Intervalle">
                <UInput v-model.number="form.recurrence_interval" type="number" min="1" />
              </UFormGroup>
            </div>
            <UFormGroup label="Date de fin (optionnelle)">
              <UInput v-model="form.recurrence_end_date" type="date" />
            </UFormGroup>
          </template>

          <!-- Actions -->
          <div class="flex justify-end gap-2 pt-4">
            <UButton color="gray" variant="ghost" @click="closeModal">
              Annuler
            </UButton>
            <UButton type="submit" :loading="loading">
              {{ editingTransaction ? 'Mettre à jour' : 'Créer' }}
            </UButton>
          </div>
        </form>
      </UCard>
    </UModal>
  </div>
</template>
