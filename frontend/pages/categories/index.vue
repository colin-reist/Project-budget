<script setup lang="ts">
import type { Category } from '~/types'

definePageMeta({
  middleware: 'auth'
})

const { getCategories, createCategory, updateCategory, deleteCategory } = useCategories()
const toast = useToast()

// State
const categories = ref<Category[]>([])
const loading = ref(false)
const showModal = ref(false)
const editingCategory = ref<Category | null>(null)

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
}

const handleSubmit = async () => {
  loading.value = true

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
  } else {
    toast.add({
      title: 'Erreur',
      description: 'Une erreur est survenue',
      color: 'red'
    })
  }
}

const handleDelete = async (category: Category) => {
  if (!confirm(`Êtes-vous sûr de vouloir supprimer la catégorie "${category.name}" ?`)) return

  loading.value = true
  const result = await deleteCategory(category.id)
  loading.value = false

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
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold">Catégories</h1>
      <UButton @click="openModal()" icon="i-heroicons-plus" size="lg">
        Nouvelle catégorie
      </UButton>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <UCard>
        <div class="text-sm text-gray-500">Total</div>
        <div class="text-2xl font-bold">{{ categories.length }}</div>
        <div class="text-xs text-gray-400">catégories</div>
      </UCard>
      <UCard>
        <div class="text-sm text-gray-500">Revenus</div>
        <div class="text-2xl font-bold text-green-600">{{ incomeCategories.length }}</div>
        <div class="text-xs text-gray-400">catégories</div>
      </UCard>
      <UCard>
        <div class="text-sm text-gray-500">Dépenses</div>
        <div class="text-2xl font-bold text-red-600">{{ expenseCategories.length }}</div>
        <div class="text-xs text-gray-400">catégories</div>
      </UCard>
    </div>

    <!-- Filter -->
    <UCard class="mb-6">
      <div class="flex gap-2">
        <UButton
          :color="filterType === '' ? 'primary' : 'gray'"
          variant="soft"
          @click="filterType = ''"
        >
          Toutes ({{ categories.length }})
        </UButton>
        <UButton
          :color="filterType === 'income' ? 'green' : 'gray'"
          variant="soft"
          @click="filterType = 'income'"
        >
          Revenus ({{ incomeCategories.length }})
        </UButton>
        <UButton
          :color="filterType === 'expense' ? 'red' : 'gray'"
          variant="soft"
          @click="filterType = 'expense'"
        >
          Dépenses ({{ expenseCategories.length }})
        </UButton>
      </div>
    </UCard>

    <!-- Categories Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <UCard
        v-for="category in filteredCategories"
        :key="category.id"
        class="hover:shadow-lg transition-shadow"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3 flex-1">
            <div
              class="w-12 h-12 rounded-full flex items-center justify-center"
              :class="`bg-${category.color}-100`"
            >
              <UIcon
                :name="category.icon"
                :class="`text-${category.color}-600 text-xl`"
              />
            </div>
            <div class="flex-1">
              <h3 class="font-semibold">{{ category.name }}</h3>
              <UBadge
                :color="category.type === 'income' ? 'green' : 'red'"
                variant="subtle"
                size="xs"
              >
                {{ category.type_display }}
              </UBadge>
            </div>
          </div>
        </div>

        <div class="flex gap-2 mt-4">
          <UButton
            size="sm"
            color="gray"
            variant="ghost"
            icon="i-heroicons-pencil"
            @click="openModal(category)"
          >
            Modifier
          </UButton>
          <UButton
            size="sm"
            color="red"
            variant="ghost"
            icon="i-heroicons-trash"
            @click="handleDelete(category)"
          >
            Supprimer
          </UButton>
        </div>
      </UCard>

      <UCard v-if="filteredCategories.length === 0 && !loading" class="col-span-full">
        <div class="text-center py-12">
          <UIcon name="i-heroicons-tag" class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-medium">Aucune catégorie</h3>
          <p class="mt-1 text-sm text-gray-500">
            Commencez par créer votre première catégorie
          </p>
          <div class="mt-6">
            <UButton @click="openModal()">
              Nouvelle catégorie
            </UButton>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Category Modal -->
    <UModal v-model="showModal" :ui="{ width: 'sm:max-w-lg' }">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">
            {{ editingCategory ? 'Modifier la catégorie' : 'Nouvelle catégorie' }}
          </h3>
        </template>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Name -->
          <UFormGroup label="Nom" required>
            <UInput
              v-model="form.name"
              placeholder="Ex: Alimentation"
              required
            />
          </UFormGroup>

          <!-- Type -->
          <UFormGroup label="Type" required>
            <USelectMenu
              v-model="form.type"
              :options="[
                { label: 'Revenu', value: 'income' },
                { label: 'Dépense', value: 'expense' }
              ]"
              option-attribute="label"
              value-attribute="value"
            />
          </UFormGroup>

          <!-- Icon -->
          <UFormGroup label="Icône">
            <USelectMenu
              v-model="form.icon"
              :options="availableIcons"
              option-attribute="label"
              value-attribute="value"
            >
              <template #label>
                <div class="flex items-center gap-2">
                  <UIcon :name="form.icon" class="text-lg" />
                  <span>{{ availableIcons.find(i => i.value === form.icon)?.label }}</span>
                </div>
              </template>
              <template #option="{ option }">
                <div class="flex items-center gap-2">
                  <UIcon :name="option.value" class="text-lg" />
                  <span>{{ option.label }}</span>
                </div>
              </template>
            </USelectMenu>
          </UFormGroup>

          <!-- Color -->
          <UFormGroup label="Couleur">
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="colorOption in availableColors"
                :key="colorOption.value"
                type="button"
                class="p-3 rounded-lg border-2 transition-all"
                :class="[
                  form.color === colorOption.value
                    ? `border-${colorOption.value}-500 bg-${colorOption.value}-50`
                    : 'border-gray-200 hover:border-gray-300'
                ]"
                @click="form.color = colorOption.value"
              >
                <div class="flex items-center gap-2">
                  <div
                    class="w-6 h-6 rounded-full"
                    :class="`bg-${colorOption.value}-500`"
                  ></div>
                  <span class="text-sm">{{ colorOption.label }}</span>
                </div>
              </button>
            </div>
          </UFormGroup>

          <!-- Preview -->
          <UFormGroup label="Aperçu">
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="flex items-center gap-3">
                <div
                  class="w-12 h-12 rounded-full flex items-center justify-center"
                  :class="`bg-${form.color}-100`"
                >
                  <UIcon
                    :name="form.icon"
                    :class="`text-${form.color}-600 text-xl`"
                  />
                </div>
                <div>
                  <div class="font-semibold">{{ form.name || 'Nom de la catégorie' }}</div>
                  <UBadge
                    :color="form.type === 'income' ? 'green' : 'red'"
                    variant="subtle"
                    size="xs"
                  >
                    {{ form.type === 'income' ? 'Revenu' : 'Dépense' }}
                  </UBadge>
                </div>
              </div>
            </div>
          </UFormGroup>

          <!-- Actions -->
          <div class="flex justify-end gap-2 pt-4">
            <UButton color="gray" variant="ghost" @click="closeModal">
              Annuler
            </UButton>
            <UButton type="submit" :loading="loading">
              {{ editingCategory ? 'Mettre à jour' : 'Créer' }}
            </UButton>
          </div>
        </form>
      </UCard>
    </UModal>
  </div>
</template>
