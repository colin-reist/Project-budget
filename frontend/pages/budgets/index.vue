<script setup lang="ts">
import type { Budget, Category } from '~/types'
import type { StandardError } from '~/types/errors'

definePageMeta({
  middleware: 'auth'
})

const { getBudgets, createBudget, updateBudget, deleteBudget, getBudgetsSummary, toggleBudgetActive } = useBudgets()
const { getCategories } = useCategories()
const { getProfile, updateProfile, ensureProfileLoaded } = useUserProfile()
const { getTransactions } = useTransactions()
const { getAccounts } = useAccounts()
const { getErrorForField, formatForToast } = useErrorHandler()
const toast = useToast()

// Navigation par mois
const selectedMonthDate = ref(new Date())
const selectedYear = computed(() => selectedMonthDate.value.getFullYear())
const selectedMonth = computed(() => selectedMonthDate.value.getMonth() + 1)
const selectedMonthLabel = computed(() =>
  selectedMonthDate.value.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
)
const isCurrentMonth = computed(() => {
  const now = new Date()
  return selectedMonthDate.value.getMonth() === now.getMonth() &&
    selectedMonthDate.value.getFullYear() === now.getFullYear()
})

const goToPrevMonth = async () => {
  const d = new Date(selectedMonthDate.value)
  d.setMonth(d.getMonth() - 1)
  selectedMonthDate.value = d
  await Promise.all([fetchBudgets(), fetchSummary()])
}

const goToNextMonth = async () => {
  if (isCurrentMonth.value) return
  const d = new Date(selectedMonthDate.value)
  d.setMonth(d.getMonth() + 1)
  selectedMonthDate.value = d
  await Promise.all([fetchBudgets(), fetchSummary()])
}

const onMonthChange = async ({ year, month }: { year: number; month: number }) => {
  selectedMonthDate.value = new Date(year, month - 1, 1)
  await Promise.all([fetchBudgets(), fetchSummary()])
}

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
const incomeForm = ref({ monthly_income: '' })
const formErrors = ref<StandardError | null>(null)
const incomeFormErrors = ref<StandardError | null>(null)

// Envelope view state
const selectedEnvelopeId = ref<number | null>(null)
const openGroups = ref<Record<string, boolean>>({})
const editingCellId = ref<number | null>(null)
const editDraft = ref('')

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
  is_savings_goal: false,
  is_mandatory_savings: false
})

// Computed for design mapping
const regularBudgets = computed(() => budgets.value.filter(b => !b.is_savings_goal))
const savingsGoals = computed(() => budgets.value.filter(b => b.is_savings_goal))

const monthlyIncome = computed(() => parseFloat(userProfile.value?.monthly_income ?? 0))
const totalBudgetAssigned = computed(() => parseFloat(String(summary.value.total_amount ?? 0)))
const totalBudgetSpent = computed(() => parseFloat(String(summary.value.total_spent ?? 0)))
const toAssign = computed(() => monthlyIncome.value - totalBudgetAssigned.value)
const progressRatio = computed(() =>
  totalBudgetAssigned.value === 0 ? 0 : Math.min(100, (totalBudgetSpent.value / totalBudgetAssigned.value) * 100)
)

const envelopeGroups = computed(() => {
  const groups: any[] = []
  const regular = regularBudgets.value
  if (regular.length > 0) {
    groups.push({
      id: 'budgets',
      name: 'Dépenses',
      color: 'var(--accent)',
      envelopes: regular.map(b => ({
        id: b.id,
        name: b.name,
        assigned: parseFloat(String(b.amount)),
        spent: (b as any).spent_amount ?? 0,
        available: (b as any).remaining_amount ?? 0,
        pct: Math.min(100, (b as any).percentage_used ?? 0),
        isOver: (b as any).is_over_budget,
        budgetObj: b,
      }))
    })
  }
  const savings = savingsGoals.value
  if (savings.length > 0) {
    groups.push({
      id: 'epargne',
      name: 'Épargne',
      color: '#16a34a',
      envelopes: savings.map(b => ({
        id: b.id,
        name: b.name,
        assigned: parseFloat(String(b.amount)),
        spent: (b as any).spent_amount ?? 0,
        available: (b as any).remaining_amount ?? 0,
        pct: Math.min(100, (b as any).percentage_used ?? 0),
        isOver: false,
        isSavings: true,
        budgetObj: b,
      }))
    })
  }
  return groups
})

watch(envelopeGroups, (groups) => {
  groups.forEach(g => {
    if (!(g.id in openGroups.value)) openGroups.value[g.id] = true
  })
}, { immediate: true })

const selectedEnvelope = computed(() => {
  if (!selectedEnvelopeId.value) return null
  for (const group of envelopeGroups.value) {
    const env = group.envelopes.find((e: any) => e.id === selectedEnvelopeId.value)
    if (env) return { env, group }
  }
  return null
})

const groupTotal = (envelopes: any[], key: string) =>
  envelopes.reduce((s: number, e: any) => s + (e[key] ?? 0), 0)

// Inline editing
const startEdit = (env: any) => {
  editingCellId.value = env.id
  editDraft.value = env.assigned.toFixed(2)
  nextTick(() => {
    const input = document.getElementById(`cell-${env.id}`)
    if (input) { (input as HTMLInputElement).focus(); (input as HTMLInputElement).select() }
  })
}

const commitEdit = async (env: any) => {
  if (editingCellId.value !== env.id) return
  editingCellId.value = null
  const newAmount = parseFloat(editDraft.value.replace(/'/g, '').replace(',', '.'))
  if (!isNaN(newAmount) && newAmount >= 0 && newAmount !== env.assigned) {
    await updateBudget(env.budgetObj.id, { amount: newAmount.toFixed(2) })
    await Promise.all([fetchBudgets(), fetchSummary(), fetchProfile()])
  }
}

const cancelEdit = () => { editingCellId.value = null }

// Methods
const fetchBudgets = async () => {
  loading.value = true
  const result = await getBudgets({ year: selectedYear.value, month: selectedMonth.value })
  if (result.success && result.data) budgets.value = result.data.results
  loading.value = false
}

const fetchCategories = async () => {
  const result = await getCategories({ type: 'expense' })
  if (result.success && result.data) categories.value = result.data.results
}

const fetchSummary = async () => {
  const result = await getBudgetsSummary({ year: selectedYear.value, month: selectedMonth.value })
  if (result.success && result.data) summary.value = result.data
}

const fetchProfile = async () => {
  const result = await getProfile()
  if (result.success && result.data) userProfile.value = result.data
}

const openModal = (budget?: Budget) => {
  formErrors.value = null
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
      is_savings_goal: budget.is_savings_goal || false,
      is_mandatory_savings: budget.is_mandatory_savings || false
    }
  } else {
    editingBudget.value = null
    form.value = {
      name: '', category: '', amount: '', period: 'monthly',
      start_date: new Date().toISOString().split('T')[0],
      end_date: '', alert_threshold: 80, is_active: true,
      is_savings_goal: false, is_mandatory_savings: false
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingBudget.value = null
  formErrors.value = null
}

const handleSubmit = async () => {
  loading.value = true
  formErrors.value = null
  const budgetData: any = {
    name: form.value.name,
    amount: form.value.amount,
    period: form.value.period,
    start_date: form.value.start_date,
    alert_threshold: form.value.alert_threshold,
    is_active: form.value.is_active,
    is_savings_goal: form.value.is_savings_goal,
    is_mandatory_savings: form.value.is_mandatory_savings
  }
  if (!form.value.is_savings_goal && !form.value.is_mandatory_savings && form.value.category) {
    budgetData.category = parseInt(form.value.category)
  }
  if (form.value.end_date) budgetData.end_date = form.value.end_date

  const result = editingBudget.value
    ? await updateBudget(editingBudget.value.id, budgetData)
    : await createBudget(budgetData)
  loading.value = false

  if (result.success) {
    toast.add({ title: 'Succès', description: editingBudget.value ? 'Budget mis à jour' : 'Budget créé', color: 'green' })
    closeModal()
    await fetchBudgets(); await fetchSummary(); await fetchProfile()
  } else if (result.error) {
    formErrors.value = result.error
    toast.add({ title: 'Erreur', description: formatForToast(result.error), color: 'red' })
  }
}

const showConfirmDelete = ref(false)
const budgetToDelete = ref<Budget | null>(null)

const handleDelete = (budget: Budget) => {
  budgetToDelete.value = budget
  showConfirmDelete.value = true
  selectedEnvelopeId.value = null
}

const executeDelete = async () => {
  if (!budgetToDelete.value) return
  loading.value = true
  const result = await deleteBudget(budgetToDelete.value.id)
  loading.value = false
  budgetToDelete.value = null
  if (result.success) {
    toast.add({ title: 'Succès', description: 'Budget supprimé', color: 'green' })
    await fetchBudgets(); await fetchSummary()
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de supprimer le budget', color: 'red' })
  }
}

const formatDate = (dateString: string) =>
  new Date(dateString).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })

const formatCurrency = (amount: number | string) => {
  const n = typeof amount === 'string' ? parseFloat(amount) : amount
  return `CHF ${Math.abs(isNaN(n) ? 0 : n).toFixed(2)}`
}

const openIncomeModal = () => {
  incomeFormErrors.value = null
  if (userProfile.value) incomeForm.value.monthly_income = userProfile.value.monthly_income
  showIncomeModal.value = true
}

const closeIncomeModal = () => {
  showIncomeModal.value = false
  incomeFormErrors.value = null
}

const handleIncomeUpdate = async () => {
  loading.value = true
  incomeFormErrors.value = null
  const result = await updateProfile({ monthly_income: incomeForm.value.monthly_income })
  loading.value = false
  if (result.success) {
    toast.add({ title: 'Succès', description: 'Revenu mensuel mis à jour', color: 'green' })
    closeIncomeModal()
    await fetchProfile(); await fetchSummary()
  } else {
    toast.add({ title: 'Erreur', description: 'Impossible de mettre à jour le revenu', color: 'red' })
  }
}

const viewBudgetTransactions = async (budget: Budget) => {
  selectedBudget.value = budget
  loading.value = true
  try {
    const today = new Date()
    const refYear = selectedYear.value
    const refMonth = selectedMonth.value - 1
    let startDate: Date, endDate: Date
    if (budget.period === 'weekly') {
      const refDate = new Date(refYear, refMonth, 1)
      const diff = refDate.getDay() === 0 ? 6 : refDate.getDay() - 1
      startDate = new Date(refDate); startDate.setDate(refDate.getDate() - diff)
      endDate = new Date(startDate); endDate.setDate(startDate.getDate() + 6)
    } else if (budget.period === 'monthly') {
      startDate = new Date(refYear, refMonth, 1)
      endDate = new Date(refYear, refMonth + 1, 0)
    } else {
      startDate = new Date(refYear, 0, 1)
      endDate = new Date(refYear, 11, 31)
    }
    if (budget.start_date && new Date(budget.start_date) > startDate) startDate = new Date(budget.start_date)
    if (budget.end_date && new Date(budget.end_date) < endDate) endDate = new Date(budget.end_date)
    if (endDate > today) endDate = today

    if (budget.is_savings_goal) {
      const accountsResult = await getAccounts({ account_type: 'savings', is_active: true })
      const savingsAccountIds = accountsResult.data?.results.map((a: any) => a.id) || []
      const result = await getTransactions({ type: 'transfer', ordering: '-date' })
      if (result.success && result.data) {
        budgetTransactions.value = result.data.results.filter((t: any) => {
          const d = new Date(t.date)
          return t.destination_account && savingsAccountIds.includes(t.destination_account) && d >= startDate && d <= endDate
        })
      }
    } else {
      const result = await getTransactions({ type: 'expense', category: budget.category, ordering: '-date' })
      if (result.success && result.data) {
        budgetTransactions.value = result.data.results.filter((t: any) => {
          const d = new Date(t.date)
          return d >= startDate && d <= endDate
        })
      }
    }
    showTransactionsModal.value = true
  } catch {
    toast.add({ title: 'Erreur', description: 'Impossible de charger les transactions', color: 'red' })
  } finally {
    loading.value = false
  }
}

const closeTransactionsModal = () => {
  showTransactionsModal.value = false
  selectedBudget.value = null
  budgetTransactions.value = []
}

onMounted(async () => {
  await ensureProfileLoaded()
  fetchBudgets(); fetchCategories(); fetchSummary(); fetchProfile()
})
</script>

<template>
  <div class="env-page">
    <!-- Top bar -->
    <div class="env-topbar">
      <div class="env-topbar-left">
        <PageHeader title="Enveloppes" subtitle="Distribuez vos revenus dans des enveloppes pour chaque catégorie." />
      </div>
      <div class="env-topbar-right">
        <MonthNavigation
          :model-value="{ year: selectedYear, month: selectedMonth }"
          @update:model-value="onMonthChange"
        />
        <button class="btn-sec" @click="openIncomeModal">
          <UIcon name="i-heroicons-banknotes" style="width:14px;height:14px" />
          Revenu
        </button>
        <button class="btn-pri" @click="openModal()">
          <UIcon name="i-heroicons-plus" style="width:14px;height:14px" />
          Nouvelle enveloppe
        </button>
      </div>
    </div>

    <!-- Main content -->
    <div class="env-content">

      <!-- Hero Banner -->
      <div class="hero-banner" :class="{ 'hero-positive': toAssign > 0 }">
        <!-- Left: to-assign -->
        <div class="hero-left">
          <div class="hero-label">
            <UIcon name="i-heroicons-envelope-open" style="width:14px;height:14px;color:var(--ink-4)" />
            Argent à assigner ce mois
          </div>
          <div class="hero-amount mono" :style="{ color: toAssign > 0 ? 'var(--accent)' : 'var(--ink-3)' }">
            CHF {{ toAssign.toFixed(2) }}
          </div>
          <p class="hero-desc">
            <template v-if="toAssign > 0">Chaque franc doit avoir un travail. Distribuez ce solde dans vos enveloppes avant que le mois ne s'écoule.</template>
            <template v-else>Tout est assigné. Vous êtes au point ✓</template>
          </p>
          <div class="hero-actions">
            <button class="btn-pri" style="height:38px;padding:0 16px;font-size:13.5px" @click="openIncomeModal">
              <UIcon name="i-heroicons-pencil" style="width:14px;height:14px" />
              Modifier le revenu
            </button>
            <button class="btn-sec" style="height:38px;padding:0 14px;font-size:13.5px" @click="openModal()">
              <UIcon name="i-heroicons-plus" style="width:14px;height:14px" />
              Nouvelle enveloppe
            </button>
          </div>
        </div>

        <!-- Right: progress + stats -->
        <div class="hero-right">
          <div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px">
              <span class="hero-right-label">Progression du mois</span>
              <span class="mono" style="font-size:12px;color:var(--ink-3)">{{ progressRatio.toFixed(0) }}%</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progressRatio + '%' }" />
            </div>
            <div class="mono" style="font-size:12px;color:var(--ink-3);margin-top:6px">
              CHF {{ totalBudgetSpent.toFixed(2) }} dépensé / CHF {{ totalBudgetAssigned.toFixed(2) }} assigné
            </div>
          </div>
          <div class="hero-stats">
            <div class="hero-stat-card">
              <div class="hero-stat-label">Revenus</div>
              <div class="hero-stat-value mono" style="color:#16a34a">+{{ monthlyIncome.toFixed(2) }}</div>
            </div>
            <div class="hero-stat-card">
              <div class="hero-stat-label">Assigné</div>
              <div class="hero-stat-value mono" style="color:var(--ink)">{{ totalBudgetAssigned.toFixed(2) }}</div>
            </div>
            <div class="hero-stat-card">
              <div class="hero-stat-label">Dépensé</div>
              <div class="hero-stat-value mono" style="color:var(--ink)">−{{ totalBudgetSpent.toFixed(2) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="budgets.length === 0 && !loading" class="empty-state-card">
        <UIcon name="i-heroicons-chart-bar" style="width:40px;height:40px;color:var(--ink-4);margin:0 auto 12px" />
        <div style="font-size:15px;font-weight:600;color:var(--ink);margin-bottom:6px">Maîtrisez vos dépenses avec les enveloppes</div>
        <div style="font-size:13px;color:var(--ink-3);margin-bottom:16px">Créez des budgets mensuels pour chaque catégorie et suivez votre progression.</div>
        <button class="btn-pri" @click="openModal()">
          <UIcon name="i-heroicons-plus" style="width:14px;height:14px" />
          Créer ma première enveloppe
        </button>
      </div>

      <!-- Table + Detail panel -->
      <div v-else class="env-table-layout">
        <!-- Envelopes table -->
        <div class="env-table-card">
          <table class="env-table">
            <thead>
              <tr class="env-table-head">
                <th class="th">Enveloppe</th>
                <th class="th" style="text-align:right">Assigné</th>
                <th class="th" style="text-align:right">Activité</th>
                <th class="th" style="text-align:right">Disponible</th>
                <th class="th" style="text-align:right;width:140px">Progression</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="group in envelopeGroups" :key="group.id">
                <!-- Group header -->
                <tr class="group-header-row">
                  <td style="padding:10px 14px">
                    <button class="group-toggle" @click="openGroups[group.id] = !openGroups[group.id]">
                      <UIcon name="i-heroicons-chevron-right"
                        style="width:14px;height:14px;color:var(--ink-3);transition:transform 0.2s"
                        :style="{ transform: openGroups[group.id] ? 'rotate(90deg)' : 'rotate(0deg)' }"
                      />
                      <span class="group-dot" :style="{ background: group.color }" />
                      <span class="group-name">{{ group.name }}</span>
                      <span class="group-count">· {{ group.envelopes.length }}</span>
                    </button>
                  </td>
                  <td class="mono" style="padding:10px 14px;text-align:right;font-size:12.5px;color:var(--ink-2);font-weight:500">
                    CHF {{ groupTotal(group.envelopes, 'assigned').toFixed(2) }}
                  </td>
                  <td class="mono" style="padding:10px 14px;text-align:right;font-size:12.5px;color:var(--ink-3)">
                    −{{ groupTotal(group.envelopes, 'spent').toFixed(2) }}
                  </td>
                  <td class="mono" style="padding:10px 14px;text-align:right;font-size:12.5px;font-weight:500"
                    :style="{ color: groupTotal(group.envelopes, 'available') < 0 ? 'var(--danger)' : 'var(--ink-2)' }">
                    {{ groupTotal(group.envelopes, 'available') >= 0 ? '' : '−' }}{{ Math.abs(groupTotal(group.envelopes, 'available')).toFixed(2) }}
                  </td>
                  <td class="mono" style="padding:10px 14px;text-align:right;font-size:11px;color:var(--ink-3)">
                    {{ groupTotal(group.envelopes, 'assigned') > 0 ? ((groupTotal(group.envelopes, 'spent') / groupTotal(group.envelopes, 'assigned')) * 100).toFixed(0) + '%' : '' }}
                  </td>
                </tr>

                <!-- Envelope rows -->
                <template v-if="openGroups[group.id]">
                  <tr v-for="env in group.envelopes" :key="env.id"
                    class="env-row"
                    :class="{ 'env-row-selected': selectedEnvelopeId === env.id }"
                    @click="selectedEnvelopeId = selectedEnvelopeId === env.id ? null : env.id"
                  >
                    <td style="padding:10px 14px 10px 40px">
                      <div style="display:flex;align-items:center;gap:10px">
                        <span class="env-icon" :style="{
                          background: `color-mix(in oklab, ${group.color} 12%, var(--surface))`,
                          color: group.color,
                          border: `1px solid color-mix(in oklab, ${group.color} 20%, transparent)`
                        }">
                          <UIcon :name="env.isSavings ? 'i-heroicons-banknotes' : 'i-heroicons-tag'" style="width:14px;height:14px" />
                        </span>
                        <div style="display:flex;flex-direction:column">
                          <span style="font-size:13.5px;font-weight:500;color:var(--ink)">{{ env.name }}</span>
                          <span v-if="env.budgetObj.category_details" style="font-size:11px;color:var(--ink-3)">{{ env.budgetObj.category_details.name }}</span>
                        </div>
                      </div>
                    </td>

                    <!-- Amount cell (click to edit) -->
                    <td style="padding:10px 14px;text-align:right" @click.stop>
                      <div v-if="editingCellId === env.id" class="amount-cell-editing">
                        <input
                          :id="`cell-${env.id}`"
                          v-model="editDraft"
                          class="mono amount-input"
                          @keydown.enter="commitEdit(env)"
                          @keydown.escape="cancelEdit"
                          @blur="commitEdit(env)"
                        />
                      </div>
                      <button v-else class="amount-cell-btn mono" @click="startEdit(env)">
                        {{ env.assigned.toFixed(2) }}
                      </button>
                    </td>

                    <td class="mono" style="padding:10px 14px;text-align:right;font-size:13.5px;color:var(--ink-2)">
                      −{{ env.spent.toFixed(2) }}
                    </td>

                    <td style="padding:10px 14px;text-align:right">
                      <span class="avail-badge mono" :style="{
                        background: env.assigned === 0 ? 'var(--surface-2)' : env.isOver ? 'var(--danger-soft)' : 'color-mix(in oklab, #16a34a 12%, transparent)',
                        border: env.assigned === 0 ? '1px solid var(--line)' : env.isOver ? '1px solid color-mix(in oklab, var(--danger) 30%, transparent)' : '1px solid color-mix(in oklab, #16a34a 24%, transparent)',
                        color: env.assigned === 0 ? 'var(--ink-3)' : env.isOver ? 'var(--danger)' : '#16a34a',
                      }">
                        {{ env.available >= 0 ? '' : '−' }}{{ Math.abs(env.available).toFixed(2) }}
                      </span>
                    </td>

                    <td style="padding:10px 14px;width:140px">
                      <div class="prog-track">
                        <div class="prog-fill" :style="{
                          width: env.pct + '%',
                          background: env.isOver
                            ? 'linear-gradient(90deg, #f59e0b, var(--danger))'
                            : group.color,
                        }" />
                      </div>
                    </td>
                  </tr>
                </template>
              </template>
            </tbody>
          </table>

          <!-- Footer -->
          <div class="table-footer">
            <button class="add-env-btn" @click="openModal()">
              <UIcon name="i-heroicons-plus" style="width:14px;height:14px" />
              Ajouter une enveloppe
            </button>
          </div>
        </div>

        <!-- Detail panel -->
        <aside v-if="selectedEnvelope" class="detail-panel">
          <!-- Header -->
          <div class="detail-header">
            <div style="display:flex;align-items:flex-start;gap:12px">
              <span class="detail-icon" :style="{
                background: `color-mix(in oklab, ${selectedEnvelope.group.color} 12%, var(--surface))`,
                color: selectedEnvelope.group.color,
                border: `1px solid color-mix(in oklab, ${selectedEnvelope.group.color} 22%, transparent)`,
              }">
                <UIcon :name="selectedEnvelope.env.isSavings ? 'i-heroicons-banknotes' : 'i-heroicons-tag'" style="width:20px;height:20px" />
              </span>
              <div style="flex:1;min-width:0">
                <div style="font-size:16px;font-weight:600;color:var(--ink);letter-spacing:-0.2px">{{ selectedEnvelope.env.name }}</div>
                <div style="font-size:12px;font-weight:500;margin-top:2px" :style="{ color: selectedEnvelope.group.color }">{{ selectedEnvelope.group.name }}</div>
              </div>
              <button class="detail-close-btn" @click="selectedEnvelopeId = null">
                <UIcon name="i-heroicons-x-mark" style="width:14px;height:14px" />
              </button>
            </div>
          </div>

          <div class="detail-body">
            <!-- Disponible -->
            <div class="detail-section">
              <div class="section-label">Disponible</div>
              <div class="detail-avail mono" :style="{
                color: selectedEnvelope.env.available < 0 ? 'var(--danger)' : selectedEnvelope.env.available === 0 ? 'var(--ink-3)' : '#16a34a'
              }">
                {{ selectedEnvelope.env.available >= 0 ? '' : '−' }}CHF {{ Math.abs(selectedEnvelope.env.available).toFixed(2) }}
              </div>
              <div style="font-size:12px;color:var(--ink-3);margin-top:8px;display:flex;justify-content:space-between">
                <span>Assigné <span class="mono" style="color:var(--ink-2)">{{ selectedEnvelope.env.assigned.toFixed(2) }}</span></span>
                <span>Activité <span class="mono" style="color:var(--ink-2)">−{{ selectedEnvelope.env.spent.toFixed(2) }}</span></span>
              </div>
            </div>

            <!-- Quick assign -->
            <div class="detail-section">
              <div class="section-label" style="margin-bottom:10px">Assigner rapidement</div>
              <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button v-for="amt in [20, 50, 100, 200, 500]" :key="amt"
                  class="quick-btn"
                  @click="startEdit(selectedEnvelope.env)">
                  <span style="font-size:11px">+</span>
                  <span class="mono">{{ amt }}</span>
                </button>
              </div>
              <div style="display:flex;gap:6px;margin-top:8px">
                <button class="quick-action-btn" @click="startEdit(selectedEnvelope.env)">
                  <UIcon name="i-heroicons-minus" style="width:12px;height:12px" />
                  <span class="mono">50</span>
                </button>
                <button class="quick-action-btn" @click="startEdit(selectedEnvelope.env)">
                  Ajuster au dépensé
                </button>
              </div>
            </div>

            <!-- Recent transactions -->
            <div class="detail-section">
              <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px">
                <span class="section-label">Activité du mois</span>
                <button class="view-txn-btn" @click="viewBudgetTransactions(selectedEnvelope.env.budgetObj)">
                  Voir tout
                </button>
              </div>
              <div style="font-size:12px;color:var(--ink-3);text-align:center;padding:16px 0">
                Cliquez sur "Voir tout" pour consulter les transactions de cette enveloppe.
              </div>
            </div>

            <!-- Actions -->
            <div style="padding:16px 0 0;display:flex;flex-direction:column;gap:4px">
              <button class="detail-action-btn" @click="openModal(selectedEnvelope.env.budgetObj)">
                <UIcon name="i-heroicons-pencil" style="width:14px;height:14px;color:var(--ink-3)" />
                Modifier l'enveloppe
              </button>
              <button class="detail-action-btn danger" @click="handleDelete(selectedEnvelope.env.budgetObj)">
                <UIcon name="i-heroicons-trash" style="width:14px;height:14px" />
                Supprimer l'enveloppe
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <!-- Budget Modal -->
    <UModal
      v-model="showModal"
      :ui="{
        width: 'w-full sm:max-w-lg',
        container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
        base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
        padding: 'p-0', background: '', ring: '', shadow: '',
      }"
    >
      <div class="modal-panel">
        <div class="modal-handle" aria-hidden />
        <div class="modal-header">
          <div class="modal-header-icon">
            <UIcon :name="editingBudget ? 'i-heroicons-pencil' : 'i-heroicons-envelope'" style="width:16px;height:16px;" />
          </div>
          <h3 class="modal-title">{{ editingBudget ? 'Modifier le budget' : 'Nouvelle enveloppe' }}</h3>
          <button class="modal-close" type="button" @click="closeModal">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="handleSubmit">

          <!-- Nom -->
          <div class="field-group">
            <label class="field-label">Nom <span class="field-required">*</span></label>
            <div class="field-wrap" :class="{ 'field-error': getErrorForField(formErrors, 'name') }">
              <UIcon name="i-heroicons-tag" class="field-icon" />
              <input v-model="form.name" type="text" placeholder="Ex: Alimentation" class="field-input" required />
            </div>
            <p v-if="getErrorForField(formErrors, 'name')" class="field-err">{{ getErrorForField(formErrors, 'name') }}</p>
          </div>

          <!-- Catégorie (si pas épargne) -->
          <div v-if="!form.is_savings_goal && !form.is_mandatory_savings" class="field-group">
            <label class="field-label">Catégorie <span class="field-required">*</span></label>
            <USelectMenu v-model="form.category" :options="categories" option-attribute="name" value-attribute="id" placeholder="Sélectionner une catégorie" size="lg" />
            <p v-if="getErrorForField(formErrors, 'category')" class="field-err">{{ getErrorForField(formErrors, 'category') }}</p>
          </div>

          <!-- Montant -->
          <div class="field-group">
            <label class="field-label">Montant (CHF) <span class="field-required">*</span></label>
            <div class="field-wrap" :class="{ 'field-error': getErrorForField(formErrors, 'amount') }">
              <UIcon name="i-heroicons-banknotes" class="field-icon" />
              <input v-model="form.amount" type="number" step="0.01" placeholder="0.00" class="field-input" inputmode="decimal" required />
            </div>
            <p v-if="getErrorForField(formErrors, 'amount')" class="field-err">{{ getErrorForField(formErrors, 'amount') }}</p>
          </div>

          <!-- Période -->
          <div class="field-group">
            <label class="field-label">Période <span class="field-required">*</span></label>
            <USelectMenu v-model="form.period" :options="[{ label: 'Mensuel', value: 'monthly' }, { label: 'Hebdomadaire', value: 'weekly' }, { label: 'Annuel', value: 'yearly' }]" option-attribute="label" value-attribute="value" size="lg" />
            <p v-if="getErrorForField(formErrors, 'period')" class="field-err">{{ getErrorForField(formErrors, 'period') }}</p>
          </div>

          <!-- Dates (2 colonnes) -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div class="field-group">
              <label class="field-label">Date de début <span class="field-required">*</span></label>
              <div class="field-wrap">
                <input v-model="form.start_date" type="date" class="field-input" required />
              </div>
              <p v-if="getErrorForField(formErrors, 'start_date')" class="field-err">{{ getErrorForField(formErrors, 'start_date') }}</p>
            </div>
            <div class="field-group">
              <label class="field-label">Date de fin</label>
              <div class="field-wrap">
                <input v-model="form.end_date" type="date" class="field-input" />
              </div>
            </div>
          </div>

          <!-- Seuil alerte -->
          <div class="field-group">
            <label class="field-label">Seuil d'alerte (%)</label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-bell" class="field-icon" />
              <input v-model.number="form.alert_threshold" type="number" min="0" max="100" placeholder="80" class="field-input" />
            </div>
          </div>

          <!-- Checkboxes -->
          <div style="display:flex;flex-direction:column;gap:8px;">
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:13.5px;color:var(--ink-2);">
              <UCheckbox v-model="form.is_active" />
              Budget actif
            </label>
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:13.5px;color:var(--ink-2);">
              <UCheckbox v-model="form.is_savings_goal" />
              Objectif d'épargne
            </label>
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:13.5px;color:var(--ink-2);">
              <UCheckbox v-model="form.is_mandatory_savings" />
              Épargne obligatoire
            </label>
          </div>

          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button type="button" class="ds-btn ds-btn-ghost" @click="closeModal">Annuler</button>
            <button type="submit" class="ds-btn ds-btn-primary" :disabled="loading">
              <span v-if="loading" class="btn-spinner" />
              <span v-else>{{ editingBudget ? 'Mettre à jour' : 'Créer' }}</span>
            </button>
          </div>
        </form>
      </div>
    </UModal>

    <!-- Income Modal -->
    <UModal
      v-model="showIncomeModal"
      :ui="{
        width: 'w-full sm:max-w-md',
        container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
        base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
        padding: 'p-0', background: '', ring: '', shadow: '',
      }"
    >
      <div class="modal-panel">
        <div class="modal-handle" aria-hidden />
        <div class="modal-header">
          <div class="modal-header-icon" style="background:var(--success-soft);color:var(--success);">
            <UIcon name="i-heroicons-banknotes" style="width:16px;height:16px;" />
          </div>
          <h3 class="modal-title">Revenu mensuel</h3>
          <button class="modal-close" type="button" @click="closeIncomeModal">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="handleIncomeUpdate">
          <div class="field-group">
            <label class="field-label">Revenu mensuel (CHF) <span class="field-required">*</span></label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-banknotes" class="field-icon" />
              <input v-model="incomeForm.monthly_income" type="number" step="0.01" placeholder="0.00" class="field-input" inputmode="decimal" required />
              <span style="font-size:13px;color:var(--ink-3);flex-shrink:0;">CHF</span>
            </div>
          </div>
          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button type="button" class="ds-btn ds-btn-ghost" @click="closeIncomeModal">Annuler</button>
            <button type="submit" class="ds-btn ds-btn-primary" :disabled="loading">
              <span v-if="loading" class="btn-spinner" />
              <span v-else>Enregistrer</span>
            </button>
          </div>
        </form>
      </div>
    </UModal>

    <!-- Confirm Delete -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer l'enveloppe"
      :message="`Êtes-vous sûr de vouloir supprimer « ${budgetToDelete?.name} » ?`"
      confirm-label="Supprimer"
      @confirm="executeDelete"
    />

    <!-- Transactions Modal -->
    <UModal
      v-model="showTransactionsModal"
      :ui="{
        width: 'w-full sm:max-w-2xl',
        container: 'flex min-h-full sm:min-h-0 items-end sm:items-center justify-center',
        base: 'relative text-left overflow-hidden w-full sm:rounded-xl rounded-t-xl rounded-b-none',
        padding: 'p-0', background: '', ring: '', shadow: '',
      }"
    >
      <div class="modal-panel">
        <div class="modal-handle" aria-hidden />
        <div class="modal-header">
          <div class="modal-header-icon">
            <UIcon :name="selectedBudget?.is_savings_goal ? 'i-heroicons-banknotes' : 'i-heroicons-receipt-percent'" style="width:16px;height:16px;" />
          </div>
          <div style="flex:1;min-width:0;">
            <h3 class="modal-title" style="flex:none;">{{ selectedBudget?.is_savings_goal ? "Transferts d'épargne" : 'Transactions du budget' }}</h3>
            <p style="font-size:12px;color:var(--ink-3);margin:0;">{{ selectedBudget?.name }}</p>
          </div>
          <button class="modal-close" type="button" @click="closeTransactionsModal">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>

        <!-- Empty state -->
        <div v-if="budgetTransactions.length === 0" style="padding:48px 20px;text-align:center;">
          <UIcon name="i-heroicons-inbox" style="width:48px;height:48px;color:var(--ink-4);margin-bottom:12px;" />
          <p style="font-size:14px;color:var(--ink-3);">Aucune transaction pour cette période</p>
        </div>

        <!-- Transaction list -->
        <div v-else class="modal-body" style="gap:0;padding:0;">
          <div
            v-for="transaction in budgetTransactions"
            :key="transaction.id"
            style="display:flex;align-items:center;gap:12px;padding:12px 20px;border-bottom:1px solid var(--line);"
          >
            <div style="width:34px;height:34px;border-radius:9px;display:grid;place-items:center;flex-shrink:0;"
              :style="{
                background: transaction.type === 'transfer' ? 'var(--accent-soft)' : 'var(--danger-soft)',
                color: transaction.type === 'transfer' ? 'var(--accent)' : 'var(--danger)',
              }"
            >
              <UIcon :name="transaction.type === 'transfer' ? 'i-heroicons-arrow-right-circle' : 'i-heroicons-arrow-up-circle'" style="width:15px;height:15px;" />
            </div>
            <div style="flex:1;min-width:0;">
              <p style="margin:0;font-size:13.5px;font-weight:500;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                {{ transaction.description || (transaction.type === 'transfer' ? 'Transfert' : 'Dépense') }}
              </p>
              <p style="margin:2px 0 0;font-size:11.5px;color:var(--ink-3);">{{ formatDate(transaction.date) }}</p>
            </div>
            <p class="mono" style="font-size:14px;font-weight:500;flex-shrink:0;"
              :style="{ color: transaction.type === 'transfer' ? 'var(--accent)' : 'var(--danger)' }">
              {{ formatCurrency(transaction.amount) }}
            </p>
          </div>
          <!-- Total row -->
          <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 20px;background:var(--surface-2);border-top:1px solid var(--line-strong);">
            <span style="font-size:13px;font-weight:500;color:var(--ink-2);">Total</span>
            <span class="mono" style="font-size:15px;font-weight:600;"
              :style="{ color: selectedBudget?.is_savings_goal ? 'var(--success)' : 'var(--danger)' }">
              {{ formatCurrency(budgetTransactions.reduce((sum, t) => sum + parseFloat(t.amount || 0), 0)) }}
            </span>
          </div>
        </div>

        <div class="modal-footer">
          <button class="ds-btn ds-btn-ghost" @click="closeTransactionsModal">Fermer</button>
        </div>
      </div>
    </UModal>
  </div>
</template>

<style scoped>
/* Page layout */
.env-page {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background: var(--bg);
}

/* TopBar */
.env-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 32px 0;
  flex-wrap: wrap;
}
.env-topbar-left { display: flex; flex-direction: column; gap: 2px; }
.env-topbar-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

/* Buttons */
.btn-pri {
  display: inline-flex; align-items: center; gap: 6px;
  height: 36px; padding: 0 14px;
  background: var(--accent); color: #fff;
  border: none; border-radius: 8px;
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: opacity 0.12s;
}
.btn-pri:hover { opacity: 0.9; }
.btn-sec {
  display: inline-flex; align-items: center; gap: 6px;
  height: 36px; padding: 0 14px;
  background: var(--surface); color: var(--ink-2);
  border: 1px solid var(--line); border-radius: 8px;
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: background 0.12s;
}
.btn-sec:hover { background: var(--surface-2); }

/* Content */
.env-content {
  padding: 20px 32px 40px;
  display: flex; flex-direction: column; gap: 18px;
  max-width: 1500px; margin: 0 auto; width: 100%;
}

/* Hero banner */
.hero-banner {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px; padding: 28px;
  display: grid; grid-template-columns: 1.3fr 1fr; gap: 28px;
  box-shadow: var(--shadow-sm);
  position: relative; overflow: hidden;
  transition: background 0.3s, border-color 0.3s;
}
.hero-banner.hero-positive {
  background: linear-gradient(135deg, color-mix(in oklab, var(--accent) 9%, var(--surface)) 0%, var(--surface) 60%);
  border-color: color-mix(in oklab, var(--accent) 22%, var(--line));
}
.hero-label {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: var(--ink-3);
  text-transform: uppercase; letter-spacing: 0.6px; font-weight: 500;
}
.hero-amount {
  font-size: 52px; font-weight: 500; letter-spacing: -2px;
  line-height: 1; margin-top: 6px;
}
.hero-desc {
  margin: 10px 0 0; font-size: 14px; color: var(--ink-2);
  max-width: 480px; line-height: 1.5;
}
.hero-actions { display: flex; gap: 8px; margin-top: 18px; flex-wrap: wrap; }
.hero-right { display: flex; flex-direction: column; justify-content: space-between; }
.hero-right-label {
  font-size: 12px; color: var(--ink-3);
  text-transform: uppercase; letter-spacing: 0.6px; font-weight: 500;
}
.progress-track {
  position: relative; height: 10px;
  background: var(--surface-2); border-radius: 999px;
  overflow: hidden; border: 1px solid var(--line);
}
.progress-fill {
  position: absolute; inset: 0;
  background: linear-gradient(90deg, var(--accent), color-mix(in oklab, var(--accent) 60%, #fff));
  border-radius: 999px; transition: width 0.4s ease;
}
.hero-stats {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-top: 20px;
}
.hero-stat-card {
  padding: 10px 12px;
  background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
}
.hero-stat-label {
  font-size: 10.5px; color: var(--ink-3);
  text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500;
}
.hero-stat-value { font-size: 17px; font-weight: 500; margin-top: 2px; line-height: 1.2; }

/* Empty state */
.empty-state-card {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 14px; padding: 48px 32px;
  text-align: center; box-shadow: var(--shadow-sm);
}

/* Table layout */
.env-table-layout { display: flex; gap: 18px; align-items: flex-start; }

/* Envelopes table */
.env-table-card {
  flex: 1; min-width: 0;
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 14px; overflow: hidden; box-shadow: var(--shadow-sm);
}
.env-table { width: 100%; border-collapse: collapse; table-layout: auto; }
.env-table-head { background: var(--surface); border-bottom: 1px solid var(--line); }
.th {
  padding: 12px 14px; text-align: left;
  font-size: 10.5px; font-weight: 500; color: var(--ink-3);
  text-transform: uppercase; letter-spacing: 0.6px;
  border-bottom: 1px solid var(--line);
}

/* Group header row */
.group-header-row {
  background: var(--surface-2);
  border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);
}
.group-toggle {
  display: flex; align-items: center; gap: 8px;
  background: transparent; border: none; cursor: pointer;
  text-align: left; padding: 0; width: 100%;
}
.group-dot { width: 8px; height: 8px; border-radius: 2px; flex-shrink: 0; }
.group-name { font-size: 12.5px; font-weight: 600; color: var(--ink); letter-spacing: -0.1px; text-transform: uppercase; }
.group-count { font-size: 11.5px; color: var(--ink-3); font-weight: 400; }

/* Envelope row */
.env-row {
  border-bottom: 1px solid var(--line);
  cursor: pointer; transition: background 0.1s;
}
.env-row:hover { background: var(--surface-2); }
.env-row-selected { background: var(--accent-soft) !important; }

/* Env icon chip */
.env-icon {
  width: 28px; height: 28px; border-radius: 7px;
  display: grid; place-items: center; flex-shrink: 0;
}

/* Amount cell */
.amount-cell-editing {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 8px; background: var(--surface);
  border: 1px solid var(--accent); border-radius: 6px;
  height: 28px; box-shadow: 0 0 0 3px var(--ring);
}
.amount-input {
  width: 70px; text-align: right; font-size: 13.5px;
  color: var(--ink); font-weight: 500;
  background: transparent; border: none; outline: none;
}
.amount-cell-btn {
  display: inline-flex; align-items: center; justify-content: flex-end;
  padding: 4px 10px; height: 28px;
  font-size: 13.5px; color: var(--ink); font-weight: 500;
  background: transparent; border: 1px dashed transparent;
  border-radius: 6px; cursor: text; transition: all 0.12s;
  width: 100%;
}
.amount-cell-btn:hover {
  background: var(--surface-2); border-color: var(--line-strong);
}

/* Available badge */
.avail-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 10px; border-radius: 999px;
  font-size: 13px; font-weight: 500;
}

/* Progress bar */
.prog-track {
  position: relative; height: 5px;
  background: var(--surface-2); border-radius: 999px; overflow: hidden;
}
.prog-fill { position: absolute; inset: 0; border-radius: 999px; }

/* Table footer */
.table-footer {
  padding: 12px 16px; border-top: 1px solid var(--line);
  background: var(--surface-2);
}
.add-env-btn {
  display: inline-flex; align-items: center; gap: 6px;
  background: transparent; border: none; cursor: pointer;
  color: var(--accent); font-size: 13px; font-weight: 500;
  padding: 4px 0;
}
.add-env-btn:hover { opacity: 0.8; }

/* Detail panel */
.detail-panel {
  position: sticky; top: 20px; align-self: flex-start;
  width: 360px; flex-shrink: 0;
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 14px; box-shadow: var(--shadow-sm);
  overflow: hidden; display: flex; flex-direction: column;
  max-height: calc(100vh - 40px);
}
.detail-header {
  padding: 20px 20px 16px; border-bottom: 1px solid var(--line);
}
.detail-icon {
  width: 42px; height: 42px; border-radius: 10px;
  display: grid; place-items: center; flex-shrink: 0;
}
.detail-close-btn {
  width: 28px; height: 28px; border-radius: 6px;
  background: transparent; border: 1px solid var(--line);
  cursor: pointer; display: grid; place-items: center;
  color: var(--ink-3); flex-shrink: 0;
}
.detail-close-btn:hover { background: var(--surface-2); }
.detail-body { flex: 1; overflow-y: auto; padding: 0 20px 20px; }
.detail-section { padding: 16px 0; border-bottom: 1px solid var(--line); }
.section-label {
  font-size: 11px; color: var(--ink-3);
  text-transform: uppercase; letter-spacing: 0.6px; font-weight: 500;
}
.detail-avail { font-size: 32px; font-weight: 500; letter-spacing: -1px; line-height: 1; margin-top: 4px; }

/* Quick buttons */
.quick-btn {
  padding: 6px 12px; height: 30px;
  background: var(--surface-2); border: 1px solid var(--line);
  border-radius: 7px; font-size: 12.5px; color: var(--ink-2);
  cursor: pointer; font-weight: 500;
  display: inline-flex; align-items: center; gap: 3px;
  transition: all 0.12s;
}
.quick-btn:hover { background: var(--accent-soft); color: var(--accent); border-color: color-mix(in oklab, var(--accent) 30%, transparent); }
.quick-action-btn {
  flex: 1; height: 32px; font-size: 12.5px; font-weight: 500;
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 7px; cursor: pointer; color: var(--ink-2);
  display: inline-flex; align-items: center; justify-content: center; gap: 5px;
  transition: background 0.12s;
}
.quick-action-btn:hover { background: var(--surface-2); }

/* View transactions btn */
.view-txn-btn {
  font-size: 11px; color: var(--accent); font-weight: 500;
  background: transparent; border: none; cursor: pointer;
  padding: 0;
}
.view-txn-btn:hover { opacity: 0.8; }

/* Detail action buttons */
.detail-action-btn {
  display: flex; align-items: center; gap: 10px; width: 100%;
  padding: 8px 10px; background: transparent; border: 1px solid transparent;
  border-radius: 7px; cursor: pointer; text-align: left;
  font-size: 12.5px; color: var(--ink-2); font-weight: 500;
  transition: background 0.12s;
}
.detail-action-btn:hover { background: var(--surface-2); border-color: var(--line); }
.detail-action-btn.danger { color: var(--danger); }
.detail-action-btn.danger:hover { background: var(--danger-soft); border-color: transparent; }

/* Mono font */
.mono { font-family: 'Geist Mono', ui-monospace, monospace; }

/* Mobile */
@media (max-width: 768px) {
  .env-topbar { padding: 14px 16px 0; }
  .env-content { padding: 14px 16px 32px; }
  .hero-banner { grid-template-columns: 1fr; gap: 20px; padding: 20px; }
  .hero-amount { font-size: 36px; }
  .env-table-layout { flex-direction: column; }
  .detail-panel { width: 100%; position: static; max-height: none; }
  .env-topbar-right { gap: 6px; }
  .btn-pri span, .btn-sec span { display: none; }
}
</style>
