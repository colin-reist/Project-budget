# 🎨 Audit UX - Budget Tracker

> **Date:** 2026-02-12
> **Version:** 1.0
> **Statut:** Documentation de référence - À implémenter progressivement

---

## 📋 Table des matières

- [Problèmes Critiques](#-problèmes-critiques)
- [Problèmes Importants](#-problèmes-importants)
- [Améliorations Souhaitables](#-améliorations-souhaitables)
- [Améliorations Avancées](#-améliorations-avancées)
- [Score UX](#-score-ux)
- [Priorisation](#-priorisation-des-actions)

---

## 🔴 **PROBLÈMES CRITIQUES** (À corriger en priorité)

### 1. **Onboarding inexistant**

**Problème:** Nouvel utilisateur arrive sur un dashboard vide sans guidage

- ❌ Aucun tutoriel de première connexion
- ❌ Pas de "empty state" engageant qui explique quoi faire
- ❌ L'utilisateur ne sait pas par où commencer (compte? catégorie? budget?)

**Solution:**
```
✅ Ajouter un wizard onboarding (3-4 étapes):
   1. "Créons votre premier compte"
   2. "Ajoutez quelques catégories"
   3. "Créez votre première transaction"
✅ Ou mieux: utiliser la commande setup_default_data automatiquement au premier login
✅ Ajouter un bouton "Guide de démarrage" visible en permanence
```

**Fichiers concernés:**
- `frontend/pages/index.vue`
- `backend/accounts/management/commands/setup_default_data.py`

---

### 2. **Hiérarchie de navigation confuse**

**Problème:** 6 items de navigation au même niveau sans distinction

```
Dashboard | Comptes | Catégories | Transactions | Budgets | Épargne
```

- ❌ "Catégories" et "Budgets" sont des **configurations** (utilisées rarement)
- ❌ Transactions devrait être l'action principale, pas au milieu
- ❌ Pas de différenciation visuelle entre actions et configuration

**Solution:**
```
✅ Navigation réorganisée:
   📊 Dashboard (home)
   💸 Transactions (action principale - raccourci clavier ⌘+N)
   💳 Comptes
   🎯 Épargne
   ---
   ⚙️ Configuration > Catégories, Budgets
```

**Fichiers concernés:**
- `frontend/layouts/default.vue` (ligne 16-65)

---

### 3. **Feedback utilisateur insuffisant**

**Problème Dashboard:**
- ❌ Pas de loading states lors du chargement initial
- ❌ Solde futur entre parenthèses: peu clair ("qu'est-ce que ça veut dire?")
- ❌ Aucune explication des termes "Solde prévisionnel" vs "Solde réel"

**Problème Formulaire transaction:**
- ❌ Validation uniquement au submit (pas de validation temps réel)
- ❌ Messages d'erreur génériques
- ❌ Pas de feedback visuel quand champs obligatoires

**Solution:**
```
✅ Ajouter skeletons/spinners pendant chargement
✅ Tooltips explicatifs sur soldes futurs
✅ Validation inline avec messages clairs
✅ Required fields avec astérisque rouge visible
```

**Fichiers concernés:**
- `frontend/pages/index.vue` (ligne 43-109, 334-427)

---

## 🟠 **PROBLÈMES IMPORTANTS**

### 4. **Dashboard surchargé d'informations**

**Problème:** Trop de données sans hiérarchie claire

```
Ligne 43-109: 3 cartes statistiques
Ligne 112-165: Section comptes
Ligne 168-251: Budget vs Réel (3 cartes + graphique + tableau)
Ligne 254-302: Transactions récentes
```

- ❌ Information overload dès l'arrivée
- ❌ Pas de priorisation visuelle
- ❌ L'utilisateur ne sait pas où regarder en premier

**Solution:**
```
✅ Hiérarchie visuelle:
   1. [HERO] Solde total + action rapide (grosse taille)
   2. [ALERTS] Budgets dépassés / alertes urgentes
   3. [OVERVIEW] Revenus/Dépenses du mois (plus petit)
   4. [DETAILS] Repliable/caché par défaut
```

**Fichiers concernés:**
- `frontend/pages/index.vue` (réorganisation complète)

---

### 5. **Formulaire modal peu ergonomique**

**Problème "Nouvelle transaction" (ligne 334-427):**
- ❌ Modal trop petit pour tout le contenu
- ❌ Scroll caché dans le modal
- ❌ Champs conditionnels (transfert/catégorie) créent du "jumping" visuel
- ❌ Pas de sauvegarde auto en cas de fermeture accidentelle
- ❌ Pas de raccourci clavier pour ouvrir rapidement (⌘+N ou Ctrl+N)

**Solution:**
```
✅ Passer à une page dédiée /transactions/new (meilleure UX mobile)
✅ Ou modal fullscreen sur mobile
✅ Ajouter confirmation "Voulez-vous sauvegarder?" si formulaire rempli
✅ Raccourci clavier global
```

**Fichiers concernés:**
- `frontend/pages/index.vue` (ligne 334-427)
- Créer: `frontend/pages/transactions/new.vue`

---

### 6. **Empty states non-engageants**

**Problème (ligne 137-150):**
```html
<h3>Aucun compte</h3>
<p>Créez votre premier compte pour commencer</p>
```

- ❌ Trop générique, pas d'émotion
- ❌ Pas d'illustration engageante
- ❌ Ne vend pas le bénéfice

**Solution:**
```
✅ "Commencez votre suivi financier 💰"
   "Un compte, c'est comme une tirelire numérique.
    Ajoutez votre compte courant pour voir où part votre argent!"
   [CTA: Créer mon premier compte]
✅ Ajouter illustration/animation
```

**Fichiers concernés:**
- `frontend/pages/index.vue` (ligne 137-150)
- `frontend/pages/transactions/index.vue`
- `frontend/pages/budgets/index.vue`

---

### 7. **Accessibilité limitée**

**Problèmes:**
- ❌ Pas de skip links pour navigation clavier
- ❌ Focus states peu visibles
- ❌ Pas d'annonces ARIA pour les changements dynamiques
- ❌ Contrast ratio à vérifier (gray-500 sur blanc = ~4.5:1, minimum est 4.5:1)
- ❌ Pas de mode haute visibilité

**Solution:**
```
✅ Ajouter skip navigation (<a href="#main">Aller au contenu</a>)
✅ Focus ring visible (outline-2 outline-offset-2)
✅ ARIA live regions pour toasts/notifications
✅ Vérifier contraste avec outil (WebAIM, Stark)
✅ Option "Mode haute visibilité" dans settings
```

**Fichiers concernés:**
- `frontend/layouts/default.vue`
- Tous les composants

---

## 🟡 **AMÉLIORATIONS SOUHAITABLES**

### 8. **Affordance des interactions manquante**

**Problème:**
- ❌ Cartes comptes cliquables mais pas d'indicateur visuel (ligne 120)
- ❌ Hover state existe mais pas visible avant de survoler
- ❌ Pas de cursor pointer explicite

**Solution:**
```css
✅ Ajouter hover:ring, hover:shadow-lg
✅ Cursor pointer visible
✅ Icon chevron-right pour indiquer action
```

**Fichiers concernés:**
- `frontend/pages/index.vue` (ligne 120)

---

### 9. **Données futures mal expliquées**

**Problème (ligne 57-59, 78-80):**
```html
<p class="text-2xl">1000 CHF</p>
<p class="text-sm text-blue-600">(1250 CHF)</p>
```

- ❌ Parenthèses mystérieuses
- ❌ Pas de tooltip explicatif
- ❌ Utilisateur confus

**Solution:**
```
✅ Ajouter UTooltip: "Avec transactions futures planifiées"
✅ Ou afficher "Actuel: 1000 CHF | Projeté: 1250 CHF"
✅ Toggle "Afficher/Masquer futures transactions"
```

**Fichiers concernés:**
- `frontend/pages/index.vue` (ligne 57-59, 78-80, 99-104)

---

### 10. **Formulaire: UX des sélecteurs**

**Problème (ligne 343-353, 368-375):**
- ❌ SelectMenu sans recherche pour catégories (peut devenir long)
- ❌ Pas de création rapide "Créer nouvelle catégorie" in-line
- ❌ Ordre alphabétique pas forcément pertinent (fréquence > alpha)

**Solution:**
```
✅ Autocomplete avec recherche fuzzy
✅ Trier par: fréquence d'utilisation, puis alpha
✅ "+ Créer une catégorie" dans la dropdown
✅ Catégories récentes en haut
```

**Fichiers concernés:**
- `frontend/pages/index.vue` (ligne 343-353, 368-375)

---

### 11. **Mobile: Navigation bottom bar absente**

**Problème:**
- ❌ Hamburger menu = friction (3 clics: ouvrir > sélectionner > fermer)
- ❌ Pas de bottom navigation bar (standard iOS/Android)
- ❌ Navigation principale cachée sur mobile

**Solution:**
```
✅ Bottom tab bar sur mobile (<768px):
   [Dashboard] [Transactions] [Comptes] [Plus]
✅ Hamburger uniquement pour actions secondaires
```

**Fichiers concernés:**
- `frontend/layouts/default.vue`

---

### 12. **Alerts iOS peu visibles**

**Problème (ligne 22-40):**
- ❌ Bannière orange peut être ignorée
- ❌ Pas de badge count visible
- ❌ Disparaît après dismiss (et si erreur?)

**Solution:**
```
✅ Badge notification sur icon navigation
✅ Persistent storage des alertes dismissées (log)
✅ Pouvoir réouvrir l'historique des alertes
```

**Fichiers concernés:**
- `frontend/pages/index.vue` (ligne 22-40)
- `frontend/layouts/default.vue` (ajout badge)

---

### 13. **Graphiques sans interactivité**

**Problème (ligne 206):**
```html
<BudgetVsActualChart :data="..." />
```

- ❌ Graphique statique (probablement)
- ❌ Pas de drill-down sur catégorie
- ❌ Pas de sélection période

**Solution:**
```
✅ Click sur barre → voir détail catégorie
✅ Hover → afficher montant exact
✅ Sélecteur période au-dessus du graphique
```

**Fichiers concernés:**
- `frontend/components/BudgetVsActualChart.vue`
- `frontend/pages/index.vue` (ligne 206)

---

### 14. **Pas de recherche globale**

**Problème:**
- ❌ Aucun search bar pour trouver rapidement une transaction
- ❌ Obligé de naviguer vers /transactions puis filtrer

**Solution:**
```
✅ Search bar global dans header (⌘+K / Ctrl+K)
✅ Recherche intelligente: transactions, comptes, catégories
✅ Raccourci clavier obvie
```

**Fichiers concernés:**
- `frontend/layouts/default.vue` (ajout search)
- Créer: `frontend/components/GlobalSearch.vue`

---

### 15. **Dark mode non optimisé**

**Problème:**
- ❌ Toggle theme = icon soleil/lune (pas clair pour tout le monde)
- ❌ Pas de "auto" (suit système)
- ❌ Contraste à vérifier en dark mode

**Solution:**
```
✅ 3 options: Clair | Sombre | Auto (système)
✅ Label explicite au survol
✅ Vérifier WCAG AAA en dark mode
```

**Fichiers concernés:**
- `frontend/layouts/default.vue` (ligne 184-196)

---

## 🔵 **AMÉLIORATIONS AVANCÉES**

### 16. **Pas de contexte de workflow**

**Problème:** Actions isolées sans guidage
```
Utilisateur crée transaction → succès → retour dashboard
```

- ❌ Pas de suggestion "Créer une autre transaction?"
- ❌ Pas de "Quick add similaire"
- ❌ Workflow interrompu

**Solution:**
```
✅ Toast avec action: "Transaction créée! [Créer une autre] [Voir tout]"
✅ Duplicate last transaction (pour récurrentes)
✅ Suggestions: "Transactions similaires habituellement créées ensemble"
```

**Fichiers concernés:**
- `frontend/pages/index.vue` (ligne 633-640)

---

### 17. **Manque de personnalisation**

**Problème:**
- ❌ Dashboard identique pour tous
- ❌ Pas de widgets configurables
- ❌ Ordre sections fixe

**Solution:**
```
✅ Drag & drop sections dashboard
✅ Masquer/afficher sections
✅ Sauvegarder layout préféré
```

**Fichiers concernés:**
- `frontend/pages/index.vue`
- Créer: `backend/accounts/models.py` (UserPreferences model)

---

### 18. **Pas d'insights / intelligence**

**Problème:**
- ❌ Données brutes sans analyse
- ❌ Utilisateur doit interpréter lui-même
- ❌ Pas de suggestions proactives

**Solution:**
```
✅ "💡 Insight: Vous dépensez 23% plus ce mois-ci vs moyenne"
✅ "⚠️ Alerte: Budget Alimentation sera dépassé dans 3 jours"
✅ "🎯 Conseil: Économisez 50 CHF/mois pour atteindre objectif en 6 mois"
```

**Fichiers concernés:**
- Créer: `backend/analytics/` (nouveau module)
- `frontend/pages/index.vue` (section insights)

---

## 📊 **SCORE UX** (critères Nielsen)

| Critère | Score | Commentaire |
|---------|-------|-------------|
| **1. Visibility of system status** | 🟡 6/10 | Pas de loading states, feedback limité |
| **2. Match system & real world** | 🟢 8/10 | Terminologie claire (CHF, catégories) |
| **3. User control & freedom** | 🟡 6/10 | Pas d'undo, confirmation limitée |
| **4. Consistency & standards** | 🟢 9/10 | Design system cohérent (Nuxt UI) |
| **5. Error prevention** | 🟡 5/10 | Validation faible, pas de confirmation |
| **6. Recognition > Recall** | 🟠 7/10 | Icons clairs mais labels manquent |
| **7. Flexibility & efficiency** | 🟡 5/10 | Pas de raccourcis, pas de bulk actions |
| **8. Aesthetic & minimalist** | 🟠 7/10 | Propre mais dashboard chargé |
| **9. Help users with errors** | 🟡 6/10 | Messages génériques, peu de guidance |
| **10. Help & documentation** | 🔴 3/10 | Aucune aide contextuelle |

**Score global: 6.2/10** - Fonctionnel mais nécessite améliorations UX

---

## 🎯 **PRIORISATION DES ACTIONS**

### **P0 - URGENT** (Impact élevé, effort faible)
1. ✅ Activer setup_default_data au premier login
2. ✅ Ajouter tooltips données futures
3. ✅ Réorganiser navigation (config dans submenu)
4. ✅ Améliorer empty states avec illustrations
5. ✅ Ajouter loading states partout

### **P1 - IMPORTANT** (Impact élevé, effort moyen)
6. ✅ Onboarding wizard première connexion
7. ✅ Search globale (⌘+K)
8. ✅ Bottom navigation mobile
9. ✅ Raccourcis clavier (nouvelle transaction)
10. ✅ Validation temps réel formulaires

### **P2 - SOUHAITABLE** (Impact moyen)
11. ✅ Insights & suggestions intelligentes
12. ✅ Dashboard personnalisable
13. ✅ Graphiques interactifs
14. ✅ Mode haute accessibilité

---

## 📝 **Notes**

- Ce document est une référence à consulter lors de l'implémentation de nouvelles fonctionnalités
- Prioriser les améliorations UX progressivement, en parallèle du développement
- Tester avec de vrais utilisateurs pour valider les hypothèses
- Mettre à jour ce document si de nouveaux problèmes UX sont découverts

---

**Dernière mise à jour:** 2026-02-12
**Auteur:** Audit UX automatisé via Claude Sonnet 4.5
