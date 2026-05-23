<script setup lang="ts">
import type { RecurringSeries } from '~/types'
import type { StandardError } from '~/types/errors'

definePageMeta({
  middleware: 'auth'
})

const { getRecurringSeries, updateSeries, deleteSeries } = useRecurring()
const { getAccounts } = useAccounts()
const { getCategories } = useCategories()
const { getErrorForField, formatForToast } = useErrorHandler()
const { ensureProfileLoaded } = useUserProfile()
const toast = useToast()

// ─── State ───────────────────────────────────────────────────────────────────

const series = ref<RecurringSeries[]>([])
const loading = ref(false)
const loadError = ref(false)

// Modal d'édition d'une série
const showEditModal = ref(false)
const editingSeries = ref<RecurringSeries | null>(null)
const formErrors = ref<StandardError | null>(null)
const submitting = ref(false)

// Modal de confirmation de suppression
const showConfirmDelete = ref(false)
const seriesToDelete = ref<RecurringSeries | null>(null)
const deleting = ref(false)

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
 * Couleur Tailwind selon le type de transaction.
 */
const typeColor = (type: string): string => {
  switch (type) {
    case 'income':   return 'green'
    case 'expense':  return 'red'
    case 'transfer': return 'blue'
    default:         return 'gray'
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
  <div class="container mx-auto px-4 py-6 sm:py-8">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6 sm:mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold">Transactions récurrentes</h1>
      <UButton
        icon="i-heroicons-arrow-path"
        size="lg"
        color="gray"
        variant="outline"
        class="sm:hidden"
        aria-label="Rafraîchir"
        :loading="loading"
        @click="fetchSeries()"
      />
      <UButton
        icon="i-heroicons-arrow-path"
        size="lg"
        color="gray"
        variant="outline"
        class="hidden sm:inline-flex"
        :loading="loading"
        @click="fetchSeries()"
      >
        Rafraîchir
      </UButton>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-3">
      <UCard v-for="i in 4" :key="i" class="animate-pulse">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-full bg-gray-200 dark:bg-gray-700 flex-shrink-0" />
          <div class="flex-1 space-y-2">
            <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48" />
            <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-32" />
          </div>
          <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-24" />
        </div>
      </UCard>
    </div>

    <!-- Error -->
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

    <!-- Empty -->
    <div v-else-if="series.length === 0">
      <EmptyState
        icon="i-heroicons-arrow-path"
        color="purple"
        title="Aucune série récurrente"
        description="Créez une transaction récurrente depuis la page Transactions pour qu'elle apparaisse ici."
      />
    </div>

    <!-- Cards mobile / Table desktop -->
    <template v-else>
      <!-- Mobile cards -->
      <div class="sm:hidden space-y-3">
        <UCard
          v-for="s in series"
          :key="s.id"
          class="transition-shadow hover:shadow-md"
        >
          <div class="flex items-start gap-3">
            <!-- Icône fréquence -->
            <div
              class="flex-shrink-0 w-11 h-11 rounded-full flex items-center justify-center mt-0.5"
              :class="`bg-${typeColor(s.type)}-100 dark:bg-${typeColor(s.type)}-900/30`"
            >
              <UIcon
                :name="frequencyIcon(s.recurrence_frequency)"
                :class="`text-${typeColor(s.type)}-600 text-lg`"
              />
            </div>

            <div class="flex-1 min-w-0">
              <div class="font-semibold text-sm truncate">{{ s.description || '(sans description)' }}</div>
              <div class="text-xs text-gray-500 mt-0.5">
                {{ s.account.name }} · {{ frequencyLabel(s.recurrence_frequency, s.recurrence_interval) }}
              </div>
              <div class="flex flex-wrap items-center gap-2 mt-2">
                <UBadge :color="typeColor(s.type)" variant="soft" size="xs">
                  {{ s.type === 'income' ? 'Revenu' : s.type === 'expense' ? 'Dépense' : 'Transfert' }}
                </UBadge>
                <span class="text-sm font-bold" :class="`text-${typeColor(s.type)}-600`">
                  {{ s.type === 'expense' ? '-' : '+' }}{{ s.amount }} {{ s.account.currency }}
                </span>
              </div>
              <div v-if="s.next_occurrence" class="text-xs text-gray-400 mt-1">
                <UIcon name="i-heroicons-calendar" class="inline mr-1" />
                Prochaine : {{ formatDate(s.next_occurrence) }}
              </div>
              <div v-else class="text-xs text-gray-400 mt-1">Aucune occurrence future</div>
              <div class="text-xs text-gray-400">{{ s.total_instances }} occurrence(s) générée(s)</div>
            </div>

            <div class="flex flex-col gap-1 flex-shrink-0">
              <UButton
                icon="i-heroicons-pencil"
                size="xs"
                color="gray"
                variant="ghost"
                class="min-h-[40px] min-w-[40px]"
                aria-label="Modifier la série"
                @click="openEditModal(s)"
              />
              <UButton
                icon="i-heroicons-trash"
                size="xs"
                color="red"
                variant="ghost"
                class="min-h-[40px] min-w-[40px]"
                aria-label="Supprimer la série"
                @click="handleDeleteClick(s)"
              />
            </div>
          </div>
        </UCard>
      </div>

      <!-- Desktop table -->
      <UCard class="hidden sm:block">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700">
              <th class="text-left py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">Description</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">Fréquence</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">Compte</th>
              <th class="text-right py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">Montant</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">Prochaine</th>
              <th class="text-center py-3 px-4 font-semibold text-gray-600 dark:text-gray-400">Occurrences</th>
              <th class="py-3 px-4" />
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr
              v-for="s in series"
              :key="s.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <td class="py-3 px-4">
                <div class="flex items-center gap-3">
                  <div
                    class="w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center"
                    :class="`bg-${typeColor(s.type)}-100 dark:bg-${typeColor(s.type)}-900/30`"
                  >
                    <UIcon
                      :name="frequencyIcon(s.recurrence_frequency)"
                      :class="`text-${typeColor(s.type)}-600`"
                    />
                  </div>
                  <div>
                    <div class="font-medium">{{ s.description || '(sans description)' }}</div>
                    <div v-if="s.category" class="text-xs text-gray-400">{{ s.category.name }}</div>
                  </div>
                </div>
              </td>
              <td class="py-3 px-4 text-gray-600 dark:text-gray-400">
                {{ frequencyLabel(s.recurrence_frequency, s.recurrence_interval) }}
              </td>
              <td class="py-3 px-4 text-gray-600 dark:text-gray-400">
                {{ s.account.name }}
              </td>
              <td class="py-3 px-4 text-right">
                <span class="font-semibold" :class="`text-${typeColor(s.type)}-600`">
                  {{ s.type === 'expense' ? '-' : '+' }}{{ s.amount }} {{ s.account.currency }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span v-if="s.next_occurrence" class="text-gray-700 dark:text-gray-300">
                  {{ formatDate(s.next_occurrence) }}
                </span>
                <span v-else class="text-gray-400 italic">Terminée</span>
              </td>
              <td class="py-3 px-4 text-center">
                <UBadge color="gray" variant="soft">{{ s.total_instances }}</UBadge>
              </td>
              <td class="py-3 px-4">
                <div class="flex items-center justify-end gap-1">
                  <UButton
                    icon="i-heroicons-pencil"
                    size="sm"
                    color="gray"
                    variant="ghost"
                    class="min-h-[40px] min-w-[40px]"
                    aria-label="Modifier la série"
                    @click="openEditModal(s)"
                  />
                  <UButton
                    icon="i-heroicons-trash"
                    size="sm"
                    color="red"
                    variant="ghost"
                    class="min-h-[40px] min-w-[40px]"
                    aria-label="Supprimer la série"
                    @click="handleDeleteClick(s)"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </UCard>
    </template>

    <!-- Edit Series Modal -->
    <UModal v-model="showEditModal" :ui="{ width: 'sm:max-w-lg' }">
      <UCard>
        <template #header>
          <div class="flex items-center gap-3">
            <UIcon name="i-heroicons-arrow-path" class="text-primary-500 text-xl" />
            <h3 class="text-lg font-semibold">Modifier la série</h3>
          </div>
        </template>

        <form class="space-y-4" @submit.prevent="handleUpdate">
          <!-- Info: les changements s'appliquent à toutes les occurrences futures -->
          <UAlert
            icon="i-heroicons-information-circle"
            color="blue"
            variant="soft"
            title="Modification de la série"
            description="Les changements s'appliqueront à toutes les occurrences futures de cette série."
          />

          <UFormGroup label="Description">
            <UInput
              v-model="form.description"
              size="lg"
              placeholder="Description de la transaction"
              inputmode="text"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'description')" />
          </UFormGroup>

          <UFormGroup label="Montant" required>
            <UInput
              v-model="form.amount"
              size="lg"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              inputmode="decimal"
              required
            />
            <FormFieldError :error="getErrorForField(formErrors, 'amount')" />
          </UFormGroup>

          <UFormGroup label="Catégorie">
            <USelectMenu
              v-model="form.category"
              :options="[{ id: '', name: 'Aucune catégorie' }, ...availableCategories]"
              option-attribute="name"
              value-attribute="id"
              placeholder="Sélectionner une catégorie"
            />
            <FormFieldError :error="getErrorForField(formErrors, 'category')" />
          </UFormGroup>

          <UFormGroup label="Date de fin (optionnelle)">
            <UInput v-model="form.recurrence_end_date" size="lg" type="date" />
            <FormFieldError :error="getErrorForField(formErrors, 'recurrence_end_date')" />
          </UFormGroup>

          <div class="flex justify-end gap-2 pt-2">
            <UButton color="gray" variant="ghost" @click="closeEditModal">
              Annuler
            </UButton>
            <UButton type="submit" :loading="submitting">
              Mettre à jour la série
            </UButton>
          </div>
        </form>
      </UCard>
    </UModal>

    <!-- Confirm Delete Modal -->
    <ConfirmModal
      v-model="showConfirmDelete"
      title="Supprimer la série récurrente"
      :message="`Supprimer le template de la série « ${seriesToDelete?.description || 'Sans description'} » ? Les occurrences déjà générées resteront dans vos transactions.`"
      confirm-label="Supprimer"
      :loading="deleting"
      @confirm="executeDelete"
    />
  </div>
</template>
