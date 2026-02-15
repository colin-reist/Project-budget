# 🛠️ Guide Développeur - Composants UX

> **Date:** 2026-02-14
> **Pour:** Développeurs travaillant sur Budget Tracker

---

## 📚 Table des Matières

1. [Composants Réutilisables](#composants-réutilisables)
2. [Composables](#composables)
3. [Patterns et Conventions](#patterns-et-conventions)
4. [Exemples d'Utilisation](#exemples-dutilisation)

---

## 🧩 Composants Réutilisables

### EmptyState.vue

**Localisation:** `frontend/components/EmptyState.vue`

**Usage:** Afficher un état vide engageant avec icône, titre, description et CTA.

**Props:**

| Prop | Type | Requis | Default | Description |
|------|------|--------|---------|-------------|
| `icon` | string | ✅ | - | Nom de l'icône Heroicons |
| `title` | string | ✅ | - | Titre principal |
| `description` | string | ✅ | - | Description motivante |
| `buttonText` | string | ❌ | - | Texte du bouton CTA |
| `buttonIcon` | string | ❌ | `'i-heroicons-plus'` | Icône du bouton |
| `color` | string | ❌ | `'primary'` | Couleur thème (primary, green, blue, purple, orange, red, gray) |

**Events:**

- `@action`: Émis quand le bouton est cliqué

**Exemple:**

```vue
<EmptyState
  icon="i-heroicons-banknotes"
  color="blue"
  title="Aucun compte trouvé"
  description="Créez votre premier compte pour commencer à suivre vos finances!"
  button-text="Créer un compte"
  @action="openAccountModal"
/>
```

**Avec slot personnalisé:**

```vue
<EmptyState
  icon="i-heroicons-chart-bar"
  color="green"
  title="Aucun budget"
  description="Configurez vos budgets mensuels"
>
  <template #action>
    <div class="flex gap-2">
      <UButton @click="createBudget">Créer</UButton>
      <UButton variant="outline" @click="importBudgets">Importer</UButton>
    </div>
  </template>
</EmptyState>
```

---

### SkeletonCard.vue

**Localisation:** `frontend/components/SkeletonCard.vue`

**Usage:** Afficher un placeholder pendant le chargement de données.

**Props:**

| Prop | Type | Requis | Default | Description |
|------|------|--------|---------|-------------|
| `lines` | number | ❌ | 3 | Nombre de lignes de contenu |
| `showHeader` | boolean | ❌ | true | Afficher le header (titre + badge) |
| `showFooter` | boolean | ❌ | false | Afficher le footer (boutons) |

**Exemple:**

```vue
<!-- Simple skeleton -->
<SkeletonCard :lines="4" />

<!-- Avec header et footer -->
<SkeletonCard :lines="5" show-header show-footer />

<!-- Grid de skeletons -->
<div class="grid grid-cols-3 gap-4">
  <SkeletonCard v-for="i in 6" :key="i" />
</div>
```

---

### OnboardingWizard.vue

**Localisation:** `frontend/components/OnboardingWizard.vue`

**Usage:** Guide interactif pour les nouveaux utilisateurs.

**Props:**

| Prop | Type | Requis | Description |
|------|------|--------|-------------|
| `modelValue` | boolean | ✅ | État ouvert/fermé du wizard (v-model) |

**Events:**

- `@update:modelValue`: Mise à jour de l'état
- `@complete`: Émis quand le wizard est terminé
- `@skip`: Émis quand l'utilisateur passe le wizard

**Exemple:**

```vue
<script setup>
const showOnboarding = ref(false)

const handleComplete = async () => {
  // Recharger les données
  await fetchData()
  toast.add({
    title: 'Bienvenue!',
    description: 'Configuration terminée',
    color: 'green'
  })
}
</script>

<template>
  <OnboardingWizard
    v-model="showOnboarding"
    @complete="handleComplete"
    @skip="handleComplete"
  />
</template>
```

**Détection automatique:**

```vue
<script setup>
// Afficher si premier utilisateur (pas de comptes ni catégories)
if (process.client && accounts.length === 0 && categories.length === 0) {
  const hasCompleted = localStorage.getItem('onboarding_completed')
  if (!hasCompleted) {
    showOnboarding.value = true
  }
}
</script>
```

---

### KeyboardShortcutHelp.vue

**Localisation:** `frontend/components/KeyboardShortcutHelp.vue`

**Usage:** Modal affichant tous les raccourcis clavier disponibles.

**Props:**

| Prop | Type | Requis | Description |
|------|------|--------|-------------|
| `modelValue` | boolean | ✅ | État ouvert/fermé (v-model) |

**Exemple:**

```vue
<script setup>
const showHelp = ref(false)
</script>

<template>
  <UButton @click="showHelp = true">
    Raccourcis
  </UButton>

  <KeyboardShortcutHelp v-model="showHelp" />
</template>
```

---

### FormHint.vue

**Localisation:** `frontend/components/FormHint.vue`

**Usage:** Note d'aide sous un champ de formulaire.

**Props:**

| Prop | Type | Requis | Default | Description |
|------|------|--------|---------|-------------|
| `icon` | string | ❌ | - | Icône Heroicons |
| `type` | string | ❌ | `'info'` | Type: info, warning, success |

**Exemple:**

```vue
<UFormGroup label="Revenu mensuel">
  <UInput v-model="income" type="number" />
  <FormHint icon="i-heroicons-information-circle">
    Saisissez votre revenu mensuel net après impôts
  </FormHint>
</UFormGroup>

<UFormGroup label="Budget alimentation">
  <UInput v-model="foodBudget" type="number" />
  <FormHint icon="i-heroicons-exclamation-triangle" type="warning">
    Ce montant ne devrait pas dépasser 30% de vos revenus
  </FormHint>
</UFormGroup>
```

---

## 🔧 Composables

### useKeyboardShortcuts

**Localisation:** `frontend/composables/useKeyboardShortcuts.ts`

**Usage:** Enregistrer et gérer des raccourcis clavier globaux.

**Méthodes:**

#### `registerShortcut(key, callback, options)`

Enregistre un nouveau raccourci.

**Paramètres:**

- `key` (string): Touche à surveiller (ex: 'n', 'k', 'Escape')
- `callback` (function): Fonction à exécuter
- `options` (object, optionnel):
  - `modifiers` (object): `{ ctrl: true, shift: true, alt: true, meta: true }`
  - `description` (string): Description du raccourci

**Retour:** void

#### `unregisterShortcut(key, modifiers)`

Supprime un raccourci.

**Paramètres:**

- `key` (string): Touche du raccourci
- `modifiers` (object, optionnel): Modificateurs

**Retour:** void

#### `getShortcutLabel(key, modifiers)`

Retourne le label formaté pour affichage.

**Paramètres:**

- `key` (string): Touche
- `modifiers` (object, optionnel): Modificateurs

**Retour:** string (ex: "⌘N" sur Mac, "Ctrl+N" sur Windows)

#### `cleanup()`

Nettoie tous les raccourcis. Appelé automatiquement au démontage.

**Retour:** void

---

**Exemple complet:**

```vue
<script setup>
const { registerShortcut, unregisterShortcut, getShortcutLabel } = useKeyboardShortcuts()
const showModal = ref(false)

// Label pour affichage
const shortcutLabel = computed(() => getShortcutLabel('n', { ctrl: true }))

onMounted(() => {
  // Ctrl+N pour ouvrir modal
  registerShortcut('n', () => {
    showModal.value = true
  }, {
    modifiers: { ctrl: true },
    description: 'Ouvrir la modal'
  })

  // Ctrl+K pour recherche
  registerShortcut('k', () => {
    openSearch()
  }, {
    modifiers: { ctrl: true },
    description: 'Ouvrir la recherche'
  })

  // ? pour aide
  registerShortcut('?', () => {
    showHelp.value = true
  }, {
    description: 'Afficher l\'aide'
  })
})

// Cleanup automatique au démontage (pas besoin d'appeler manuellement)
</script>

<template>
  <UButton @click="showModal = true">
    Nouveau
    <template #trailing>
      <UKbd>{{ shortcutLabel }}</UKbd>
    </template>
  </UButton>
</template>
```

**Comportement:**

- ✅ Ignore les raccourcis dans inputs/textareas/selects
- ✅ Support Mac (⌘) et Windows (Ctrl)
- ✅ Prevent default automatique
- ✅ Cleanup automatique

---

## 📐 Patterns et Conventions

### 1. Loading States

**Pattern:**

```vue
<script setup>
const loading = ref(true)
const data = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const result = await api.getData()
    data.value = result
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<template>
  <!-- Loading skeletons -->
  <div v-if="loading">
    <SkeletonCard v-for="i in 3" :key="i" />
  </div>

  <!-- Actual content -->
  <div v-else>
    <UCard v-for="item in data" :key="item.id">
      <!-- ... -->
    </UCard>
  </div>
</template>
```

---

### 2. Empty States

**Pattern:**

```vue
<template>
  <div v-if="loading">
    <SkeletonCard />
  </div>

  <div v-else-if="error">
    <EmptyState
      icon="i-heroicons-exclamation-circle"
      color="red"
      title="Erreur de chargement"
      description="Impossible de charger les données"
      button-text="Réessayer"
      @action="fetchData"
    />
  </div>

  <div v-else-if="data.length === 0">
    <EmptyState
      icon="i-heroicons-inbox"
      color="blue"
      title="Aucune donnée"
      description="Commencez par ajouter votre premier élément!"
      button-text="Ajouter"
      @action="openModal"
    />
  </div>

  <div v-else>
    <!-- Actual content -->
  </div>
</template>
```

---

### 3. Tooltips sur Données Projetées

**Pattern:**

```vue
<template>
  <div class="flex items-baseline gap-2">
    <!-- Valeur actuelle -->
    <span class="text-2xl font-bold">
      {{ formatCurrency(currentAmount) }}
    </span>

    <!-- Valeur projetée (si différente) -->
    <UTooltip
      v-if="projectedAmount !== currentAmount"
      text="Montant projeté incluant vos transactions futures planifiées"
    >
      <span class="text-sm text-blue-600 dark:text-blue-400 cursor-help">
        ({{ formatCurrency(projectedAmount) }})
      </span>
    </UTooltip>
  </div>
</template>
```

---

### 4. Validation Temps Réel

**Pattern:**

```vue
<script setup>
const form = ref({ amount: '', email: '' })
const errors = ref({})

const validateAmount = () => {
  const amount = parseFloat(form.value.amount)
  if (!form.value.amount) {
    errors.value.amount = 'Le montant est requis'
  } else if (isNaN(amount) || amount <= 0) {
    errors.value.amount = 'Le montant doit être supérieur à 0'
  } else {
    errors.value.amount = ''
  }
}

const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.value.email) {
    errors.value.email = 'L\'email est requis'
  } else if (!emailRegex.test(form.value.email)) {
    errors.value.email = 'Email invalide'
  } else {
    errors.value.email = ''
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <UFormGroup label="Montant" required :error="errors.amount">
      <UInput
        v-model="form.amount"
        type="number"
        @blur="validateAmount"
        @input="errors.amount = ''"
      />
    </UFormGroup>

    <UFormGroup label="Email" required :error="errors.email">
      <UInput
        v-model="form.email"
        type="email"
        @blur="validateEmail"
        @input="errors.email = ''"
      />
    </UFormGroup>
  </form>
</template>
```

---

### 5. Bottom Navigation Mobile

**Pattern dans layout:**

```vue
<template>
  <div>
    <!-- Main content avec padding bottom pour mobile -->
    <main class="pb-20 sm:pb-8">
      <slot />
    </main>

    <!-- Bottom nav (mobile uniquement) -->
    <nav class="fixed bottom-0 inset-x-0 sm:hidden z-40">
      <div class="grid grid-cols-4 h-16">
        <NuxtLink
          v-for="link in bottomNavLinks"
          :key="link.to"
          :to="link.to"
          class="flex flex-col items-center justify-center"
          active-class="text-primary-600"
          inactive-class="text-gray-500"
        >
          <UIcon :name="link.icon" class="h-6 w-6" />
          <span class="text-xs mt-1">{{ link.label }}</span>
        </NuxtLink>
      </div>
    </nav>
  </div>
</template>
```

---

## 💡 Exemples d'Utilisation

### Créer une Nouvelle Page avec UX Complète

```vue
<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const { getData, createData } = useMyApi()
const { registerShortcut, getShortcutLabel } = useKeyboardShortcuts()

// State
const loading = ref(true)
const loadError = ref(false)
const data = ref([])
const showModal = ref(false)

// Keyboard shortcut label
const shortcutLabel = computed(() => getShortcutLabel('n', { ctrl: true }))

// Fetch data
const fetchData = async () => {
  loading.value = true
  loadError.value = false
  try {
    const result = await getData()
    if (result.success) {
      data.value = result.data
    } else {
      loadError.value = true
    }
  } catch (error) {
    loadError.value = true
  } finally {
    loading.value = false
  }
}

// Register keyboard shortcuts
onMounted(() => {
  fetchData()

  registerShortcut('n', () => {
    showModal.value = true
  }, {
    modifiers: { ctrl: true },
    description: 'Créer un nouvel élément'
  })
})
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-8 flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold">Ma Page</h1>
        <p class="text-gray-600">Description de la page</p>
      </div>
      <UButton @click="showModal = true">
        Nouveau
        <template #trailing>
          <UKbd>{{ shortcutLabel }}</UKbd>
        </template>
      </UButton>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-3 gap-4">
      <SkeletonCard v-for="i in 6" :key="i" />
    </div>

    <!-- Error State -->
    <div v-else-if="loadError">
      <UCard>
        <EmptyState
          icon="i-heroicons-exclamation-circle"
          color="red"
          title="Impossible de charger les données"
          description="Vérifiez votre connexion et réessayez"
          button-text="Réessayer"
          @action="fetchData"
        />
      </UCard>
    </div>

    <!-- Empty State -->
    <div v-else-if="data.length === 0">
      <UCard>
        <EmptyState
          icon="i-heroicons-inbox"
          color="blue"
          title="Aucun élément"
          description="Créez votre premier élément pour commencer!"
          button-text="Créer"
          @action="showModal = true"
        />
      </UCard>
    </div>

    <!-- Content -->
    <div v-else class="grid grid-cols-3 gap-4">
      <UCard v-for="item in data" :key="item.id">
        <!-- ... -->
      </UCard>
    </div>
  </div>
</template>
```

---

## 🎨 Style Guidelines

### Couleurs pour Empty States

- **Blue** (`color="blue"`): Informations générales, comptes, données vides normales
- **Green** (`color="green"`): Succès, argent, économies, budgets
- **Purple** (`color="purple"`): Transactions, actions
- **Orange** (`color="orange"`): Avertissements, alertes modérées
- **Red** (`color="red"`): Erreurs, échecs, suppressions
- **Gray** (`color="gray"`): Neutre, désactivé

### Icônes Recommandées

- Comptes: `i-heroicons-banknotes`, `i-heroicons-building-library`
- Transactions: `i-heroicons-arrows-right-left`
- Budgets: `i-heroicons-chart-bar`
- Catégories: `i-heroicons-tag`
- Épargne: `i-heroicons-currency-dollar`
- Erreur: `i-heroicons-exclamation-circle`
- Succès: `i-heroicons-check-circle`
- Info: `i-heroicons-information-circle`
- Recherche: `i-heroicons-magnifying-glass`
- Plus/Ajouter: `i-heroicons-plus`

---

## 📖 Ressources

- **Nuxt UI Documentation:** https://ui.nuxt.com
- **Heroicons:** https://heroicons.com
- **Tailwind CSS:** https://tailwindcss.com
- **UX Audit:** `docs/UX_AUDIT.md`
- **Testing Checklist:** `docs/UX_TESTING_CHECKLIST.md`

---

**Dernière mise à jour:** 2026-02-14
**Auteur:** fullstack-architect agent
