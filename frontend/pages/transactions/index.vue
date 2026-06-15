<script setup lang="ts">
import type { Transaction, Account, Category } from '~/types'
import type { StandardError } from '~/types/errors'

definePageMeta({ middleware: 'auth' })

const { getTransactions, createTransaction, updateTransaction, deleteTransaction, generateRecurring } = useTransactions()
const { updateSeries } = useRecurring()
const { getAccounts } = useAccounts()
const { getCategories } = useCategories()
const { getBudgets } = useBudgets()
const { getErrorForField, formatForToast } = useErrorHandler()
const { ensureProfileLoaded, budgetStartDay, getCurrentBudgetMonth, getBudgetPeriodDates } = useUserProfile()
const toast = useToast()

// ── Data ────────────────────────────────────────────────────
const transactions = ref<Transaction[]>([])
const accounts = ref<Account[]>([])
const categories = ref<Category[]>([])
const spendingBudgets = ref<{ id: number; name: string }[]>([])
const loading = ref(false)
const loadError = ref(false)

// ── Month navigation ─────────────────────────────────────────
const currentMonthDate = ref(new Date())

const today = new Date().toISOString().split('T')[0]

// ── Filters ──────────────────────────────────────────────────
const filters = ref({ type: 'all', account: 'all', category: 'all', search: '' })
const isFiltered = computed(() =>
  !!filters.value.search || filters.value.type !== 'all' || filters.value.account !== 'all' || filters.value.category !== 'all'
)
const resetFilters = () => { filters.value = { type: 'all', account: 'all', category: 'all', search: '' } }

// ── Dropdown open state ──────────────────────────────────────
const openDropdown = ref<string | null>(null)
const toggleDropdown = (name: string) => {
  openDropdown.value = openDropdown.value === name ? null : name
}
const closeDropdowns = () => { openDropdown.value = null }

// ── Selection (checkboxes) ───────────────────────────────────
const selectedIds = ref(new Set<number>())
const isSelected = (id: number) => selectedIds.value.has(id)
const toggleSelect = (id: number) => {
  const s = new Set(selectedIds.value)
  s.has(id) ? s.delete(id) : s.add(id)
  selectedIds.value = s
}
const toggleDaySelect = (txns: Transaction[]) => {
  const allSelected = txns.every(t => selectedIds.value.has(t.id))
  const s = new Set(selectedIds.value)
  if (allSelected) txns.forEach(t => s.delete(t.id)); else txns.forEach(t => s.add(t.id))
  selectedIds.value = s
}
const clearSelected = () => { selectedIds.value = new Set() }
const bulkDelete = async () => {
  const ids = [...selectedIds.value]
  clearSelected()
  await Promise.all(ids.map(id => deleteTransaction(id)))
  await fetchTransactions()
  toast.add({ title: 'Succès', description: `${ids.length} transaction${ids.length > 1 ? 's supprimées' : ' supprimée'}`, color: 'green' })
}

// ── Computed filtered + grouped ──────────────────────────────
const filteredTransactions = computed(() => {
  return transactions.value.filter(t => {
    if (filters.value.type !== 'all' && t.type !== filters.value.type) return false
    if (filters.value.account !== 'all' && t.account !== parseInt(filters.value.account)) return false
    if (filters.value.category !== 'all' && t.category !== parseInt(filters.value.category)) return false
    if (filters.value.search) {
      const q = filters.value.search.toLowerCase()
      return t.description.toLowerCase().includes(q) || t.notes?.toLowerCase().includes(q) || t.category_name?.toLowerCase().includes(q)
    }
    return true
  })
})

const groupedByDay = computed(() => {
  const map = new Map<string, Transaction[]>()
  for (const t of filteredTransactions.value) {
    if (!map.has(t.date)) map.set(t.date, [])
    map.get(t.date)!.push(t)
  }
  return [...map.entries()].sort((a, b) => b[0].localeCompare(a[0]))
})

const monthTotals = computed(() => {
  let totalIncome = 0, countIncome = 0, totalExpense = 0, countExpense = 0
  for (const t of filteredTransactions.value) {
    if (t.type === 'income') { totalIncome += parseFloat(t.amount); countIncome++ }
    else if (t.type === 'expense') { totalExpense += parseFloat(t.amount); countExpense++ }
  }
  return { totalIncome, countIncome, totalExpense, countExpense, net: totalIncome - totalExpense }
})

// ── Helpers ──────────────────────────────────────────────────
const dayLabel = (isoDate: string): string => {
  const todayStr = new Date().toISOString().split('T')[0]
  const yesterdayStr = new Date(Date.now() - 86400000).toISOString().split('T')[0]
  if (isoDate === todayStr) return "Aujourd'hui"
  if (isoDate === yesterdayStr) return 'Hier'
  const d = new Date(isoDate + 'T00:00:00')
  const wd = d.toLocaleDateString('fr-FR', { weekday: 'long' })
  const diff = Math.round((new Date(todayStr).getTime() - d.getTime()) / 86400000)
  if (diff < 7) return wd.charAt(0).toUpperCase() + wd.slice(1)
  return d.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })
}

const dayNet = (txns: Transaction[]): number =>
  txns.reduce((s, t) => t.type === 'income' ? s + parseFloat(t.amount) : t.type === 'expense' ? s - parseFloat(t.amount) : s, 0)

const isDayAllSelected = (txns: Transaction[]) => txns.length > 0 && txns.every(t => selectedIds.value.has(t.id))
const isDaySomeSelected = (txns: Transaction[]) => txns.some(t => selectedIds.value.has(t.id))

const typeIcon = (type: string): string => ({ income: 'i-heroicons-arrow-trending-up', expense: 'i-heroicons-arrow-trending-down', transfer: 'i-heroicons-arrows-right-left' }[type] || 'i-heroicons-banknotes')
const typeIconColor = (type: string): string => ({ income: '#16a34a', expense: 'var(--ink-2)', transfer: 'var(--accent)' }[type] || 'var(--ink-3)')

const categoryChipColor = (type: string) => ({
  income:   { bg: 'color-mix(in oklab, #16a34a 10%, var(--surface))',        border: 'color-mix(in oklab, #16a34a 22%, transparent)',        color: '#16a34a' },
  expense:  { bg: 'color-mix(in oklab, var(--accent) 10%, var(--surface))',  border: 'color-mix(in oklab, var(--accent) 22%, transparent)',  color: 'var(--accent)' },
  transfer: { bg: 'color-mix(in oklab, var(--ink-3) 10%, var(--surface))',   border: 'color-mix(in oklab, var(--ink-3) 22%, transparent)',   color: 'var(--ink-3)' },
}[type] || { bg: 'var(--surface-2)', border: 'var(--line)', color: 'var(--ink-3)' })

// ── Form state ───────────────────────────────────────────────
const showModal = ref(false)
const editingTransaction = ref<Transaction | null>(null)
const editingAsSeries = ref(false)
const formErrors = ref<StandardError | null>(null)
const form = ref({
  type: 'expense' as 'income' | 'expense' | 'transfer',
  account: '', category: '', destination_account: '',
  amount: '', description: '', date: new Date().toISOString().split('T')[0],
  notes: '', is_recurring: false, recurrence_frequency: '', recurrence_interval: 1, recurrence_end_date: '',
  refund_budget: null as number | null,
})

watch(() => form.value.type, () => { form.value.category = ''; form.value.destination_account = ''; form.value.refund_budget = null })

const incomeCategories = computed(() => categories.value.filter(c => c.type === 'income'))
const expenseCategories = computed(() => categories.value.filter(c => c.type === 'expense'))
const availableCategories = computed(() => form.value.type === 'income' ? incomeCategories.value : form.value.type === 'expense' ? expenseCategories.value : [])

const openModal = (transaction?: Transaction) => {
  if (transaction) {
    editingTransaction.value = transaction
    const catMismatch = transaction.category_details != null && transaction.category_details.type !== transaction.type
    form.value = {
      type: (transaction.type === 'adjustment' ? 'expense' : transaction.type) as 'income' | 'expense' | 'transfer', account: transaction.account.toString(),
      category: catMismatch ? '' : (transaction.category?.toString() || ''),
      destination_account: transaction.destination_account?.toString() || '',
      amount: transaction.amount, description: transaction.description, date: transaction.date,
      notes: transaction.notes || '', is_recurring: transaction.is_recurring,
      recurrence_frequency: transaction.recurrence_frequency || '',
      recurrence_interval: transaction.recurrence_interval,
      recurrence_end_date: transaction.recurrence_end_date || '',
      refund_budget: transaction.refund_budget ?? null,
    }
  } else {
    editingTransaction.value = null
    form.value = {
      type: 'expense', account: '', category: '', destination_account: '',
      amount: '', description: '', date: new Date().toISOString().split('T')[0],
      notes: '', is_recurring: false, recurrence_frequency: '', recurrence_interval: 1, recurrence_end_date: '',
      refund_budget: null,
    }
  }
  showModal.value = true
}

const closeModal = () => { showModal.value = false; editingTransaction.value = null; formErrors.value = null; editingAsSeries.value = false }

const handleSubmit = async () => {
  loading.value = true; formErrors.value = null
  const data: any = {
    type: form.value.type, account: parseInt(form.value.account),
    amount: form.value.amount, description: form.value.description, date: form.value.date,
    is_recurring: form.value.is_recurring
  }
  if (form.value.type !== 'transfer' && form.value.category) data.category = parseInt(form.value.category)
  if (form.value.type === 'transfer' && form.value.destination_account) data.destination_account = parseInt(form.value.destination_account)
  if (form.value.notes) data.notes = form.value.notes
  data.refund_budget = form.value.type === 'income' ? (form.value.refund_budget ?? null) : null
  if (form.value.is_recurring) {
    data.recurrence_frequency = form.value.recurrence_frequency
    data.recurrence_interval = form.value.recurrence_interval
    if (form.value.recurrence_end_date) data.recurrence_end_date = form.value.recurrence_end_date
  }

  let result
  if (editingTransaction.value && editingAsSeries.value) {
    result = await updateSeries(editingTransaction.value.id, {
      amount: data.amount?.toString(), description: data.description,
      category: data.category ?? null, notes: data.notes ?? null,
      recurrence_end_date: data.recurrence_end_date ?? null, account: data.account,
    }, editingTransaction.value.date)
  } else if (editingTransaction.value) {
    result = await updateTransaction(editingTransaction.value.id, data)
  } else {
    result = await createTransaction(data)
  }
  loading.value = false
  if (result.success) {
    toast.add({ title: 'Succès', description: editingTransaction.value ? 'Transaction mise à jour' : 'Transaction créée', color: 'green' })
    closeModal(); await fetchTransactions();   } else if (result.error) {
    formErrors.value = result.error
    toast.add({ title: 'Erreur', description: formatForToast(result.error), color: 'red' })
  }
}

// ── Recurring ─────────────────────────────────────────────────
const showRecurringChoice = ref(false)
const pendingEditTransaction = ref<Transaction | null>(null)
const handleEditClick = (transaction: Transaction) => {
  if (transaction.recurring_series_id && !transaction.is_series_template) {
    pendingEditTransaction.value = transaction; showRecurringChoice.value = true
  } else { openModal(transaction) }
}
const onEditSingleOccurrence = () => { if (pendingEditTransaction.value) { openModal(pendingEditTransaction.value); pendingEditTransaction.value = null } }
const onEditSeries = () => { if (pendingEditTransaction.value) { editingAsSeries.value = true; openModal(pendingEditTransaction.value); pendingEditTransaction.value = null } }

// ── Delete ────────────────────────────────────────────────────
const showConfirmDelete = ref(false)
const transactionToDelete = ref<Transaction | null>(null)
const handleDelete = (transaction: Transaction) => { transactionToDelete.value = transaction; showConfirmDelete.value = true }
const executeDelete = async () => {
  if (!transactionToDelete.value) return
  loading.value = true
  const result = await deleteTransaction(transactionToDelete.value.id)
  loading.value = false; transactionToDelete.value = null
  if (result.success) {
    toast.add({ title: 'Succès', description: 'Transaction supprimée', color: 'green' })
    clearSelected(); await fetchTransactions();   } else {
    toast.add({ title: 'Erreur', description: 'Impossible de supprimer', color: 'red' })
  }
}

// ── Fetch ─────────────────────────────────────────────────────
const fetchTransactions = async () => {
  loading.value = true; loadError.value = false
  const d = currentMonthDate.value
  const year = d.getFullYear()
  const month = d.getMonth() + 1
  const startDay = budgetStartDay.value
  const { startDate, endDate } = getBudgetPeriodDates(year, month, startDay)
  const result = await getTransactions({
    ordering: '-date,-created_at',
    start_date: startDate,
    end_date: endDate,
    page_size: 500
  })
  if (result.success && result.data) transactions.value = result.data.results
  else loadError.value = true
  loading.value = false
}
const fetchAccounts = async () => { const r = await getAccounts(); if (r.success && r.data) accounts.value = r.data.results }
const fetchCategories = async () => { const r = await getCategories(); if (r.success && r.data) categories.value = r.data.results }
const fetchBudgets = async () => {
  const r = await getBudgets({ is_active: true })
  if (r.data?.results) spendingBudgets.value = r.data.results.filter(b => !b.is_savings_goal).map(b => ({ id: b.id, name: b.name }))
}
const onMonthChange = ({ year, month }: { year: number; month: number }) => {
  currentMonthDate.value = new Date(year, month - 1, 1)
}

watch(currentMonthDate, () => fetchTransactions())

onMounted(async () => {
  await ensureProfileLoaded()
  // Initialise la navigation au mois budgétaire courant (selon budget_start_day)
  const { year, month } = getCurrentBudgetMonth(budgetStartDay.value)
  currentMonthDate.value = new Date(year, month - 1, 1)
  generateRecurring()
  fetchTransactions(); fetchAccounts(); fetchCategories(); fetchBudgets()
  document.addEventListener('click', (e) => {
    if (!(e.target as Element)?.closest('.tx-dropdown')) closeDropdowns()
  })
})
</script>

<template>
  <div class="tx-root fade-up">

    <!-- ── Page TopBar ─────────────────────────────────────────── -->
    <header class="tx-topbar">
      <PageHeader
        title="Transactions"
        subtitle="Tous vos mouvements financiers, catégorisés par enveloppe."
      >
        <template #actions>
          <MonthNavigation
            :model-value="{ year: currentMonthDate.getFullYear(), month: currentMonthDate.getMonth() + 1 }"
            @update:model-value="onMonthChange"
          />
          <button class="ds-btn ds-btn-primary" style="height:36px;font-size:13px;" @click="openModal()">
            <UIcon name="i-heroicons-plus" style="width:14px;height:14px;" />
            <span class="hidden sm:inline">Nouvelle transaction</span>
          </button>
        </template>
      </PageHeader>
    </header>

    <!-- ── Content ─────────────────────────────────────────────── -->
    <div class="tx-content">

      <!-- Filter bar -->
      <div class="tx-filter-bar">
        <!-- Search -->
        <div class="tx-search" :class="{ focused: false }">
          <UIcon name="i-heroicons-magnifying-glass" style="width:15px;height:15px;color:var(--ink-4);flex-shrink:0;" />
          <input
            v-model="filters.search"
            placeholder="Rechercher un libellé, une enveloppe…"
            class="tx-search-input"
          />
          <button v-if="filters.search" class="tx-clear-btn" @click="filters.search = ''">
            <UIcon name="i-heroicons-x-mark" style="width:13px;height:13px;" />
          </button>
        </div>

        <!-- Type dropdown -->
        <div class="tx-dropdown">
          <button class="tx-filter-btn" @click.stop="toggleDropdown('type')">
            <UIcon name="i-heroicons-arrows-right-left" style="width:14px;height:14px;color:var(--ink-3);" />
            <span><span style="color:var(--ink-3);">Type : </span><span style="color:var(--ink);font-weight:500;">{{ { all:'Tous', income:'Revenus', expense:'Dépenses', transfer:'Transferts' }[filters.type] }}</span></span>
            <UIcon name="i-heroicons-chevron-down" style="width:12px;height:12px;color:var(--ink-3);" />
          </button>
          <div v-if="openDropdown === 'type'" class="tx-dropdown-menu">
            <button v-for="opt in [{ id:'all', label:'Tous' }, { id:'income', label:'Revenus' }, { id:'expense', label:'Dépenses' }, { id:'transfer', label:'Transferts' }]" :key="opt.id"
              class="tx-dropdown-item" :class="{ active: filters.type === opt.id }"
              @click.stop="filters.type = opt.id; closeDropdowns()">
              <span>{{ opt.label }}</span>
              <UIcon v-if="filters.type === opt.id" name="i-heroicons-check" style="width:12px;height:12px;" />
            </button>
          </div>
        </div>

        <!-- Compte dropdown -->
        <div class="tx-dropdown">
          <button class="tx-filter-btn" @click.stop="toggleDropdown('account')">
            <UIcon name="i-heroicons-building-library" style="width:14px;height:14px;color:var(--ink-3);" />
            <span>
              <span style="color:var(--ink-3);">Compte : </span>
              <span style="color:var(--ink);font-weight:500;">{{ filters.account === 'all' ? 'Tous' : (accounts.find(a => a.id.toString() === filters.account)?.name || 'Tous') }}</span>
            </span>
            <UIcon name="i-heroicons-chevron-down" style="width:12px;height:12px;color:var(--ink-3);" />
          </button>
          <div v-if="openDropdown === 'account'" class="tx-dropdown-menu">
            <button class="tx-dropdown-item" :class="{ active: filters.account === 'all' }" @click.stop="filters.account = 'all'; closeDropdowns()">
              <span>Tous</span>
              <UIcon v-if="filters.account === 'all'" name="i-heroicons-check" style="width:12px;height:12px;" />
            </button>
            <button v-for="a in accounts" :key="a.id"
              class="tx-dropdown-item" :class="{ active: filters.account === a.id.toString() }"
              @click.stop="filters.account = a.id.toString(); closeDropdowns()">
              <span>{{ a.name }}</span>
              <UIcon v-if="filters.account === a.id.toString()" name="i-heroicons-check" style="width:12px;height:12px;" />
            </button>
          </div>
        </div>

        <!-- Catégorie dropdown -->
        <div class="tx-dropdown">
          <button class="tx-filter-btn" @click.stop="toggleDropdown('category')">
            <UIcon name="i-heroicons-tag" style="width:14px;height:14px;color:var(--ink-3);" />
            <span>
              <span style="color:var(--ink-3);">Catégorie : </span>
              <span style="color:var(--ink);font-weight:500;">{{ filters.category === 'all' ? 'Toutes' : (categories.find(c => c.id.toString() === filters.category)?.name || 'Toutes') }}</span>
            </span>
            <UIcon name="i-heroicons-chevron-down" style="width:12px;height:12px;color:var(--ink-3);" />
          </button>
          <div v-if="openDropdown === 'category'" class="tx-dropdown-menu">
            <button class="tx-dropdown-item" :class="{ active: filters.category === 'all' }" @click.stop="filters.category = 'all'; closeDropdowns()">
              <span>Toutes</span>
              <UIcon v-if="filters.category === 'all'" name="i-heroicons-check" style="width:12px;height:12px;" />
            </button>
            <button v-for="c in categories" :key="c.id"
              class="tx-dropdown-item" :class="{ active: filters.category === c.id.toString() }"
              @click.stop="filters.category = c.id.toString(); closeDropdowns()">
              <span>{{ c.name }}</span>
              <UIcon v-if="filters.category === c.id.toString()" name="i-heroicons-check" style="width:12px;height:12px;" />
            </button>
          </div>
        </div>

        <div style="flex:1;" />

        <span class="mono" style="font-size:12.5px;color:var(--ink-3);white-space:nowrap;">
          {{ filteredTransactions.length }} résultat{{ filteredTransactions.length > 1 ? 's' : '' }}
        </span>
        <button v-if="isFiltered" class="ds-btn ds-btn-secondary" style="height:32px;padding:0 10px;font-size:12px;" @click="resetFilters">
          <UIcon name="i-heroicons-arrow-path" style="width:12px;height:12px;" />
          Réinitialiser
        </button>
      </div>

      <!-- Summary cards -->
      <div class="tx-summary-grid">
        <div v-for="card in [
          { label: 'Revenus',   value: monthTotals.totalIncome,  color: '#16a34a',        sign: '+', icon: 'i-heroicons-arrow-trending-up' },
          { label: 'Dépenses',  value: monthTotals.totalExpense, color: 'var(--ink)',      sign: '−', icon: 'i-heroicons-arrow-trending-down' },
          { label: 'Solde net', value: monthTotals.net,          color: monthTotals.net >= 0 ? '#16a34a' : 'var(--danger)', sign: monthTotals.net >= 0 ? '+' : '−', icon: 'i-heroicons-banknotes' },
        ]" :key="card.label" class="tx-summary-card">
          <div class="tx-summary-top">
            <span class="tx-summary-label">{{ card.label }}</span>
            <div class="tx-summary-icon" :style="{ color: card.color }">
              <UIcon :name="card.icon" style="width:14px;height:14px;" />
            </div>
          </div>
          <div class="mono tx-summary-amount" :style="{ color: card.color }">
            {{ card.sign }}{{ formatCurrency(Math.abs(card.value)) }}
          </div>
          <div class="tx-summary-sub">{{ filteredTransactions.length }} transaction{{ filteredTransactions.length > 1 ? 's' : '' }} dans la sélection</div>
        </div>
      </div>

      <!-- Table card -->
      <div class="tx-table-card">

        <!-- Loading -->
        <div v-if="loading" style="padding:20px 14px;">
          <div v-for="i in 6" :key="i" class="tx-skeleton" style="height:50px;margin-bottom:8px;" />
        </div>

        <!-- Error -->
        <div v-else-if="loadError" style="padding:48px 24px;">
          <EmptyState icon="i-heroicons-exclamation-circle" color="red"
            title="Impossible de charger les transactions"
            description="Vérifiez votre connexion et réessayez."
            button-text="Réessayer" button-icon="i-heroicons-arrow-path"
            @action="fetchTransactions()" />
        </div>

        <!-- Empty -->
        <div v-else-if="filteredTransactions.length === 0" style="padding:60px 24px;text-align:center;">
          <div style="width:56px;height:56px;border-radius:14px;background:var(--accent-soft);color:var(--accent);display:grid;place-items:center;margin:0 auto 16px;">
            <UIcon name="i-heroicons-arrows-right-left" style="width:26px;height:26px;" />
          </div>
          <h3 style="margin:0 0 4px;font-size:16px;font-weight:600;color:var(--ink);">Aucune transaction</h3>
          <p style="margin:0 0 16px;font-size:13px;color:var(--ink-3);">Aucun mouvement ne correspond aux filtres actuels.</p>
          <button class="ds-btn ds-btn-primary" style="height:38px;padding:0 16px;font-size:13px;" @click="openModal()">
            <UIcon name="i-heroicons-plus" style="width:14px;height:14px;" />
            Ajouter une transaction
          </button>
        </div>

        <!-- Grouped list -->
        <div v-else>
          <template v-for="[date, txns] in groupedByDay" :key="date">

            <!-- Day header -->
            <div class="tx-day-header">
              <!-- Checkbox -->
              <label class="tx-checkbox" @click.stop="toggleDaySelect(txns)">
                <span class="tx-checkbox-box" :class="{ checked: isDayAllSelected(txns), indeterminate: isDaySomeSelected(txns) && !isDayAllSelected(txns) }">
                  <svg v-if="isDayAllSelected(txns)" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
                  <span v-else-if="isDaySomeSelected(txns)" style="width:8px;height:2px;background:white;border-radius:1px;display:block;" />
                </span>
              </label>
              <div style="flex:1;display:flex;align-items:baseline;gap:10px;">
                <span class="tx-day-label">{{ dayLabel(date) }}</span>
                <span class="mono" style="font-size:11px;color:var(--ink-3);">{{ txns.length }} transaction{{ txns.length > 1 ? 's' : '' }}</span>
              </div>
              <span class="mono" style="font-size:12.5px;font-weight:500;" :style="{ color: dayNet(txns) >= 0 ? '#16a34a' : 'var(--ink-2)' }">
                {{ dayNet(txns) >= 0 ? '+' : '−' }}{{ formatCurrency(Math.abs(dayNet(txns))) }}
              </span>
            </div>

            <!-- Transaction rows -->
            <div
              v-for="txn in txns"
              :key="txn.id"
              class="tx-row"
              :class="{ selected: isSelected(txn.id), future: txn.date > today }"
              @click="toggleSelect(txn.id)"
            >
              <!-- Checkbox -->
              <label class="tx-checkbox" @click.stop="toggleSelect(txn.id)">
                <span class="tx-checkbox-box" :class="{ checked: isSelected(txn.id) }">
                  <svg v-if="isSelected(txn.id)" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
                </span>
              </label>

              <!-- Icon -->
              <div class="tx-row-icon" :style="{ color: typeIconColor(txn.type) }">
                <UIcon :name="typeIcon(txn.type)" style="width:15px;height:15px;" />
              </div>

              <!-- Description + meta + chip -->
              <div class="tx-row-body">
                <div class="tx-row-left">
                  <div class="tx-row-desc">{{ txn.description || '—' }}</div>
                  <div class="mono tx-row-meta">
                    {{ txn.date || '' }} · {{ txn.account_name }}
                    <template v-if="txn.type === 'transfer' && txn.destination_account_name">
                      → {{ txn.destination_account_name }}
                    </template>
                  </div>
                </div>

                <!-- Category chip -->
                <div v-if="txn.category_name || txn.type === 'transfer'" class="tx-chip"
                  :style="{
                    background: categoryChipColor(txn.type).bg,
                    border: `1px solid ${categoryChipColor(txn.type).border}`,
                    color: categoryChipColor(txn.type).color,
                  }">
                  <span class="tx-chip-dot" :style="{ background: categoryChipColor(txn.type).color }" />
                  {{ txn.type === 'transfer' ? 'Transfert' : txn.category_name }}
                </div>
              </div>

              <!-- Amount -->
              <div class="mono tx-row-amount" :style="{ color: txn.type === 'income' ? '#16a34a' : 'var(--ink)' }">
                {{ txn.type === 'income' ? '+' : txn.type === 'expense' ? '−' : '' }}{{ formatCurrency(parseFloat(txn.amount)) }}
              </div>

              <!-- Future indicator -->
              <UIcon v-if="txn.date > today" name="i-heroicons-clock" style="width:13px;height:13px;color:#f59e0b;flex-shrink:0;" />

              <!-- More button → UDropdown -->
              <div class="tx-more-wrap" @click.stop>
                <UDropdown :items="[[
                  { label: 'Modifier', icon: 'i-heroicons-pencil-square', click: () => handleEditClick(txn) },
                  { label: 'Supprimer', icon: 'i-heroicons-trash', click: () => handleDelete(txn) },
                ]]" :popper="{ placement: 'bottom-end' }">
                  <button class="tx-more-btn">
                    <UIcon name="i-heroicons-ellipsis-horizontal" style="width:14px;height:14px;" />
                  </button>
                </UDropdown>
              </div>
            </div>

          </template>

          <!-- Pagination info -->
          <div class="tx-pagination">
            <span>Affichage de <b style="color:var(--ink-2);">1 à {{ filteredTransactions.length }}</b> sur <b style="color:var(--ink-2);">{{ filteredTransactions.length }}</b> transactions</span>
          </div>
        </div>

      </div>
    </div>

    <!-- ── Bulk action bar ─────────────────────────────────────── -->
    <Transition name="bulk">
      <div v-if="selectedIds.size > 0" class="tx-bulk-bar">
        <span style="font-size:13px;font-weight:500;">
          {{ selectedIds.size }} transaction{{ selectedIds.size > 1 ? 's' : '' }} sélectionnée{{ selectedIds.size > 1 ? 's' : '' }}
        </span>
        <span class="tx-bulk-sep" />
        <button class="tx-bulk-btn tx-bulk-btn--danger" @click="bulkDelete">
          <UIcon name="i-heroicons-trash" style="width:14px;height:14px;" />
          Supprimer
        </button>
        <button class="tx-bulk-close" @click="clearSelected">
          <UIcon name="i-heroicons-x-mark" style="width:12px;height:12px;" />
        </button>
      </div>
    </Transition>

    <!-- ── Modals ──────────────────────────────────────────────── -->
    <RecurringEditChoiceModal v-model="showRecurringChoice" @edit-single="onEditSingleOccurrence" @edit-series="onEditSeries" />

    <ConfirmModal v-model="showConfirmDelete" title="Supprimer la transaction"
      :message="`Supprimer « ${transactionToDelete?.description || 'Sans description'} » (${transactionToDelete?.amount}) ?`"
      confirm-label="Supprimer" @confirm="executeDelete" />

    <UModal v-model="showModal" :ui="{ width: 'sm:max-w-2xl' }">
      <UCard>
        <template #header>
          <h3 style="font-size:15px;font-weight:600;color:var(--ink);margin:0;">
            {{ editingTransaction ? 'Modifier la transaction' : 'Nouvelle transaction' }}
          </h3>
        </template>
        <form class="space-y-4" @submit.prevent="handleSubmit">
          <UFormGroup label="Type" required>
            <USelectMenu v-model="form.type" :options="[{ label:'Revenu', value:'income' }, { label:'Dépense', value:'expense' }, { label:'Transfert', value:'transfer' }]" option-attribute="label" value-attribute="value" />
          </UFormGroup>
          <UFormGroup label="Compte" required>
            <USelectMenu v-model="form.account" :options="accounts" option-attribute="name" value-attribute="id" placeholder="Sélectionner un compte" />
            <FormFieldError :error="getErrorForField(formErrors, 'account')" />
          </UFormGroup>
          <UFormGroup v-if="form.type !== 'transfer'" label="Catégorie" required>
            <USelectMenu v-model="form.category" :options="availableCategories" option-attribute="name" value-attribute="id" placeholder="Sélectionner une catégorie" />
            <FormFieldError :error="getErrorForField(formErrors, 'category')" />
          </UFormGroup>
          <UFormGroup v-if="form.type === 'transfer'" label="Compte destination" required>
            <USelectMenu v-model="form.destination_account" :options="accounts.filter(a => a.id.toString() !== form.account)" option-attribute="name" value-attribute="id" placeholder="Sélectionner un compte" />
            <FormFieldError :error="getErrorForField(formErrors, 'destination_account')" />
          </UFormGroup>
          <UFormGroup v-if="form.type === 'income'" label="Rembourse une enveloppe" hint="Optionnel">
            <USelectMenu
              v-model="form.refund_budget"
              :options="[{ id: null, name: '— Aucune —' }, ...spendingBudgets]"
              option-attribute="name"
              value-attribute="id"
              placeholder="— Aucune —"
            />
          </UFormGroup>
          <UFormGroup label="Montant" required>
            <UInput v-model="form.amount" type="number" step="0.01" placeholder="0.00" required />
            <FormFieldError :error="getErrorForField(formErrors, 'amount')" />
          </UFormGroup>
          <UFormGroup label="Description">
            <UInput v-model="form.description" placeholder="Description de la transaction" />
            <FormFieldError :error="getErrorForField(formErrors, 'description')" />
          </UFormGroup>
          <UFormGroup label="Date" required>
            <UInput v-model="form.date" type="date" required />
            <FormFieldError :error="getErrorForField(formErrors, 'date')" />
          </UFormGroup>
          <UFormGroup label="Notes">
            <UTextarea v-model="form.notes" placeholder="Notes additionnelles…" />
          </UFormGroup>
          <UFormGroup>
            <UCheckbox v-model="form.is_recurring" label="Transaction récurrente" />
          </UFormGroup>
          <template v-if="form.is_recurring">
            <div class="grid grid-cols-2 gap-4">
              <UFormGroup label="Fréquence">
                <USelectMenu v-model="form.recurrence_frequency" :options="[{ label:'Quotidien', value:'daily' }, { label:'Hebdomadaire', value:'weekly' }, { label:'Mensuel', value:'monthly' }, { label:'Annuel', value:'yearly' }]" option-attribute="label" value-attribute="value" />
              </UFormGroup>
              <UFormGroup label="Intervalle">
                <UInput v-model.number="form.recurrence_interval" type="number" min="1" />
              </UFormGroup>
            </div>
            <UFormGroup label="Date de fin (optionnelle)">
              <UInput v-model="form.recurrence_end_date" type="date" />
            </UFormGroup>
          </template>
          <div class="flex justify-end gap-2 pt-2">
            <UButton color="gray" variant="ghost" @click="closeModal">Annuler</UButton>
            <UButton type="submit" :loading="loading">{{ editingTransaction ? 'Mettre à jour' : 'Créer' }}</UButton>
          </div>
        </form>
      </UCard>
    </UModal>

  </div>
</template>

<style scoped>
/* ── Root ───────────────────────────────────────────────────── */
.tx-root {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

/* ── TopBar ─────────────────────────────────────────────────── */
.tx-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px 8px;
  background: var(--bg);
  gap: 16px;
  flex-wrap: wrap;
}
@media (max-width: 640px) { .tx-topbar { padding: 16px 16px 8px; } }
/* ── Content ─────────────────────────────────────────────────── */
.tx-content {
  padding: 20px 32px 60px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
@media (max-width: 640px) { .tx-content { padding: 16px 16px 80px; gap: 14px; } }

/* ── Filter bar ─────────────────────────────────────────────── */
.tx-filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 14px 18px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}
.tx-search {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  padding: 0 12px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  flex: 1;
  min-width: 220px;
  transition: border-color 0.15s;
}
.tx-search:focus-within { border-color: var(--accent); }
.tx-search-input {
  flex: 1;
  font-size: 13px;
  color: var(--ink);
  background: transparent;
  border: none;
  outline: none;
  min-width: 0;
  font-family: inherit;
}
.tx-search-input::placeholder { color: var(--ink-4); }
.tx-clear-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--ink-4);
  display: grid;
  place-items: center;
  padding: 0;
  flex-shrink: 0;
}

/* Dropdown */
.tx-dropdown { position: relative; }
.tx-filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  padding: 0 10px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 13px;
  color: var(--ink-2);
  cursor: pointer;
  transition: background 0.12s;
  white-space: nowrap;
  font-family: inherit;
}
.tx-filter-btn:hover { background: var(--surface-2); }
.tx-dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 200px;
  padding: 4px;
  z-index: 50;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  box-shadow: var(--shadow-lg);
  max-height: 320px;
  overflow-y: auto;
}
.tx-dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--ink-2);
  text-align: left;
  font-family: inherit;
  transition: background 0.1s;
}
.tx-dropdown-item:hover { background: var(--surface-2); }
.tx-dropdown-item.active { background: var(--accent-soft); color: var(--accent); font-weight: 500; }

/* ── Summary cards ──────────────────────────────────────────── */
.tx-summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}
@media (max-width: 640px) { .tx-summary-grid { grid-template-columns: 1fr; gap: 8px; } }
.tx-summary-card {
  padding: 18px 20px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}
.tx-summary-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.tx-summary-label {
  font-size: 11px;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  font-weight: 500;
}
.tx-summary-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--surface-2);
  display: grid;
  place-items: center;
}
.tx-summary-amount {
  font-size: 26px;
  font-weight: 500;
  letter-spacing: -0.8px;
  line-height: 1;
}
.tx-summary-sub {
  font-size: 11.5px;
  color: var(--ink-3);
  margin-top: 6px;
}

/* ── Table card ─────────────────────────────────────────────── */
.tx-table-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* ── Checkbox ───────────────────────────────────────────────── */
.tx-checkbox {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}
.tx-checkbox-box {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 1.5px solid var(--line-strong);
  background: var(--surface);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.12s;
  flex-shrink: 0;
}
.tx-checkbox-box.checked,
.tx-checkbox-box.indeterminate {
  border-color: var(--accent);
  background: var(--accent);
}

/* ── Day header ─────────────────────────────────────────────── */
.tx-day-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--surface-2);
  border-top: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 1;
}
.tx-day-header:first-child { border-top: none; }
.tx-day-label {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.1px;
  text-transform: capitalize;
}

/* ── Transaction row ────────────────────────────────────────── */
.tx-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 14px;
  border-top: 1px solid var(--line);
  cursor: pointer;
  transition: background 0.1s;
}
.tx-row:hover { background: var(--surface-2); }
.tx-row.selected { background: var(--accent-soft); }
.tx-row.future { opacity: 0.65; }

.tx-row-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.tx-row:hover .tx-row-icon { background: var(--surface); }
.tx-row.selected .tx-row-icon { background: var(--surface); }

.tx-row-body {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}
.tx-row-left {
  flex: 1 1 0;
  min-width: 0;
}
.tx-row-desc {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tx-row-meta {
  font-size: 11.5px;
  color: var(--ink-3);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Category chip */
.tx-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 9px;
  height: 22px;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 500;
  flex-shrink: 0;
  white-space: nowrap;
}
@media (max-width: 768px) { .tx-chip { display: none; } }
.tx-chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 1.5px;
  flex-shrink: 0;
}

/* Amount */
.tx-row-amount {
  font-size: 14px;
  font-weight: 500;
  width: 110px;
  text-align: right;
  flex-shrink: 0;
}
@media (max-width: 480px) { .tx-row-amount { width: 80px; font-size: 13px; } }

/* More button */
.tx-more-wrap {
  flex-shrink: 0;
  opacity: 0.6;
  transition: opacity 0.15s;
}
.tx-row:hover .tx-more-wrap { opacity: 1; }
@media (max-width: 768px) { .tx-more-wrap { opacity: 1; } }
.tx-more-btn {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  color: var(--ink-3);
  display: grid;
  place-items: center;
  transition: all 0.12s;
}
.tx-more-btn:hover {
  background: var(--surface);
  border-color: var(--line);
  color: var(--ink-2);
}

/* Pagination */
.tx-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-top: 1px solid var(--line);
  font-size: 12.5px;
  color: var(--ink-3);
}

/* ── Bulk bar ───────────────────────────────────────────────── */
.tx-bulk-bar {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 8px 8px 14px;
  background: var(--ink);
  color: var(--bg);
  border-radius: 12px;
  box-shadow: 0 16px 40px -12px rgba(0,0,0,0.4);
  z-index: 50;
  white-space: nowrap;
}
.tx-bulk-sep {
  width: 1px;
  height: 18px;
  background: rgba(255,255,255,0.15);
  margin: 0 4px;
  flex-shrink: 0;
}
.tx-bulk-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 10px;
  height: 28px;
  background: transparent;
  color: var(--bg);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12.5px;
  font-weight: 500;
  font-family: inherit;
  transition: background 0.12s;
}
.tx-bulk-btn:hover { background: rgba(255,255,255,0.1); }
.tx-bulk-btn--danger { color: #fca5a5; }
.tx-bulk-close {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: rgba(255,255,255,0.1);
  border: none;
  cursor: pointer;
  color: var(--bg);
  display: grid;
  place-items: center;
  margin-left: 4px;
  transition: background 0.12s;
}
.tx-bulk-close:hover { background: rgba(255,255,255,0.18); }

/* Bulk bar transition */
.bulk-enter-active, .bulk-leave-active { transition: all 0.25s cubic-bezier(.2,.7,.2,1); }
.bulk-enter-from, .bulk-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }

/* ── Skeleton ───────────────────────────────────────────────── */
.tx-skeleton {
  background: var(--surface-2);
  border-radius: 8px;
  animation: txPulse 1.5s ease infinite;
}
@keyframes txPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}
</style>
