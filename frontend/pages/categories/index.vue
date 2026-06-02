<script setup lang="ts">
import type { Category } from '~/types'
import type { StandardError } from '~/types/errors'

definePageMeta({
  middleware: 'auth'
})

const { getCategories, createCategory, updateCategory, deleteCategory } = useCategories()
const { getErrorForField, formatForToast } = useErrorHandler()
const toast = useToast()

// State
const categories = ref<Category[]>([])
const loading = ref(false)
const showModal = ref(false)
const editingCategory = ref<Category | null>(null)
const formErrors = ref<StandardError | null>(null)

// Filters
const filterType = ref<'' | 'income' | 'expense'>('')

// Form
const form = ref({
  name: '',
  type: 'expense' as 'income' | 'expense',
  icon: 'i-heroicons-tag',
  color: 'blue'
})

// Computed
const filteredCategories = computed(() => {
  if (!filterType.value) return categories.value
  return categories.value.filter(c => c.type === filterType.value)
})

const incomeCategories = computed(() => categories.value.filter(c => c.type === 'income'))
const expenseCategories = computed(() => categories.value.filter(c => c.type === 'expense'))

/**
 * Map des couleurs Tailwind vers des valeurs CSS utilisables dans les styles inline.
 * Nécessaire car les classes Tailwind dynamiques (bg-${color}-100) ne sont pas
 * incluses dans le build si elles ne sont pas référencées statiquement.
 */
const COLOR_MAP: Record<string, { bg: string; text: string; border: string }> = {
  red:    { bg: '#fee2e2', text: '#dc2626', border: 'rgba(220,38,38,0.25)' },
  orange: { bg: '#ffedd5', text: '#ea580c', border: 'rgba(234,88,12,0.25)' },
  yellow: { bg: '#fef9c3', text: '#ca8a04', border: 'rgba(202,138,4,0.25)' },
  green:  { bg: '#dcfce7', text: '#16a34a', border: 'rgba(22,163,74,0.25)' },
  blue:   { bg: '#dbeafe', text: '#2563eb', border: 'rgba(37,99,235,0.25)' },
  indigo: { bg: '#e0e7ff', text: '#4338ca', border: 'rgba(67,56,202,0.25)' },
  purple: { bg: '#f3e8ff', text: '#9333ea', border: 'rgba(147,51,234,0.25)' },
  pink:   { bg: '#fce7f3', text: '#db2777', border: 'rgba(219,39,119,0.25)' },
  gray:   { bg: '#f1f5f9', text: '#64748b', border: 'rgba(100,116,139,0.25)' },
}

/** Retourne les tokens CSS d'une couleur nommée, avec fallback sur gray. */
const getColorTokens = (color: string) => COLOR_MAP[color] ?? COLOR_MAP.gray

// Icons disponibles
const availableIcons = [
  { value: 'i-heroicons-home', label: 'Maison' },
  { value: 'i-heroicons-shopping-cart', label: 'Courses' },
  { value: 'i-heroicons-currency-dollar', label: 'Argent' },
  { value: 'i-heroicons-truck', label: 'Transport' },
  { value: 'i-heroicons-heart', label: 'Santé' },
  { value: 'i-heroicons-academic-cap', label: 'Éducation' },
  { value: 'i-heroicons-film', label: 'Loisirs' },
  { value: 'i-heroicons-wifi', label: 'Internet' },
  { value: 'i-heroicons-device-phone-mobile', label: 'Mobile' },
  { value: 'i-heroicons-light-bulb', label: 'Électricité' },
  { value: 'i-heroicons-fire', label: 'Chauffage' },
  { value: 'i-heroicons-banknotes', label: 'Salaire' },
  { value: 'i-heroicons-gift', label: 'Cadeaux' },
  { value: 'i-heroicons-building-office', label: 'Bureau' },
  { value: 'i-heroicons-wrench-screwdriver', label: 'Réparations' },
  { value: 'i-heroicons-tag', label: 'Tag' }
]

// Couleurs disponibles
const availableColors = [
  { value: 'red', label: 'Rouge' },
  { value: 'orange', label: 'Orange' },
  { value: 'yellow', label: 'Jaune' },
  { value: 'green', label: 'Vert' },
  { value: 'blue', label: 'Bleu' },
  { value: 'indigo', label: 'Indigo' },
  { value: 'purple', label: 'Violet' },
  { value: 'pink', label: 'Rose' },
  { value: 'gray', label: 'Gris' }
]

// Methods
const fetchCategories = async () => {
  loading.value = true
  const result = await getCategories()
  if (result.success && result.data) {
    categories.value = result.data.results
  }
  loading.value = false
}

const openModal = (category?: Category) => {
  if (category) {
    editingCategory.value = category
    form.value = {
      name: category.name,
      type: category.type,
      icon: category.icon,
      color: category.color
    }
  } else {
    editingCategory.value = null
    form.value = {
      name: '',
      type: 'expense',
      icon: 'i-heroicons-tag',
      color: 'blue'
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingCategory.value = null
  formErrors.value = null
}

const handleSubmit = async () => {
  loading.value = true
  formErrors.value = null

  const categoryData = {
    name: form.value.name,
    type: form.value.type,
    icon: form.value.icon,
    color: form.value.color
  }

  let result
  if (editingCategory.value) {
    result = await updateCategory(editingCategory.value.id, categoryData)
  } else {
    result = await createCategory(categoryData)
  }

  loading.value = false

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: editingCategory.value ? 'Catégorie mise à jour' : 'Catégorie créée',
      color: 'green'
    })
    closeModal()
    await fetchCategories()
  } else if (result.error) {
    formErrors.value = result.error
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
const categoryToDelete = ref<Category | null>(null)

const handleDelete = (category: Category) => {
  categoryToDelete.value = category
  showConfirmDelete.value = true
}

const executeDelete = async () => {
  if (!categoryToDelete.value) return

  loading.value = true
  const result = await deleteCategory(categoryToDelete.value.id)
  loading.value = false
  categoryToDelete.value = null

  if (result.success) {
    toast.add({
      title: 'Succès',
      description: 'Catégorie supprimée',
      color: 'green'
    })
    await fetchCategories()
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Impossible de supprimer la catégorie (elle est peut-être utilisée)',
      color: 'red'
    })
  }
}

// Lifecycle
onMounted(() => {
  fetchCategories()
})
</script>

<template>
  <div class="page-root fade-up">

    <!-- ── Header ──────────────────────────────────────────────── -->
    <PageHeader
      title="Catégories"
      :subtitle="`${categories.length} catégorie(s) · ${incomeCategories.length} revenus · ${expenseCategories.length} dépenses`"
    >
      <template #actions>
        <button class="ds-btn ds-btn-primary" @click="openModal()">
          <UIcon name="i-heroicons-plus" style="width:14px;height:14px;" />
          <span class="hidden sm:inline">Nouvelle catégorie</span>
          <span class="sm:hidden">Ajouter</span>
        </button>
      </template>
    </PageHeader>

    <!-- ── Filter tabs ──────────────────────────────────────────── -->
    <div class="filter-tabs">
      <button
        class="filter-tab"
        :class="{ 'filter-tab--active': filterType === '' }"
        @click="filterType = ''"
      >
        Toutes
        <span class="filter-count">{{ categories.length }}</span>
      </button>
      <button
        class="filter-tab filter-tab--income"
        :class="{ 'filter-tab--income-active': filterType === 'income' }"
        @click="filterType = 'income'"
      >
        Revenus
        <span class="filter-count">{{ incomeCategories.length }}</span>
      </button>
      <button
        class="filter-tab filter-tab--expense"
        :class="{ 'filter-tab--expense-active': filterType === 'expense' }"
        @click="filterType = 'expense'"
      >
        Dépenses
        <span class="filter-count">{{ expenseCategories.length }}</span>
      </button>
    </div>

    <!-- ── Loading ─────────────────────────────────────────────── -->
    <div v-if="loading && categories.length === 0" class="cat-grid">
      <div v-for="i in 8" :key="i" class="cat-card skeleton-card">
        <div class="skeleton-icon" />
        <div style="flex:1;">
          <div class="skeleton-line" style="width:70%;height:14px;" />
          <div class="skeleton-line" style="width:40%;height:11px;margin-top:6px;" />
        </div>
      </div>
    </div>

    <!-- ── Empty state ─────────────────────────────────────────── -->
    <div v-else-if="filteredCategories.length === 0 && !loading" class="section-card empty-section">
      <UIcon name="i-heroicons-tag" style="width:40px;height:40px;color:var(--ink-4);" />
      <p style="font-size:14px;font-weight:500;color:var(--ink-2);margin:8px 0 0;">Aucune catégorie</p>
      <p style="font-size:13px;color:var(--ink-3);margin:4px 0 0;">Commencez par créer votre première catégorie</p>
      <button class="ds-btn ds-btn-primary" style="margin-top:16px;" @click="openModal()">
        <UIcon name="i-heroicons-plus" style="width:14px;height:14px;" />
        Nouvelle catégorie
      </button>
    </div>

    <!-- ── 2 sections : Dépenses / Revenus ────────────────────── -->
    <template v-else>

      <!-- Section Dépenses -->
      <div v-if="filterType === '' || filterType === 'expense'" class="section-card">
        <div class="section-header">
          <div>
            <div class="section-title">
              <span class="section-dot section-dot--expense" />
              Dépenses
            </div>
            <div class="section-sub">{{ expenseCategories.length }} catégorie(s)</div>
          </div>
        </div>

        <div v-if="expenseCategories.length === 0" class="section-empty">
          Aucune catégorie de dépense
        </div>
        <div v-else class="cat-grid">
          <div
            v-for="category in expenseCategories"
            :key="category.id"
            class="cat-card"
          >
            <!-- Icône colorée -->
            <div
              class="cat-icon"
              :style="{
                background: getColorTokens(category.color).bg,
                color: getColorTokens(category.color).text,
                border: `1px solid ${getColorTokens(category.color).border}`,
              }"
            >
              <UIcon :name="category.icon" style="width:18px;height:18px;" />
            </div>
            <!-- Nom + type -->
            <div class="cat-info">
              <div class="cat-name">{{ category.name }}</div>
              <span class="ds-badge ds-badge-danger" style="font-size:10px;">Dépense</span>
            </div>
            <!-- Actions -->
            <div class="cat-actions">
              <button
                class="ds-btn-icon"
                aria-label="Modifier la catégorie"
                @click="openModal(category)"
              >
                <UIcon name="i-heroicons-pencil" style="width:13px;height:13px;" />
              </button>
              <button
                class="ds-btn-icon ds-btn-icon--danger"
                aria-label="Supprimer la catégorie"
                @click="handleDelete(category)"
              >
                <UIcon name="i-heroicons-trash" style="width:13px;height:13px;" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Section Revenus -->
      <div v-if="filterType === '' || filterType === 'income'" class="section-card">
        <div class="section-header">
          <div>
            <div class="section-title">
              <span class="section-dot section-dot--income" />
              Revenus
            </div>
            <div class="section-sub">{{ incomeCategories.length }} catégorie(s)</div>
          </div>
        </div>

        <div v-if="incomeCategories.length === 0" class="section-empty">
          Aucune catégorie de revenu
        </div>
        <div v-else class="cat-grid">
          <div
            v-for="category in incomeCategories"
            :key="category.id"
            class="cat-card"
          >
            <div
              class="cat-icon"
              :style="{
                background: getColorTokens(category.color).bg,
                color: getColorTokens(category.color).text,
                border: `1px solid ${getColorTokens(category.color).border}`,
              }"
            >
              <UIcon :name="category.icon" style="width:18px;height:18px;" />
            </div>
            <div class="cat-info">
              <div class="cat-name">{{ category.name }}</div>
              <span class="ds-badge ds-badge-success" style="font-size:10px;">Revenu</span>
            </div>
            <div class="cat-actions">
              <button
                class="ds-btn-icon"
                aria-label="Modifier la catégorie"
                @click="openModal(category)"
              >
                <UIcon name="i-heroicons-pencil" style="width:13px;height:13px;" />
              </button>
              <button
                class="ds-btn-icon ds-btn-icon--danger"
                aria-label="Supprimer la catégorie"
                @click="handleDelete(category)"
              >
                <UIcon name="i-heroicons-trash" style="width:13px;height:13px;" />
              </button>
            </div>
          </div>
        </div>
      </div>

    </template>

    <!-- ── Confirm Delete Modal ────────────────────────────────── -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer la catégorie"
      :message="`Êtes-vous sûr de vouloir supprimer la catégorie « ${categoryToDelete?.name} » ? Elle est peut-être utilisée par des transactions.`"
      confirm-label="Supprimer"
      @confirm="executeDelete"
    />

    <!-- ── Category Modal ─────────────────────────────────────── -->
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
            <UIcon :name="editingCategory ? 'i-heroicons-pencil' : 'i-heroicons-tag'" style="width:16px;height:16px;" />
          </div>
          <h3 class="modal-title">{{ editingCategory ? 'Modifier la catégorie' : 'Nouvelle catégorie' }}</h3>
          <button class="modal-close" type="button" @click="closeModal">
            <UIcon name="i-heroicons-x-mark" style="width:18px;height:18px;" />
          </button>
        </div>
        <form class="modal-body" @submit.prevent="handleSubmit">

          <!-- Nom -->
          <div class="field-group">
            <label class="field-label">Nom <span class="field-required">*</span></label>
            <div class="field-wrap">
              <UIcon name="i-heroicons-tag" class="field-icon" />
              <input v-model="form.name" type="text" placeholder="Ex: Alimentation" class="field-input" inputmode="text" required />
            </div>
            <p v-if="getErrorForField(formErrors, 'name')" class="field-err">{{ getErrorForField(formErrors, 'name') }}</p>
          </div>

          <!-- Type -->
          <div class="field-group">
            <label class="field-label">Type <span class="field-required">*</span></label>
            <USelectMenu
              v-model="form.type"
              :options="[{ label: 'Dépense', value: 'expense' }, { label: 'Revenu', value: 'income' }]"
              option-attribute="label"
              value-attribute="value"
              size="lg"
            />
            <p v-if="getErrorForField(formErrors, 'category_type')" class="field-err">{{ getErrorForField(formErrors, 'category_type') }}</p>
          </div>

          <!-- Icône -->
          <div class="field-group">
            <label class="field-label">Icône</label>
            <USelectMenu
              v-model="form.icon"
              :options="availableIcons"
              option-attribute="label"
              value-attribute="value"
              size="lg"
            >
              <template #label>
                <div style="display:flex;align-items:center;gap:8px;">
                  <UIcon :name="form.icon" style="width:16px;height:16px;" />
                  <span>{{ availableIcons.find(i => i.value === form.icon)?.label }}</span>
                </div>
              </template>
              <template #option="{ option }">
                <div style="display:flex;align-items:center;gap:8px;">
                  <UIcon :name="option.value" style="width:16px;height:16px;" />
                  <span>{{ option.label }}</span>
                </div>
              </template>
            </USelectMenu>
          </div>

          <!-- Couleur -->
          <div class="field-group">
            <label class="field-label">Couleur</label>
            <div class="color-picker">
              <button
                v-for="colorOption in availableColors"
                :key="colorOption.value"
                type="button"
                class="color-swatch"
                :title="colorOption.label"
                :style="{
                  background: getColorTokens(colorOption.value).bg,
                  border: form.color === colorOption.value
                    ? `2px solid ${getColorTokens(colorOption.value).text}`
                    : `2px solid transparent`,
                  outline: form.color === colorOption.value
                    ? `2px solid ${getColorTokens(colorOption.value).text}`
                    : 'none',
                  outlineOffset: '2px',
                }"
                @click="form.color = colorOption.value"
              >
                <span class="color-dot" :style="{ background: getColorTokens(colorOption.value).text }" />
                <span class="color-label">{{ colorOption.label }}</span>
              </button>
            </div>
          </div>

          <!-- Aperçu -->
          <div class="cat-preview">
            <div
              class="cat-preview-icon"
              :style="{
                background: getColorTokens(form.color).bg,
                color: getColorTokens(form.color).text,
                border: `1px solid ${getColorTokens(form.color).border}`,
              }"
            >
              <UIcon :name="form.icon" style="width:20px;height:20px;" />
            </div>
            <div>
              <div style="font-size:14px;font-weight:500;color:var(--ink);">
                {{ form.name || 'Nom de la catégorie' }}
              </div>
              <span
                class="ds-badge"
                :class="form.type === 'income' ? 'ds-badge-success' : 'ds-badge-danger'"
                style="font-size:10px;margin-top:4px;"
              >
                {{ form.type === 'income' ? 'Revenu' : 'Dépense' }}
              </span>
            </div>
          </div>

          <div class="modal-footer" style="padding:0;border:none;margin-top:4px;">
            <button type="button" class="ds-btn ds-btn-ghost" @click="closeModal">Annuler</button>
            <button type="submit" class="ds-btn ds-btn-primary" :disabled="loading">
              <span v-if="loading" class="btn-spinner" />
              <span v-else>{{ editingCategory ? 'Mettre à jour' : 'Créer' }}</span>
            </button>
          </div>
        </form>
      </div>
    </UModal>

  </div>
</template>

<style scoped>
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp .4s cubic-bezier(.2,.7,.2,1) both; }

/* ── Root ── */
.page-root {
  padding: 16px 16px 80px;
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
@media (min-width: 640px) {
  .page-root { padding: 20px 24px 40px; gap: 18px; }
}

/* ── Filter tabs ── */
.filter-tabs {
  display: flex;
  gap: 6px;
  padding: 4px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  width: fit-content;
}
.filter-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border-radius: var(--radius);
  font-size: 13px;
  font-weight: 500;
  color: var(--ink-3);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.filter-tab:hover { background: var(--surface-2); color: var(--ink-2); }
.filter-tab--active {
  background: var(--accent);
  color: #fff !important;
}
.filter-tab--income-active {
  background: var(--success-soft);
  color: var(--success) !important;
}
.filter-tab--expense-active {
  background: var(--danger-soft);
  color: var(--danger) !important;
}
.filter-count {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 99px;
  background: rgba(0,0,0,0.08);
  line-height: 1.4;
}
.filter-tab--active .filter-count { background: rgba(255,255,255,0.25); }

/* ── Section card ── */
.section-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: var(--shadow-sm);
}
@media (min-width: 640px) { .section-card { padding: 20px 24px; } }

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.2px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-sub { font-size: 12.5px; color: var(--ink-3); margin-top: 2px; }
.section-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  flex-shrink: 0;
}
.section-dot--expense { background: var(--danger); }
.section-dot--income  { background: var(--success); }
.section-empty {
  font-size: 13px;
  color: var(--ink-4);
  text-align: center;
  padding: 20px 0;
}

/* ── Empty section (full page) ── */
.empty-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px;
  text-align: center;
}

/* ── Category grid ── */
.cat-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}
@media (min-width: 480px) {
  .cat-grid { grid-template-columns: 1fr 1fr; }
}
@media (min-width: 768px) {
  .cat-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 1024px) {
  .cat-grid { grid-template-columns: repeat(4, 1fr); }
}

/* ── Category card ── */
.cat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  transition: border-color 0.12s, box-shadow 0.12s;
}
.cat-card:hover {
  border-color: var(--line-strong);
  box-shadow: var(--shadow-sm);
}

.cat-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.cat-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.cat-name {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cat-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
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
  width: 36px;
  height: 36px;
  border-radius: var(--radius);
  background: var(--surface-2);
  border: 1px solid var(--line);
  animation: pulse 1.5s ease-in-out infinite;
  flex-shrink: 0;
}
.skeleton-line {
  background: var(--line);
  border-radius: 4px;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: .4; }
}

/* ── Color picker (dans le modal) ── */
.color-picker {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}
.color-swatch {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: var(--radius);
  cursor: pointer;
  transition: opacity 0.12s;
}
.color-swatch:hover { opacity: 0.85; }
.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
}
.color-label { font-size: 12.5px; font-weight: 500; }

/* ── Preview (dans le modal) ── */
.cat-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
}
.cat-preview-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius);
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
</style>
