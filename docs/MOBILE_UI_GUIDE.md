# 📱 Guide d'Utilisation - UI Mobile Optimisée

Guide complet pour utiliser les améliorations UI mobile dans Budget Tracker.

---

## 🎯 Vue d'ensemble

L'UI a été optimisée pour mobile avec :

- ✅ **Touch targets** : Tous les boutons ≥ 44px × 44px
- ✅ **Typography** : Font-size ≥ 16px sur mobile (évite zoom iOS)
- ✅ **Formulaires** : Inputs 48px de hauteur, keyboard types corrects
- ✅ **Tableaux** : Transformation automatique en cards sur mobile
- ✅ **Modals** : Full-screen sur mobile avec swipe to close
- ✅ **Spacing** : Padding et margins confortables

---

## 🧩 Composants Disponibles

### 1. ResponsiveTable

Transforme automatiquement les tableaux en cards sur mobile.

```vue
<template>
  <ResponsiveTable
    :columns="[
      { key: 'description', label: 'Description' },
      { key: 'amount', label: 'Montant', class: 'text-right' },
      { key: 'date', label: 'Date' }
    ]"
    :rows="transactions"
    :loading="loading"
    empty-message="Aucune transaction"
  >
    <!-- Custom cell rendering -->
    <template #cell-amount="{ value }">
      <CurrencyAmount :amount="value" compact />
    </template>

    <template #cell-date="{ value }">
      {{ formatDate(value) }}
    </template>

    <!-- Actions (visible sur mobile ET desktop) -->
    <template #actions="{ row }">
      <UButton size="sm" icon="i-heroicons-pencil" @click="edit(row)" />
      <UButton size="sm" icon="i-heroicons-trash" color="red" @click="delete(row)" />
    </template>

    <!-- Empty state -->
    <template #empty>
      <div class="text-center py-8">
        <UIcon name="i-heroicons-inbox" class="h-12 w-12 mx-auto text-gray-400 mb-3" />
        <p>Aucune donnée à afficher</p>
      </div>
    </template>
  </ResponsiveTable>
</template>
```

**Affichage:**
- **Mobile (< 640px):** Cards avec labels
- **Desktop (≥ 640px):** Table traditionnelle

---

### 2. MobileInput

Input optimisé pour mobile avec keyboard types corrects.

```vue
<template>
  <div class="space-y-4">
    <!-- Email with email keyboard -->
    <MobileInput
      v-model="email"
      label="Email"
      type="email"
      placeholder="exemple@email.com"
      autocomplete="email"
      required
    />

    <!-- Number with numeric keyboard -->
    <MobileInput
      v-model="amount"
      label="Montant"
      type="number"
      inputmode="decimal"
      placeholder="0.00"
    >
      <template #trailing>
        <span class="text-gray-500">CHF</span>
      </template>
    </MobileInput>

    <!-- Phone with tel keyboard -->
    <MobileInput
      v-model="phone"
      label="Téléphone"
      type="tel"
      placeholder="+41 79 123 45 67"
      autocomplete="tel"
    />

    <!-- Text with help -->
    <MobileInput
      v-model="description"
      label="Description"
      type="text"
      placeholder="Ex: Courses Migros"
      help="Décrivez la transaction"
      :error="errors.description"
    />
  </div>
</template>

<script setup>
const email = ref('')
const amount = ref('')
const phone = ref('')
const description = ref('')
const errors = ref({})
</script>
```

**Bénéfices:**
- ✅ Font-size 16px (pas de zoom iOS)
- ✅ Min-height 48px (facile à taper)
- ✅ Keyboard type approprié
- ✅ Autocomplete activé

---

### 3. MobileModal

Modal full-screen sur mobile avec swipe to close.

```vue
<template>
  <div>
    <UButton @click="showModal = true">
      Ouvrir Modal
    </UButton>

    <MobileModal v-model="showModal" title="Nouvelle transaction">
      <!-- Contenu du modal -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <MobileInput
          v-model="form.description"
          label="Description"
          required
        />

        <MobileInput
          v-model="form.amount"
          label="Montant"
          type="number"
          inputmode="decimal"
          required
        />
      </form>

      <!-- Footer avec boutons -->
      <template #footer="{ close }">
        <UButton color="gray" variant="ghost" @click="close">
          Annuler
        </UButton>
        <UButton @click="handleSubmit">
          Enregistrer
        </UButton>
      </template>
    </MobileModal>
  </div>
</template>

<script setup>
const showModal = ref(false)
const form = ref({ description: '', amount: '' })

const handleSubmit = () => {
  // Submit logic
  showModal.value = false
}
</script>
```

**Affichage:**
- **Mobile:** Full-screen avec slide-up animation
- **Desktop:** Modal centré classique
- **Swipe:** Swiper vers le bas pour fermer (mobile)

---

## 🎨 Classes CSS Utilitaires

### Touch Targets

```vue
<!-- Bouton avec touch target minimum -->
<UButton size="lg" class="btn-touch-target" />

<!-- Bouton large -->
<UButton size="lg" class="btn-touch-target-lg" />

<!-- Icon cliquable -->
<UIcon name="i-heroicons-pencil" class="icon-btn" />

<!-- Lien avec padding -->
<a href="#" class="touch-padding">Lien</a>
```

### Typography Responsive

```vue
<!-- Headers -->
<h1 class="text-responsive-2xl">Page Title</h1>
<h2 class="text-responsive-xl">Section Title</h2>
<h3 class="text-responsive-lg">Subsection</h3>

<!-- Body text -->
<p class="text-responsive-base">Normal text</p>
<span class="text-responsive-sm">Small text</span>
```

### Spacing Mobile

```vue
<!-- Card avec padding responsive -->
<UCard class="card-mobile">
  Content
</UCard>

<!-- Grid avec gaps responsive -->
<div class="grid grid-mobile grid-cols-1 sm:grid-cols-2">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Section spacing -->
<section class="section-mobile">
  Content
</section>

<!-- Liste items -->
<ul>
  <li class="list-item-mobile">Item 1</li>
  <li class="list-item-mobile">Item 2</li>
</ul>
```

### Formulaires Mobile

```vue
<!-- Bouton full-width sur mobile -->
<UButton class="btn-primary-mobile">
  Enregistrer
</UButton>

<!-- Groupe de boutons -->
<div class="btn-group-mobile">
  <UButton color="gray">Annuler</UButton>
  <UButton>Valider</UButton>
</div>

<!-- Actions fixées en bas (mobile) -->
<div class="actions-mobile">
  <UButton class="w-full">Enregistrer</UButton>
</div>
```

---

## 📏 Standards à Respecter

### Touch Targets

```vue
✅ DO
<UButton size="lg" class="min-h-[44px]">Clic</UButton>

❌ DON'T
<button class="text-sm p-1">Clic</button>
```

### Typography

```vue
✅ DO
<input type="email" class="text-base min-h-[48px]" />

❌ DON'T
<input type="email" class="text-sm h-8" />
```

### Spacing

```vue
✅ DO
<div class="p-4 sm:p-6 gap-4 sm:gap-6">

❌ DON'T
<div class="p-2 gap-2">
```

---

## 🔄 Migration

### Avant (Tableaux)

```vue
<table class="w-full">
  <thead>
    <tr>
      <th>Nom</th>
      <th>Montant</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="item in items" :key="item.id">
      <td>{{ item.name }}</td>
      <td>{{ item.amount }}</td>
    </tr>
  </tbody>
</table>
```

### Après (ResponsiveTable)

```vue
<ResponsiveTable
  :columns="[
    { key: 'name', label: 'Nom' },
    { key: 'amount', label: 'Montant' }
  ]"
  :rows="items"
/>
```

---

### Avant (Formulaires)

```vue
<UFormGroup label="Email">
  <UInput v-model="email" type="email" />
</UFormGroup>
```

### Après (MobileInput)

```vue
<MobileInput
  v-model="email"
  label="Email"
  type="email"
  autocomplete="email"
/>
```

---

### Avant (Modals)

```vue
<UModal v-model="show">
  <UCard>
    <template #header>
      <div class="flex justify-between">
        <h3>Titre</h3>
        <UButton @click="show = false">×</UButton>
      </div>
    </template>
    Content
  </UCard>
</UModal>
```

### Après (MobileModal)

```vue
<MobileModal v-model="show" title="Titre">
  Content
  <template #footer="{ close }">
    <UButton @click="close">Fermer</UButton>
  </template>
</MobileModal>
```

---

## 🧪 Tests

### Test Touch Targets

1. Ouvrir sur mobile réel ou Chrome DevTools
2. Activer "Show Paint Flashing"
3. Vérifier que tous les boutons sont faciles à cliquer
4. Mesurer : tous les éléments interactifs ≥ 44px

### Test Typography

1. Ouvrir sur iPhone (Safari)
2. Remplir un formulaire
3. Vérifier : pas de zoom automatique
4. Font-size inputs ≥ 16px

### Test Tableaux

1. Ouvrir /transactions sur mobile
2. Vérifier : affichage en cards
3. Ouvrir sur desktop
4. Vérifier : affichage en table

### Test Modals

1. Ouvrir un modal sur mobile
2. Vérifier : full-screen
3. Swiper vers le bas
4. Vérifier : modal se ferme

---

## 🎯 Checklist d'Implémentation

- [ ] Import CSS mobile dans nuxt.config.ts
- [ ] Remplacer tables par ResponsiveTable
- [ ] Utiliser MobileInput pour formulaires
- [ ] Utiliser MobileModal pour modals
- [ ] Appliquer classes touch-target
- [ ] Vérifier font-size ≥ 16px partout
- [ ] Tester sur iPhone/Android réel
- [ ] Vérifier accessibilité (VoiceOver/TalkBack)
- [ ] Lighthouse Mobile Score ≥ 90

---

**Date de mise à jour : 2026-02-23**
