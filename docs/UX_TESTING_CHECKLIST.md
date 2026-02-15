# ✅ Checklist de Test des Améliorations UX

> **Date:** 2026-02-14
> **Version:** 2.0
> **Pour:** Validation des améliorations P0 et P1

---

## 🎯 Instructions de Test

Cette checklist permet de valider que toutes les améliorations UX implémentées fonctionnent correctement sur desktop et mobile.

---

## ✅ P0 - Tests Urgents

### 1. Tooltips sur Données Futures

**Page:** Dashboard (`/`)

- [ ] **Dashboard - Revenus:**
  - Afficher le dashboard avec des revenus futurs planifiés
  - Survoler le montant entre parenthèses (bleu)
  - Vérifier tooltip: "Solde projeté incluant vos revenus futurs planifiés ce mois"

- [ ] **Dashboard - Dépenses:**
  - Avec des dépenses futures planifiées
  - Survoler le montant entre parenthèses (rouge)
  - Vérifier tooltip: "Montant projeté incluant vos dépenses futures planifiées ce mois"

- [ ] **Dashboard - Économies:**
  - Avec économies futures
  - Survoler le montant entre parenthèses (vert ou rouge)
  - Vérifier tooltip: "Économies projetées incluant vos transactions futures planifiées ce mois"

**Page:** Comptes (`/accounts`)

- [ ] **Solde actuel:**
  - Survoler "Solde actuel"
  - Vérifier tooltip: "Votre solde actuel, sans compter les transactions futures planifiées"

- [ ] **Solde projeté:**
  - Si différent du solde actuel, survoler la carte bleue
  - Vérifier tooltip: "Votre solde futur estimé en incluant toutes les transactions planifiées"

**Page:** Budgets (`/budgets`)

- [ ] **Budgets d'épargne - Montant projeté:**
  - Survoler "Projeté: XXX CHF" (vert)
  - Vérifier tooltip: "Montant projeté incluant vos transferts futurs planifiés"

- [ ] **Budgets réguliers - Montant projeté:**
  - Survoler "Projeté: XXX CHF" (bleu)
  - Vérifier tooltip: "Montant projeté incluant vos dépenses futures planifiées"

- [ ] **Pourcentage projeté:**
  - Survoler "(XX% projeté)"
  - Vérifier tooltip approprié selon le type de budget

---

### 2. Navigation Réorganisée

**Desktop:**

- [ ] Vérifier l'ordre de navigation:
  1. Dashboard (avec icône home)
  2. Transactions (avec icône arrows-right-left)
  3. Comptes (avec icône building-library)
  4. Épargne (avec icône banknotes)
  5. Configuration (dropdown avec icône cog)

- [ ] Cliquer sur "Configuration":
  - Vérifier que le dropdown s'ouvre
  - Voir "Catégories" avec icône tag
  - Voir "Budgets" avec icône chart-bar

- [ ] Vérifier que toutes les icônes sont visibles à côté des labels

**Mobile:**

- [ ] Menu hamburger contient tous les liens dans le bon ordre
- [ ] Icônes visibles dans le slideover mobile

---

### 3. Empty States Améliorés

**Dashboard - Aucun compte:**

- [ ] Créer un nouvel utilisateur (ou supprimer tous les comptes)
- [ ] Vérifier l'affichage:
  - Icône banknote dans cercle bleu
  - Titre: "Commencez votre suivi financier 💰"
  - Description engageante
  - Bouton "Créer mon premier compte" visible

**Page Transactions - Aucune transaction:**

- [ ] Sans transactions
- [ ] Vérifier:
  - Icône arrows-right-left dans cercle violet
  - Titre: "Aucune transaction trouvée"
  - Description motivante
  - Bouton "Créer une transaction"

**Page Comptes - Aucun compte:**

- [ ] Sans comptes
- [ ] Vérifier:
  - Icône banknote dans cercle bleu
  - Titre: "Créez votre premier compte 💳"
  - Description claire
  - Bouton "Créer un compte"

**Page Budgets - Aucun budget:**

- [ ] Sans budgets
- [ ] Vérifier:
  - Icône chart-bar dans cercle vert
  - Titre: "Maîtrisez vos dépenses avec les budgets 📊"
  - Description avec bénéfices
  - Bouton "Créer mon premier budget"

---

### 4. Loading States (Skeletons)

**Dashboard:**

- [ ] Rafraîchir la page
- [ ] Pendant le chargement, vérifier:
  - 3 skeleton cards pour les statistiques (revenus, dépenses, économies)
  - 4 skeleton cards pour les comptes
  - Pas de "flash" de contenu vide

**Page Transactions:**

- [ ] Rafraîchir la page
- [ ] Vérifier skeletons:
  - 5 lignes avec icône circulaire + texte + montant
  - Animation de pulse

**Page Comptes:**

- [ ] Rafraîchir la page
- [ ] Vérifier:
  - 3 skeleton cards avec header et footer
  - Plusieurs lignes de contenu
  - Transitions fluides vers le contenu réel

---

## ✅ P1 - Tests Importants

### 5. Onboarding Wizard

**Conditions de test:**

- [ ] Créer un nouveau compte utilisateur
- [ ] Se connecter pour la première fois
- [ ] OU supprimer tous comptes + catégories + vider localStorage `onboarding_completed`

**Test du wizard:**

- [ ] **Étape 0 - Bienvenue:**
  - Modal s'ouvre automatiquement au chargement
  - Titre: "Bienvenue dans Budget Tracker! 🎉"
  - 3 cartes de bénéfices (Comptes, Catégories, Transactions)
  - Bouton "Passer" visible en haut à droite
  - Bouton "Commencer" en bas à droite
  - Barre de progression: 25%

- [ ] **Étape 1 - Créer compte:**
  - Cliquer "Commencer"
  - Formulaire de création de compte visible
  - Champs: Nom, Type, Solde
  - Info box bleue expliquant "Pourquoi créer un compte?"
  - Bouton "Retour" à gauche
  - Bouton "Suivant" à droite
  - Barre de progression: 50%

- [ ] **Remplir et soumettre:**
  - Remplir: "Compte Courant", "Compte Courant", "1000"
  - Cliquer "Suivant"
  - Vérifier que le compte est créé (pas d'erreur)

- [ ] **Étape 2 - Catégories:**
  - Info box verte: catégories par défaut créées
  - 2 cartes montrant les catégories revenus et dépenses
  - Bouton "Suivant"
  - Barre de progression: 75%

- [ ] **Étape 3 - Félicitations:**
  - Icône check-circle verte
  - Titre: "Tout est prêt! 🎊"
  - Section "Astuces" avec 3 conseils
  - Mention du raccourci Ctrl+N (ou ⌘N sur Mac)
  - Bouton "Terminer et commencer"
  - Barre de progression: 100%

- [ ] **Finalisation:**
  - Cliquer "Terminer et commencer"
  - Modal se ferme
  - Dashboard affiche le compte créé
  - Toast de succès: "Bienvenue! 🎉"

- [ ] **Vérifier qu'il ne se réaffiche pas:**
  - Rafraîchir la page
  - Wizard ne doit PAS se réouvrir

- [ ] **Test du bouton "Passer":**
  - Effacer localStorage `onboarding_completed`
  - Rafraîchir
  - Cliquer "Passer" sur l'étape 0
  - Wizard se ferme
  - Ne se réaffiche plus au refresh

---

### 6. Raccourcis Clavier

**Ctrl+N / ⌘N - Nouvelle transaction:**

- [ ] Sur le dashboard
- [ ] Appuyer sur Ctrl+N (ou ⌘N sur Mac)
- [ ] Modal "Nouvelle transaction" s'ouvre
- [ ] Appuyer sur Escape
- [ ] Modal se ferme

- [ ] Sur n'importe quelle page
- [ ] Même test: Ctrl+N ouvre la modal

- [ ] Dans un champ input/textarea
- [ ] Ctrl+N ne doit PAS ouvrir la modal (on tape du texte)

**Bouton avec indication du raccourci:**

- [ ] Bouton "Nouvelle transaction" sur le dashboard
- [ ] Vérifier badge UKbd visible: "Ctrl+N" ou "⌘N"

**? - Aide raccourcis:**

- [ ] Appuyer sur `?` (sans Shift, juste le point d'interrogation)
- [ ] Modal "Raccourcis clavier" s'ouvre
- [ ] Voir la liste des raccourcis
- [ ] Section "Actions principales": Ctrl+N pour nouvelle transaction
- [ ] Section "Navigation": Esc pour fermer modals
- [ ] Bouton "Fermer"

**Bouton d'aide dans le header:**

- [ ] Desktop: icône command-line visible dans le header
- [ ] Survoler: tooltip "Raccourcis clavier (appuyez sur ?)"
- [ ] Cliquer: modal s'ouvre

---

### 7. Validation Temps Réel

**Modal Nouvelle Transaction:**

- [ ] Ouvrir la modal (bouton ou Ctrl+N)

**Test champ Montant:**

- [ ] Laisser vide et cliquer hors du champ (blur)
- [ ] Erreur rouge: "Le montant est requis"

- [ ] Saisir "0" puis blur
- [ ] Erreur: "Le montant doit être supérieur à 0"

- [ ] Saisir "abc" puis blur
- [ ] Erreur: "Le montant doit être supérieur à 0" (NaN)

- [ ] Saisir "50.50"
- [ ] Erreur disparaît immédiatement (sur @input)

**Test champ Compte:**

- [ ] Changer la sélection
- [ ] Si erreur précédente, elle disparaît

**Validation au submit:**

- [ ] Laisser tous les champs vides
- [ ] Cliquer "Créer"
- [ ] Toast d'erreur avec message de validation
- [ ] Erreurs affichées sous chaque champ

---

### 8. Bottom Navigation Mobile

**Test sur mobile (<768px):**

- [ ] Réduire la fenêtre navigateur < 768px
- [ ] OU utiliser DevTools mode responsive

**Vérifier la bottom nav:**

- [ ] Barre fixe en bas de l'écran
- [ ] 5 items visibles:
  1. Accueil (icône home)
  2. Transactions (icône arrows-right-left)
  3. Comptes (icône building-library)
  4. Épargne (icône banknotes)
  5. Plus (icône ellipsis-horizontal-circle)

- [ ] Icônes ET labels visibles
- [ ] Navigation vers chaque page fonctionne
- [ ] Item actif en couleur primary
- [ ] Items inactifs en gris

**Vérifier l'overlap:**

- [ ] Le contenu principal ne doit PAS être caché par la bottom nav
- [ ] Padding bottom ajouté automatiquement (pb-20)
- [ ] Scroll jusqu'en bas: tout le contenu accessible

**Desktop:**

- [ ] Agrandir > 768px
- [ ] Bottom nav disparaît
- [ ] Navigation top visible normalement

---

## 🧪 Tests Supplémentaires

### Responsive Design

- [ ] **Mobile (< 640px):**
  - Dashboard responsive
  - Cards en 1 colonne
  - Formulaires lisibles
  - Bottom nav fonctionnelle

- [ ] **Tablet (640px - 1024px):**
  - Grid 2-3 colonnes
  - Navigation top visible
  - Pas de bottom nav

- [ ] **Desktop (> 1024px):**
  - Layout optimal
  - Tous les éléments visibles
  - Dropdowns fonctionnels

### Accessibilité

- [ ] **Navigation clavier:**
  - Tab pour naviguer entre éléments
  - Focus visible (outline)
  - Enter pour activer boutons/links

- [ ] **ARIA labels:**
  - Boutons sans texte ont aria-label
  - Modals ont role="dialog"

- [ ] **Contraste:**
  - Texte lisible sur fond
  - Respecte WCAG AA (4.5:1)

### Dark Mode

- [ ] Basculer en dark mode
- [ ] Tous les composants s'adaptent:
  - Tooltips lisibles
  - Empty states visibles
  - Skeletons corrects
  - Bottom nav contrastée
  - Modals sombres

### Performance

- [ ] Pas de ralentissement avec les skeletons
- [ ] Raccourcis clavier réactifs (<100ms)
- [ ] Modals s'ouvrent rapidement
- [ ] Pas de layout shifts au chargement

---

## 📝 Rapport de Bugs

Si vous trouvez des problèmes, documentez-les ici:

### Bug Template

```
**Page/Composant:**
**Description:**
**Étapes pour reproduire:**
1.
2.
3.
**Comportement attendu:**
**Comportement actuel:**
**Environnement:** (Desktop/Mobile, Navigateur)
**Screenshots:**
```

---

## ✅ Validation Finale

Une fois tous les tests passés:

- [ ] Tous les tooltips fonctionnent
- [ ] Navigation réorganisée et intuitive
- [ ] Empty states engageants
- [ ] Loading states professionnels
- [ ] Onboarding wizard complet
- [ ] Raccourcis clavier opérationnels
- [ ] Validation temps réel active
- [ ] Bottom nav mobile fonctionnelle

**Date de validation:** ___________
**Validé par:** ___________
**Score:** _____ / 50 tests

---

**Dernière mise à jour:** 2026-02-14
**Version:** 2.0
