<script setup lang="ts">
import type { RecurringSeries } from '~/types'
import type { StandardError } from '~/types/errors'

definePageMeta({
  middleware: 'auth'
})

const { getRecurringSeries, updateSeries, deleteSeries } = useRecurring()
const { createTransaction, generateRecurring } = useTransactions()
const { getAccounts } = useAccounts()
const { getCategories } = useCategories()
const { getErrorForField, formatForToast } = useErrorHandler()
const { ensureProfileLoaded } = useUserProfile()
const toast = useToast()

// ─── State ───────────────────────────────────────────────────────────────────

const series = ref<RecurringSeries[]>([])
const loading = ref(false)
const loadError = ref(false)

// Modal de création d'une nouvelle série
const showCreateModal = ref(false)
const createForm = ref({
  type: 'expense',
  account: '' as string | number,
  destination_account: '' as string | number,
  category: '' as string | number,
  amount: '',
  description: '',
  date: new Date().toISOString().slice(0, 10),
  recurrence_frequency: 'monthly',
  recurrence_interval: 1,
  recurrence_end_date: '',
})
const createErrors = ref<StandardError | null>(null)
const creating = ref(false)

const resetCreateForm = () => {
  createForm.value = {
    type: 'expense',
    account: '',
    destination_account: '',
    category: '',
    amount: '',
    description: '',
    date: new Date().toISOString().slice(0, 10),
    recurrence_frequency: 'monthly',
    recurrence_interval: 1,
    recurrence_end_date: '',
  }
  createErrors.value = null
}

const handleCreate = async () => {
  creating.value = true
  createErrors.value = null

  const payload: Record<string, unknown> = {
    type: createForm.value.type,
    account: createForm.value.account,
    amount: createForm.value.amount,
    description: createForm.value.description,
    date: createForm.value.date,
    is_recurring: true,
    recurrence_frequency: createForm.value.recurrence_frequency,
    recurrence_interval: createForm.value.recurrence_interval,
  }
  if (createForm.value.category) payload.category = createForm.value.category
  if (createForm.value.type === 'transfer' && createForm.value.destination_account)
    payload.destination_account = createForm.value.destination_account
  if (createForm.value.recurrence_end_date)
    payload.recurrence_end_date = createForm.value.recurrence_end_date

  const result = await createTransaction(payload)
  creating.value = false

  if (result.success) {
    toast.add({ title: 'Série créée', description: 'La première occurrence sera générée automatiquement.', color: 'green' })
    showCreateModal.value = false
    resetCreateForm()
    await generateRecurring()
    await fetchSeries()
  } else {
    createErrors.value = result.error ?? null
    toast.add({ title: 'Erreur', description: formatForToast(result.error ?? null), color: 'red' })
  }
}

// Modal d'édition d'une série
const showEditModal = ref(false)
const editingSeries = ref<RecurringSeries | null>(null)
const formErrors = ref<StandardError | null>(null)
const submitting = ref(false)

// Modal de confirmation de suppression (unitaire)
const showConfirmDelete = ref(false)
const seriesToDelete = ref<RecurringSeries | null>(null)
const deleting = ref(false)

// Sélection multiple
const selectedIds = ref<Set<number>>(new Set())
const allSelected = computed(() =>
  series.value.length > 0 && series.value.every(s => selectedIds.value.has(s.id))
)
const someSelected = computed(() => selectedIds.value.size > 0)

const toggleSelect = (id: number) => {
  const next = new Set(selectedIds.value)
  next.has(id) ? next.delete(id) : next.add(id)
  selectedIds.value = next
}
const toggleSelectAll = () => {
  selectedIds.value = allSelected.value
    ? new Set()
    : new Set(series.value.map(s => s.id))
}
const clearSelection = () => { selectedIds.value = new Set() }

// Modal de confirmation de suppression en masse
const showConfirmBulkDelete = ref(false)
const bulkDeleting = ref(false)

const executeBulkDelete = async () => {
  bulkDeleting.value = true
  const toDelete = series.value.filter(s => selectedIds.value.has(s.id))
  let failed = 0
  for (const s of toDelete) {
    const result = await deleteSeries(s.recurring_series_id, s.id)
    if (!result.success) failed++
  }
  bulkDeleting.value = false
  showConfirmBulkDelete.value = false
  clearSelection()
  await fetchSeries()
  if (failed === 0) {
    toast.add({ title: `${toDelete.length} série(s) supprimée(s)`, color: 'green' })
  } else {
    toast.add({ title: `${toDelete.length - failed} supprimée(s), ${failed} erreur(s)`, color: 'orange' })
  }
}

// Formulaire d'édition de série
const form = ref({
  description: '',
  amount: '',
  category: '' as string | number,
  notes: '',
  recurrence_end_date: '',
})

// Données auxiliaires pour les selects
const accounts = ref<Array<{ id: number; name: string }>>([])
const categories = ref<Array<{ id: number; name: string; type: string }>>([])

// ─── Computed ─────────────────────────────────────────────────────────────────

const availableCategories = computed(() => {
  if (!editingSeries.value) return categories.value
  return categories.value.filter(c => c.type === editingSeries.value!.type)
})

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Retourne le label français de la fréquence de récurrence.
 */
const frequencyLabel = (freq: string, interval: number): string => {
  const labels: Record<string, string[]> = {
    daily:   ['Tous les jours', 'Tous les %n jours'],
    weekly:  ['Toutes les semaines', 'Toutes les %n semaines'],
    monthly: ['Tous les mois', 'Tous les %n mois'],
    yearly:  ['Tous les ans', 'Tous les %n ans'],
  }
  const pair = labels[freq] ?? ['Périodique', 'Tous les %n']
  if (interval <= 1) return pair[0]
  return pair[1].replace('%n', interval.toString())
}

/**
 * Icône Heroicons selon la fréquence de récurrence.
 */
const frequencyIcon = (freq: string): string => {
  const icons: Record<string, string> = {
    daily:   'i-heroicons-sun',
    weekly:  'i-heroicons-calendar-days',
    monthly: 'i-heroicons-calendar',
    yearly:  'i-heroicons-archive-box',
  }
  return icons[freq] ?? 'i-heroicons-arrow-path'
}

/**
 * Couleur CSS variable selon le type de transaction.
 */
const typeColor = (type: string): string => {
  switch (type) {
    case 'income':   return 'var(--success)'
    case 'expense':  return 'var(--danger)'
    case 'transfer': return 'var(--accent)'
    default:         return 'var(--ink-3)'
  }
}

/**
 * Couleur de fond (soft) selon le type de transaction.
 */
const typeBgColor = (type: string): string => {
  switch (type) {
    case 'income':   return 'var(--success-soft)'
    case 'expense':  return 'var(--danger-soft)'
    case 'transfer': return 'var(--accent-soft)'
    default:         return 'var(--surface-2)'
  }
}

/**
 * Label français du type.
 */
const typeLabel = (type: string): string => {
  switch (type) {
    case 'income':   return 'Revenu'
    case 'expense':  return 'Dépense'
    case 'transfer': return 'Transfert'
    default:         return type
  }
}

/**
 * Formate une date ISO en format court français.
 */
const formatDate = (iso: string | null): string => {
  if (!iso) return '—'
  return new Date(iso + 'T00:00:00').toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

// ─── Data fetching ─────────────────────────────────────────────────────────────

const fetchSeries = async () => {
  loading.value = true
  loadError.value = false
  const result = await getRecurringSeries()
  if (result.success && result.data) {
    series.value = result.data
  } else {
    loadError.value = true
  }
  loading.value = false
}

const fetchAuxData = async () => {
  const [accountsResult, categoriesResult] = await Promise.all([
    getAccounts(),
    getCategories(),
  ])
  if (accountsResult.success && accountsResult.data) {
    accounts.value = accountsResult.data.results
  }
  if (categoriesResult.success && categoriesResult.data) {
    categories.value = categoriesResult.data.results
  }
}

// ─── Edit ──────────────────────────────────────────────────────────────────────

const openEditModal = (s: RecurringSeries) => {
  editingSeries.value = s
  form.value = {
    description: s.description,
    amount: s.amount,
    category: s.category?.id?.toString() ?? '',
    notes: '',
    recurrence_end_date: s.recurrence_end_date ?? '',
  }
  formErrors.value = null
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingSeries.value = null
  formErrors.value = null
}

const handleUpdate = async () => {
  if (!editingSeries.value) return
  submitting.value = true
  formErrors.value = null

  const payload: Parameters<typeof updateSeries>[1] = {
    description: form.value.description,
    amount: form.value.amount,
  }
  if (form.value.category) payload.category = parseInt(form.value.category as string)
  else payload.category = null
  if (form.value.notes) payload.notes = form.value.notes
  if (form.value.recurrence_end_date) payload.recurrence_end_date = form.value.recurrence_end_date
  else payload.recurrence_end_date = null

  const result = await updateSeries(editingSeries.value.id, payload)
  submitting.value = false

  if (result.success) {
    toast.add({
      title: 'Série mise à jour',
      description: `${result.updated} occurrence(s) modifiée(s)`,
      color: 'green',
    })
    closeEditModal()
    await fetchSeries()
  } else if (result.error) {
    formErrors.value = result.error
    toast.add({
      title: 'Erreur',
      description: formatForToast(result.error),
      color: 'red',
    })
  }
}

// ─── Delete ────────────────────────────────────────────────────────────────────

const handleDeleteClick = (s: RecurringSeries) => {
  seriesToDelete.value = s
  showConfirmDelete.value = true
}

const executeDelete = async () => {
  if (!seriesToDelete.value) return
  deleting.value = true

  const result = await deleteSeries(
    seriesToDelete.value.recurring_series_id,
    seriesToDelete.value.id,
  )
  deleting.value = false
  showConfirmDelete.value = false

  if (result.success) {
    toast.add({
      title: 'Série supprimée',
      description: 'Le template de la série a été supprimé.',
      color: 'green',
    })
    seriesToDelete.value = null
    await fetchSeries()
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Impossible de supprimer la série.',
      color: 'red',
    })
  }
}

// ─── Lifecycle ─────────────────────────────────────────────────────────────────

onMounted(async () => {
  await ensureProfileLoaded()
  await Promise.all([fetchSeries(), fetchAuxData()])
})
</script>

<template>
  <div class="page-root fade-up">

    <!-- ── Header ──────────────────────────────────────────────── -->
    <PageHeader
      title="Transactions récurrentes"
      :subtitle="series.length > 0 ? `${series.length} série(s) active(s)` : 'Gérez vos dépenses et revenus périodiques'"
    >
      <template #actions>
        <button
          class="ds-btn-icon sm:hidden"
          :disabled="loading"
          aria-label="Rafraîchir"
          @click="fetchSeries()"
        >
          <UIcon name="i-heroicons-arrow-path" style="width:15px;height:15px;" :class="{ 'spin': loading }" />
        </button>
        <button class="ds-btn-icon sm:hidden" aria-label="Nouvelle série" @click="showCreateModal = true">
          <UIcon name="i-heroicons-plus" style="width:15px;height:15px;" />
        </button>
        <span class="hidden sm:inline-flex" style="gap:8px;">
          <button class="ds-btn ds-btn-secondary" :disabled="loading" @click="fetchSeries()">
            <UIcon name="i-heroicons-arrow-path" style="width:14px;height:14px;" :class="{ 'spin': loading }" />
            Rafraîchir
          </button>
          <button class="ds-btn ds-btn-primary" @click="showCreateModal = true">
            <UIcon name="i-heroicons-plus" style="width:14px;height:14px;" />
            Nouvelle série
          </button>
        </span>
      </template>
    </PageHeader>

    <!-- ── Loading skeletons ───────────────────────────────────── -->
    <div v-if="loading" class="series-list">
      <div v-for="i in 4" :key="i" class="series-card skeleton-card">
        <div class="skeleton-icon" />
        <div style="flex:1;">
          <div class="skeleton-line" style="width:60%;height:14px;" />
          <div class="skeleton-line" style="width:40%;height:11px;margin-top:7px;" />
        </div>
        <div class="skeleton-line" style="width:80px;height:18px;" />
      </div>
    </div>

    <!-- ── Error ───────────────────────────────────────────────── -->
    <div v-else-if="loadError">
      <EmptyState
        icon="i-heroicons-exclamation-circle"
        color="red"
        title="Impossible de charger les séries"
        description="Vérifiez votre connexion et réessayez."
        button-text="Réessayer"
        button-icon="i-heroicons-arrow-path"
        @action="fetchSeries()"
      />
    </div>

    <!-- ── Empty ───────────────────────────────────────────────── -->
    <div v-else-if="series.length === 0">
      <EmptyState
        icon="i-heroicons-arrow-path"
        color="purple"
        title="Aucune série récurrente"
        description="Créez une transaction récurrente depuis la page Transactions pour qu'elle apparaisse ici."
      />
    </div>

    <!-- ── Liste de cards ──────────────────────────────────────── -->
    <div v-else class="series-list">
      <div
        v-for="s in series"
        :key="s.id"
        class="series-card"
        :class="{ 'series-card--selected': selectedIds.has(s.id) }"
        @click="toggleSelect(s.id)"
      >
        <!-- Checkbox de sélection -->
        <label class="series-checkbox" @click.stop="toggleSelect(s.id)">
          <span class="series-checkbox-box" :class="{ checked: selectedIds.has(s.id) }">
            <svg v-if="selectedIds.has(s.id)" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
          </span>
        </label>

        <!-- Icône fréquence -->
        <div
          class="series-icon"
          :style="{
            background: typeBgColor(s.type),
            color: typeColor(s.type),
            border: `1px solid color-mix(in oklab, ${typeColor(s.type)} 25%, transparent)`,
          }"
        >
          <UIcon :name="frequencyIcon(s.recurrence_frequency)" style="width:16px;height:16px;" />
        </div>

        <!-- Contenu principal -->
        <div class="series-body">
          <div class="series-desc">{{ s.description || '(sans description)' }}</div>
          <div class="series-meta">
            <span class="series-account">{{ s.account.name }}</span>
            <span class="series-dot">·</span>
            <span>{{ frequencyLabel(s.recurrence_frequency, s.recurrence_interval) }}</span>
          </div>
          <div class="series-details">
            <!-- Badge type -->
            <span
              class="ds-badge"
              :style="{
                background: typeBgColor(s.type),
                color: typeColor(s.type),
                border: `1px solid color-mix(in oklab, ${typeColor(s.type)} 25%, transparent)`,
              }"
            >
              {{ typeLabel(s.type) }}
            </span>
            <!-- Catégorie si disponible -->
            <span v-if="s.category" class="series-category">{{ s.category.name }}</span>
          </div>
          <!-- Prochaine occurrence -->
          <div class="series-next">
            <UIcon name="i-heroicons-calendar" style="width:12px;height:12px;flex-shrink:0;" />
            <span v-if="s.next_occurrence">Prochaine : {{ formatDate(s.next_occurrence) }}</span>
            <span v-else style="color:var(--ink-4);">Aucune occurrence future</span>
            <span class="series-total">· {{ s.total_instances }} occ.</span>
          </div>
        </div>

        <!-- Montant + actions -->
        <div class="series-right">
          <div
            class="mono series-amount"
            :style="{ color: typeColor(s.type) }"
          >
            {{ s.type === 'expense' ? '−' : '+' }}{{ s.amount }} {{ s.account.currency }}
          </div>
          <div class="series-actions">
            <button
              class="ds-btn-icon"
              aria-label="Modifier la série"
              @click="openEditModal(s)"
            >
              <UIcon name="i-heroicons-pencil" style="width:14px;height:14px;" />
            </button>
            <button
              class="ds-btn-icon ds-btn-icon--danger"
              aria-label="Supprimer la série"
              @click="handleDeleteClick(s)"
            >
              <UIcon name="i-heroicons-trash" style="width:14px;height:14px;" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Create Series Modal ──────────────────────────────────── -->
    <UModal
      v-model="showCreateModal"
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
            <UIcon name="i-heroicons-plus" style="width:16px;height:16px;" />
          </div>
          <h3 class="modal-title">Nouvelle série récurrente</h3>
          <button class="modal-close" type="button" @click="showCreateModal = false; resetCreateForm()">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="handleCreate">

          <!-- Type -->
          <div class="field-group">
            <label class="field-label">Type <span class="field-required">*</span></label>
            <div style="display:flex;gap:6px;">
              <button
                v-for="t in [{ value:'expense', label:'Dépense' }, { value:'income', label:'Revenu' }, { value:'transfer', label:'Transfert' }]"
                :key="t.value"
                type="button"
                class="type-btn"
                :class="{ active: createForm.type === t.value }"
                @click="createForm.type = t.value; createForm.category = ''"
              >{{ t.label }}</button>
            </div>
          </div>

          <!-- Compte -->
          <div class="field-group">
            <label class="field-label">Compte <span class="field-required">*</span></label>
            <USelectMenu
              v-model="createForm.account"
              :options="accounts"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner un compte"
              size="lg"
            />
            <p v-if="getErrorForField(createErrors, 'account')" class="field-err">{{ getErrorForField(createErrors, 'account') }}</p>
          </div>

          <!-- Compte destination (transfert) -->
          <div v-if="createForm.type === 'transfer'" class="field-group">
            <label class="field-label">Compte destination <span class="field-required">*</span></label>
            <USelectMenu
              v-model="createForm.destination_account"
              :options="accounts.filter(a => a.id !== createForm.account)"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner un compte"
              size="lg"
            />
            <p v-if="getErrorForField(createErrors, 'destination_account')" class="field-err">{{ getErrorForField(createErrors, 'destination_account') }}</p>
          </div>

          <!-- Catégorie -->
          <div v-if="createForm.type !== 'transfer'" class="field-group">
            <label class="field-label">Catégorie</label>
            <USelectMenu
              v-model="createForm.category"
              :options="[{ id: '', name: 'Aucune catégorie' }, ...categories.filter(c => c.type === createForm.type)]"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner une catégorie"
              size="lg"
            />
          </div>

          <!-- Montant + description côte à côte -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="field-group" style="margin:0">
              <label class="field-label">Montant <span class="field-required">*</span></label>
              <div class="field-wrap">
                <UIcon name="i-heroicons-banknotes" class="field-icon" />
                <input v-model="createForm.amount" type="number" step="0.01" min="0" placeholder="0.00" class="field-input" inputmode="decimal" required />
              </div>
              <p v-if="getErrorForField(createErrors, 'amount')" class="field-err">{{ getErrorForField(createErrors, 'amount') }}</p>
            </div>
            <div class="field-group" style="margin:0">
              <label class="field-label">Première occurrence <span class="field-required">*</span></label>
              <div class="field-wrap">
                <UIcon name="i-heroicons-calendar" class="field-icon" />
                <input v-model="createForm.date" type="date" class="field-input" required />
              </div>
            </div>
          </div>

          <!-- Description -->
          <div class="field-group">
            <label class="field-label">Description</label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-pencil-square" class="field-icon" />
              <input v-model="createForm.description" type="text" placeholder="Ex: Loyer, Netflix, Salaire…" class="field-input" inputmode="text" />
            </div>
          </div>

          <!-- Fréquence + intervalle côte à côte -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
            <div class="field-group" style="margin:0">
              <label class="field-label">Fréquence <span class="field-required">*</span></label>
              <USelectMenu
                v-model="createForm.recurrence_frequency"
                :options="[{ label:'Quotidien', value:'daily' }, { label:'Hebdomadaire', value:'weekly' }, { label:'Mensuel', value:'monthly' }, { label:'Annuel', value:'yearly' }]"
                option-attribute="label"
                value-attribute="value"
                size="lg"
              />
            </div>
            <div class="field-group" style="margin:0">
              <label class="field-label">Tous les</label>
              <div class="field-wrap">
                <input v-model.number="createForm.recurrence_interval" type="number" min="1" max="99" class="field-input" />
              </div>
            </div>
          </div>

          <!-- Date de fin -->
          <div class="field-group">
            <label class="field-label">Date de fin (optionnelle)</label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-calendar-days" class="field-icon" />
              <input v-model="createForm.recurrence_end_date" type="date" class="field-input" />
            </div>
          </div>

          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button type="button" class="ds-btn ds-btn-ghost" @click="showCreateModal = false; resetCreateForm()">Annuler</button>
            <button type="submit" class="ds-btn ds-btn-primary" :disabled="creating">
              <span v-if="creating" class="btn-spinner" />
              <span v-else>Créer la série</span>
            </button>
          </div>
        </form>
      </div>
    </UModal>

    <!-- ── Edit Series Modal ───────────────────────────────────── -->
    <UModal
      v-model="showEditModal"
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
            <UIcon name="i-heroicons-arrow-path" style="width:16px;height:16px;" />
          </div>
          <h3 class="modal-title">Modifier la série</h3>
          <button class="modal-close" type="button" @click="closeEditModal">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="handleUpdate">

          <!-- Info banner -->
          <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 12px;background:var(--accent-soft);border:1px solid color-mix(in oklab,var(--accent) 22%,transparent);border-radius:var(--radius);">
            <UIcon name="i-heroicons-information-circle" style="width:16px;height:16px;color:var(--accent);flex-shrink:0;margin-top:1px;" />
            <p style="font-size:13px;color:var(--accent);margin:0;line-height:1.5;">Les changements s'appliqueront à toutes les occurrences futures de cette série.</p>
          </div>

          <!-- Description -->
          <div class="field-group">
            <label class="field-label">Description</label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-pencil-square" class="field-icon" />
              <input v-model="form.description" type="text" placeholder="Description de la transaction" class="field-input" inputmode="text" />
            </div>
            <p v-if="getErrorForField(formErrors, 'description')" class="field-err">{{ getErrorForField(formErrors, 'description') }}</p>
          </div>

          <!-- Montant -->
          <div class="field-group">
            <label class="field-label">Montant <span class="field-required">*</span></label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-banknotes" class="field-icon" />
              <input v-model="form.amount" type="number" step="0.01" min="0" placeholder="0.00" class="field-input" inputmode="decimal" required />
            </div>
            <p v-if="getErrorForField(formErrors, 'amount')" class="field-err">{{ getErrorForField(formErrors, 'amount') }}</p>
          </div>

          <!-- Catégorie -->
          <div class="field-group">
            <label class="field-label">Catégorie</label>
            <USelectMenu
              v-model="form.category"
              :options="[{ id: '', name: 'Aucune catégorie' }, ...availableCategories]"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner une catégorie"
              size="lg"
            />
            <p v-if="getErrorForField(formErrors, 'category')" class="field-err">{{ getErrorForField(formErrors, 'category') }}</p>
          </div>

          <!-- Date de fin -->
          <div class="field-group">
            <label class="field-label">Date de fin (optionnelle)</label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-calendar-days" class="field-icon" />
              <input v-model="form.recurrence_end_date" type="date" class="field-input" />
            </div>
            <p v-if="getErrorForField(formErrors, 'recurrence_end_date')" class="field-err">{{ getErrorForField(formErrors, 'recurrence_end_date') }}</p>
          </div>

          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button type="button" class="ds-btn ds-btn-ghost" @click="closeEditModal">Annuler</button>
            <button type="submit" class="ds-btn ds-btn-primary" :disabled="submitting">
              <span v-if="submitting" class="btn-spinner" />
              <span v-else>Mettre à jour la série</span>
            </button>
          </div>
        </form>
      </div>
    </UModal>

    <!-- ── Floating bulk bar ─────────────────────────────────────── -->
    <Transition name="bulk">
      <div v-if="someSelected" class="series-bulk-bar">
        <span style="font-size:13px;font-weight:500;">
          {{ selectedIds.size }} série{{ selectedIds.size > 1 ? 's' : '' }} sélectionnée{{ selectedIds.size > 1 ? 's' : '' }}
        </span>
        <span class="series-bulk-sep" />
        <button class="series-bulk-btn series-bulk-btn--danger" @click="showConfirmBulkDelete = true">
          <UIcon name="i-heroicons-trash" style="width:14px;height:14px;" />
          Supprimer
        </button>
        <button class="series-bulk-close" @click="clearSelection">
          <UIcon name="i-heroicons-x-mark" style="width:12px;height:12px;" />
        </button>
      </div>
    </Transition>

    <!-- ── Confirm Delete Modal (unitaire) ──────────────────────── -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer la série récurrente"
      :message="`Supprimer le template de la série « ${seriesToDelete?.description || 'Sans description'} » ? Les occurrences déjà générées resteront dans vos transactions.`"
      confirm-label="Supprimer"
      :loading="deleting"
      @confirm="executeDelete"
    />

    <!-- ── Confirm Bulk Delete Modal ─────────────────────────────── -->
    <ConfirmModal
      v-model="showConfirmBulkDelete"
      title="Supprimer les séries sélectionnées"
      :message="`Supprimer ${selectedIds.size} série(s) récurrente(s) ? Les occurrences déjà générées resteront dans vos transactions. Cette action est irréversible.`"
      confirm-label="Tout supprimer"
      confirm-color="red"
      icon="i-heroicons-trash"
      :loading="bulkDeleting"
      @confirm="executeBulkDelete"
    />

  </div>
</template>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp .4s cubic-bezier(.2,.7,.2,1) both; }

@keyframes spin {
  to { transform: rotate(360deg); }
}
.spin { animation: spin 0.7s linear infinite; }

/* ── Root ── */
.page-root {
  padding: 16px 16px 80px;
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
@media (min-width: 640px) {
  .page-root { padding: 20px 24px 40px; gap: 18px; }
}

/* ── Series list ── */
.series-list { display: flex; flex-direction: column; gap: 10px; }

/* ── Series card ── */
.series-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.series-card:hover {
  border-color: var(--line-strong);
  box-shadow: var(--shadow-md);
}
@media (min-width: 640px) {
  .series-card { padding: 16px 20px; gap: 14px; }
}

/* Icône */
.series-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius);
  display: grid;
  place-items: center;
  flex-shrink: 0;
  margin-top: 2px;
}

/* Corps */
.series-body { flex: 1; min-width: 0; }
.series-desc {
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.series-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--ink-3);
  margin-top: 3px;
}
.series-account { color: var(--ink-3); }
.series-dot { color: var(--ink-4); }
.series-details {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.series-category {
  font-size: 11.5px;
  color: var(--ink-3);
  padding: 1px 7px;
  border-radius: var(--radius-sm);
  background: var(--surface-2);
  border: 1px solid var(--line);
}
.series-next {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  color: var(--ink-3);
  margin-top: 6px;
}
.series-total { color: var(--ink-4); }

/* Partie droite */
.series-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}
.series-amount {
  font-size: 15px;
  font-weight: 500;
  letter-spacing: -0.3px;
  white-space: nowrap;
}
.series-actions { display: flex; gap: 4px; }

/* ── Checkbox ── */
.series-checkbox {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}
.series-checkbox-box {
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
.series-checkbox-box.checked {
  border-color: var(--accent);
  background: var(--accent);
}

/* ── Selected card state ── */
.series-card--selected {
  background: var(--accent-soft);
}
.series-card--selected:hover {
  background: var(--accent-soft);
}

/* ── Floating bulk bar ── */
.series-bulk-bar {
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
.series-bulk-sep {
  width: 1px;
  height: 18px;
  background: rgba(255,255,255,0.15);
  margin: 0 4px;
  flex-shrink: 0;
}
.series-bulk-btn {
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
.series-bulk-btn:hover { background: rgba(255,255,255,0.1); }
.series-bulk-btn--danger { color: #fca5a5; }
.series-bulk-close {
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
.series-bulk-close:hover { background: rgba(255,255,255,0.18); }

/* Transition floating bar */
.bulk-enter-active, .bulk-leave-active { transition: all 0.25s cubic-bezier(.2,.7,.2,1); }
.bulk-enter-from, .bulk-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }

/* Type selector buttons */
.type-btn {
  flex: 1;
  height: 36px;
  border-radius: var(--radius);
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--ink-3);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.12s;
}
.type-btn:hover { background: var(--surface-2); color: var(--ink-2); }
.type-btn.active {
  background: var(--accent-soft);
  border-color: var(--accent);
  color: var(--accent);
}

/* Danger icon button variant */
.ds-btn-icon--danger {
  color: var(--danger) !important;
}
.ds-btn-icon--danger:hover {
  background: var(--danger-soft) !important;
  border-color: color-mix(in oklab, var(--danger) 25%, transparent) !important;
}

/* ── Skeleton ── */
.skeleton-card { pointer-events: none; }
.skeleton-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius);
  background: var(--surface-2);
  animation: pulse 1.5s ease-in-out infinite;
  flex-shrink: 0;
}
.skeleton-line {
  background: var(--surface-2);
  border-radius: 4px;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: .4; }
}
</style>
