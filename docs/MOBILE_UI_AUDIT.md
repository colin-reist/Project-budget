# 📱 Audit UI Mobile - Budget Tracker

> **Date:** 2026-02-23
> **Version:** 1.0
> **Objectif:** Identifier et corriger tous les problèmes d'UI mobile

---

## 📊 État Actuel

### ✅ Points Positifs

1. **Bottom Navigation** ✅
   - Navigation fixe en bas sur mobile
   - 5 liens principaux accessibles
   - Icons clairs

2. **Hamburger Menu** ✅
   - Slideover avec tous les liens
   - User info affichées
   - Fermeture facile

3. **Responsive Grid** ✅
   - grid-cols-1 sm:grid-cols-2 lg:grid-cols-3
   - Adapte automatiquement

4. **Padding Bottom** ✅
   - pb-20 sm:pb-8 pour éviter chevauchement
   - Bottom nav ne cache pas le contenu

### ❌ Problèmes Identifiés

#### 1. Touch Targets (Critique)
- ❌ Certains boutons < 44px (trop petits pour le toucher)
- ❌ Liens de navigation trop proches (risque de mauvais clic)
- ❌ Icons dans les cards trop petits

#### 2. Typography (Important)
- ❌ Texte trop petit sur mobile (< 14px)
- ❌ Line-height trop serrée
- ❌ Contraste insuffisant sur certains textes gris

#### 3. Formulaires (Important)
- ❌ Inputs pas assez grands sur mobile
- ❌ Pas de keyboard type approprié (numeric, email, tel)
- ❌ Labels parfois trop petits
- ❌ Messages d'erreur peu visibles

#### 4. Tableaux (Critique)
- ❌ Tableaux pas responsive (scroll horizontal problématique)
- ❌ Devrait se transformer en cards sur mobile
- ❌ Texte trop petit dans les cellules

#### 5. Modals (Moyen)
- ❌ Modals pas full-screen sur mobile
- ❌ Bouton fermer pas assez grand
- ❌ Pas de swipe to close

#### 6. Cards (Moyen)
- ❌ Padding insuffisant sur mobile
- ❌ Gap entre cards trop petit
- ❌ Texte parfois coupé

#### 7. Spacing (Moyen)
- ❌ Espacement général trop serré sur mobile
- ❌ Margin entre sections insuffisant

#### 8. Images & Icons (Mineur)
- ❌ Icons pas assez grands sur mobile
- ❌ Pas d'avatars/images optimisées

---

## 🎯 Plan d'Amélioration

### Phase 1 : Touch Targets (P0 - Critique)

**Objectif:** Tous les éléments tactiles ≥ 44px × 44px

**Actions:**
1. Augmenter taille des boutons principaux
2. Augmenter padding des liens de navigation
3. Augmenter taille des icons interactifs
4. Ajouter plus d'espace entre éléments tactiles

**Fichiers:**
- `layouts/default.vue` - Navigation
- `pages/*.vue` - Boutons d'action
- Tous les composants avec boutons

### Phase 2 : Typography (P0 - Critique)

**Objectif:** Texte lisible sans zoom (≥ 16px base)

**Actions:**
1. Augmenter font-size de base à 16px sur mobile
2. Augmenter line-height à 1.6 minimum
3. Améliorer contraste (WCAG AA minimum)
4. Headers plus grands sur mobile

**Fichiers:**
- `tailwind.config.ts` - Base typography
- `app.vue` - CSS global
- Tous les composants

### Phase 3 : Formulaires (P1 - Important)

**Objectif:** Formulaires optimisés mobile

**Actions:**
1. Inputs min-height 48px sur mobile
2. Ajouter inputmode/type appropriés
3. Labels toujours 16px minimum
4. Messages d'erreur bien visibles
5. Auto-focus intelligent

**Fichiers:**
- `pages/profile.vue`
- `pages/transactions/index.vue`
- `pages/accounts/index.vue`
- Tous les formulaires

### Phase 4 : Tableaux Responsive (P1 - Important)

**Objectif:** Tableaux → Cards sur mobile

**Actions:**
1. Créer composant ResponsiveTable
2. Transformer tableaux en cards < 768px
3. Améliorer scroll horizontal si nécessaire
4. Actions swipe (delete, edit)

**Fichiers:**
- `pages/transactions/index.vue`
- `pages/budgets/index.vue`
- `components/ResponsiveTable.vue` (nouveau)

### Phase 5 : Modals (P2 - Moyen)

**Objectif:** Modals optimisés mobile

**Actions:**
1. Full-screen sur mobile
2. Bouton fermer 44×44px
3. Swipe to close
4. Animation slide-up

**Fichiers:**
- Tous les modals
- Composant custom si nécessaire

### Phase 6 : Spacing & Layout (P2 - Moyen)

**Objectif:** Espacement confortable

**Actions:**
1. Augmenter padding des cards sur mobile
2. Augmenter gap entre éléments
3. Margin sections plus généreux
4. Responsive padding (px-4 sm:px-6 lg:px-8)

**Fichiers:**
- Tous les fichiers

---

## 📏 Standards Mobile

### Touch Targets
```
Minimum: 44px × 44px (Apple HIG)
Recommandé: 48px × 48px (Material Design)
Espace entre: 8px minimum
```

### Typography
```
Base: 16px (mobile), 14px ok desktop
Headers:
  - H1: 28-32px mobile, 36-48px desktop
  - H2: 24-28px mobile, 30-36px desktop
  - H3: 20-24px mobile, 24-30px desktop
Line-height: 1.5-1.6 minimum
Contraste: 4.5:1 minimum (WCAG AA)
```

### Spacing
```
Padding cards: p-4 sm:p-6
Gap grids: gap-4 sm:gap-6
Margin sections: mb-6 sm:mb-8
```

### Inputs
```
Min-height: 48px
Padding: py-3 px-4
Font-size: 16px (évite zoom iOS)
```

---

## 🔧 Outils & Classes Tailwind

### Touch Targets
```vue
<!-- Button minimum -->
<UButton size="lg" class="min-h-[44px]" />

<!-- Link avec padding -->
<a class="p-3 -m-3">Lien</a>

<!-- Icon cliquable -->
<UIcon class="h-6 w-6 p-2 -m-2" />
```

### Typography Responsive
```vue
<!-- Headers -->
<h1 class="text-2xl sm:text-3xl lg:text-4xl">

<!-- Body -->
<p class="text-base sm:text-lg">

<!-- Small -->
<span class="text-sm sm:text-base">
```

### Spacing Responsive
```vue
<!-- Card -->
<UCard class="p-4 sm:p-6 lg:p-8">

<!-- Grid -->
<div class="grid gap-4 sm:gap-6 lg:gap-8">

<!-- Section -->
<section class="mb-6 sm:mb-8 lg:mb-12">
```

---

## ✅ Checklist de Validation

### Navigation
- [ ] Bottom nav items ≥ 44px
- [ ] Hamburger button ≥ 44px
- [ ] Espacement entre items ≥ 8px
- [ ] Labels lisibles sans zoom

### Formulaires
- [ ] Inputs ≥ 48px hauteur
- [ ] Labels ≥ 16px
- [ ] Type/inputmode corrects
- [ ] Erreurs visibles et lisibles
- [ ] Validation temps réel

### Tableaux
- [ ] Responsive sur mobile
- [ ] Cards ou scroll amélioré
- [ ] Texte ≥ 14px
- [ ] Actions accessibles

### Cards
- [ ] Padding ≥ 16px mobile
- [ ] Gap entre cards ≥ 16px
- [ ] Texte pas coupé
- [ ] Touch targets corrects

### Typography
- [ ] Base ≥ 16px mobile
- [ ] Contraste ≥ 4.5:1
- [ ] Line-height ≥ 1.5
- [ ] Headers proportionnés

### Spacing
- [ ] Padding confortable
- [ ] Sections bien séparées
- [ ] Pas de texte collé aux bords
- [ ] Bottom nav ne cache rien

---

## 📝 Priorités

### P0 - À faire immédiatement
1. Touch targets (sécurité d'utilisation)
2. Typography (lisibilité)

### P1 - À faire rapidement
3. Formulaires (UX critique)
4. Tableaux (frustration utilisateur)

### P2 - À faire ensuite
5. Modals (confort)
6. Spacing (polish)

---

**Prochaine étape:** Créer les composants et utilitaires réutilisables
