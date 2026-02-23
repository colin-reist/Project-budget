# 📱 Guide Mobile - Devise Personnalisable

Guide complet pour l'utilisation optimisée de la fonctionnalité de devise personnalisable sur mobile.

---

## 🎯 Vue d'ensemble

La fonctionnalité de devise personnalisable a été optimisée pour mobile avec :

- ✅ **Notation compacte** : Grands montants affichés en notation abrégée (1K, 1M) sur mobile
- ✅ **Drapeaux emoji** : Sélecteur de devise avec drapeaux pour meilleure UX
- ✅ **Performance optimisée** : Cache de 5 minutes + déduplication des requêtes
- ✅ **Composant responsive** : CurrencyAmount s'adapte automatiquement
- ✅ **Détection d'écran** : useScreenSize pour adapter l'UI

---

## 🔧 Utilisation

### 1. Formater une devise (méthode simple)

```vue
<template>
  <div>
    <p>{{ formatCurrency(1234.56) }}</p>
    <!-- Affiche : "1 234,56 CHF" (ou €, $, £ selon profil) -->
  </div>
</template>

<script setup>
// Importe automatiquement depuis ~/utils/currency
</script>
```

### 2. Formater avec notation compacte (mobile)

```vue
<template>
  <div>
    <!-- Notation compacte forcée -->
    <p>{{ formatCurrency(123456, undefined, { forceCompact: true }) }}</p>
    <!-- Affiche : "123K CHF" -->

    <!-- Notation compacte automatique (> 10'000) -->
    <p>{{ formatCurrency(12345, undefined, { compact: true }) }}</p>
    <!-- Affiche : "12K CHF" sur mobile, "12 345,00 CHF" sur desktop -->
  </div>
</template>
```

### 3. Utiliser le composant CurrencyAmount (recommandé)

```vue
<template>
  <div>
    <!-- Utilisation basique -->
    <CurrencyAmount :amount="1234.56" />

    <!-- Avec notation compacte sur mobile -->
    <CurrencyAmount :amount="123456" compact />
    <!-- Affiche "123K CHF" sur mobile, "123 456,00 CHF" sur desktop -->

    <!-- Notation compacte forcée -->
    <CurrencyAmount :amount="1234567" forceCompact />
    <!-- Affiche toujours "1,2M CHF" -->

    <!-- Avec devise spécifique -->
    <CurrencyAmount :amount="99.99" currency="EUR" />

    <!-- Avec classes CSS personnalisées -->
    <CurrencyAmount
      :amount="1234.56"
      class="text-2xl font-bold text-green-600"
      compact
    />
  </div>
</template>

<script setup>
// Composant auto-importé
</script>
```

### 4. Détection de la taille d'écran

```vue
<template>
  <div>
    <!-- Affichage conditionnel selon la taille -->
    <div v-if="isMobile">
      <CurrencyAmount :amount="amount" forceCompact />
    </div>
    <div v-else>
      <CurrencyAmount :amount="amount" />
    </div>

    <!-- Classes conditionnelles -->
    <div :class="{ 'text-sm': isMobile, 'text-lg': isDesktop }">
      {{ formatCurrency(amount) }}
    </div>
  </div>
</template>

<script setup>
const { isMobile, isTablet, isDesktop } = useScreenSize()
</script>
```

### 5. Sélecteur de devise avec drapeaux

```vue
<template>
  <UFormGroup label="Devise">
    <USelectMenu
      v-model="selectedCurrency"
      :options="currencyOptions"
      option-attribute="label"
      value-attribute="value"
    >
      <template #label>
        <span class="flex items-center gap-2">
          <span class="text-lg">{{ getCurrencyFlag(selectedCurrency) }}</span>
          <span>{{ getCurrencyLabel(selectedCurrency) }}</span>
        </span>
      </template>
      <template #option="{ option }">
        <span class="flex items-center gap-2">
          <span class="text-lg">{{ option.flag }}</span>
          <span>{{ option.label }}</span>
        </span>
      </template>
    </USelectMenu>
  </UFormGroup>
</template>

<script setup>
import { CURRENCY_FLAGS } from '~/utils/currency'

const selectedCurrency = ref('CHF')

const currencyOptions = [
  { label: 'Franc Suisse (CHF)', value: 'CHF', flag: '🇨🇭' },
  { label: 'Euro (EUR)', value: 'EUR', flag: '🇪🇺' },
  { label: 'Dollar US (USD)', value: 'USD', flag: '🇺🇸' },
  { label: 'Livre Sterling (GBP)', value: 'GBP', flag: '🇬🇧' }
]

const getCurrencyFlag = (code: string) => {
  return currencyOptions.find(c => c.value === code)?.flag || '🌍'
}

const getCurrencyLabel = (code: string) => {
  return currencyOptions.find(c => c.value === code)?.label || code
}
</script>
```

---

## 📊 Exemples d'affichage

### Sur Mobile (< 640px)

```
Montant     | Normal              | Compact
------------|---------------------|------------------
100         | 100,00 CHF          | 100 CHF
1 234       | 1 234,00 CHF        | 1 234 CHF
12 345      | 12 345,00 CHF       | 12K CHF
123 456     | 123 456,00 CHF      | 123K CHF
1 234 567   | 1 234 567,00 CHF    | 1,2M CHF
```

### Sur Desktop (>= 640px)

```
Montant     | Normal              | Compact
------------|---------------------|------------------
100         | 100,00 CHF          | 100,00 CHF
1 234       | 1 234,00 CHF        | 1 234,00 CHF
12 345      | 12 345,00 CHF       | 12 345,00 CHF
123 456     | 123 456,00 CHF      | 123 456,00 CHF
1 234 567   | 1 234 567,00 CHF    | 1 234 567,00 CHF
```

---

## ⚡ Optimisations Performance

### 1. Cache du profil utilisateur

Le profil utilisateur est mis en cache pendant 5 minutes pour éviter les appels API répétés :

```ts
// Première page
const { currency } = useUserProfile()
await ensureProfileLoaded() // Appel API

// Deuxième page (< 5 min après)
const { currency } = useUserProfile()
await ensureProfileLoaded() // Utilise le cache, pas d'appel API
```

### 2. Déduplication des requêtes

Si plusieurs composants appellent `ensureProfileLoaded()` simultanément, une seule requête est effectuée :

```ts
// Dans 3 composants montés simultanément
await ensureProfileLoaded() // 1 seul appel API partagé
```

### 3. Auto-importation

Les composants et utilitaires sont auto-importés par Nuxt :

```vue
<template>
  <!-- Pas besoin d'import -->
  <CurrencyAmount :amount="100" />
  {{ formatCurrency(100) }}
</template>

<script setup>
// Pas besoin d'import pour :
// - formatCurrency
// - CurrencyAmount
// - useUserProfile
// - useScreenSize
</script>
```

---

## 🎨 Bonnes pratiques

### ✅ DO

```vue
<!-- Utiliser CurrencyAmount pour consistance -->
<CurrencyAmount :amount="total" compact class="text-2xl" />

<!-- Utiliser compact sur mobile pour grands montants -->
<CurrencyAmount :amount="1234567" compact />

<!-- Ajouter title/tooltip pour montants compacts -->
<CurrencyAmount :amount="amount" compact /> <!-- Auto-tooltip -->
```

### ❌ DON'T

```vue
<!-- Ne pas formater manuellement -->
<span>{{ amount.toFixed(2) }} CHF</span> ❌

<!-- Ne pas utiliser toujours forceCompact -->
<CurrencyAmount :amount="100" forceCompact /> ❌
<!-- 100 devient "100,00 CHF" au lieu de format compact -->

<!-- Ne pas dupliquer la logique de formatage -->
<span>{{ new Intl.NumberFormat(...) }}</span> ❌
```

---

## 📱 Classes CSS Utiles

### Responsive Text Size

```vue
<CurrencyAmount
  :amount="amount"
  compact
  class="text-sm sm:text-base lg:text-lg"
/>
```

### Éviter le débordement

```vue
<div class="overflow-hidden text-ellipsis">
  <CurrencyAmount :amount="veryLongAmount" compact />
</div>
```

### Grid responsive pour montants

```vue
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  <div v-for="item in items" :key="item.id">
    <CurrencyAmount :amount="item.amount" compact class="text-xl font-bold" />
  </div>
</div>
```

---

## 🔍 Debugging

### Vérifier la devise du profil

```vue
<script setup>
const { userProfile, currency } = useUserProfile()

watchEffect(() => {
  console.log('Current currency:', currency.value)
  console.log('Full profile:', userProfile.value)
})
</script>
```

### Vérifier la taille d'écran

```vue
<script setup>
const { screenWidth, isMobile, isTablet, isDesktop } = useScreenSize()

watchEffect(() => {
  console.log('Screen width:', screenWidth.value)
  console.log('Is mobile:', isMobile.value)
})
</script>
```

### Forcer le rafraîchissement du profil

```vue
<script setup>
const { fetchProfile } = useUserProfile()

// Forcer le rafraîchissement (ignore le cache)
await fetchProfile(true)
</script>
```

---

## 🚀 Performance Tips

1. **Utilisez `compact`** pour les tableaux avec beaucoup de montants sur mobile
2. **Évitez `forceCompact`** sauf si vous voulez toujours la notation compacte
3. **Le cache de 5 min** évite les appels API répétés
4. **Auto-import** réduit la taille du bundle

---

## 📝 Migration

### Avant (code dupliqué)

```vue
<template>
  <span>{{ formatCurrency(amount) }}</span>
</template>

<script setup>
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('fr-CH', {
    style: 'currency',
    currency: 'CHF'
  }).format(amount)
}
</script>
```

### Après (centralisé et optimisé)

```vue
<template>
  <CurrencyAmount :amount="amount" compact />
</template>

<script setup>
// Rien à importer, tout est auto-importé !
</script>
```

---

**Date de mise à jour : 2026-02-23**
