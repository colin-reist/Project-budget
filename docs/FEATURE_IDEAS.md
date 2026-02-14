# 💡 Idées de Fonctionnalités - Budget Tracker

> **Date:** 2026-02-13
> **Source:** Suggestions de Claude Sonnet 4.5
> **Statut:** Backlog d'idées à considérer

---

## 📋 Table des matières

- [Suggestions Prioritaires](#-suggestions-prioritaires)
- [Suggestions Avancées](#-suggestions-avancées)
- [Implémenté](#-implémenté)

---

## 🎯 **SUGGESTIONS PRIORITAIRES** (Impact élevé)

### 1. **📊 Split de transactions**

**Description:**
Diviser une transaction en plusieurs catégories pour une comptabilité plus précise.

**Cas d'usage:**
```
Achat Migros 100 CHF →
  ├─ 70 CHF → Alimentation (70%)
  ├─ 20 CHF → Produits ménagers (20%)
  └─ 10 CHF → Hygiène (10%)
```

**Bénéfices:**
- ✅ Comptabilité plus précise
- ✅ Meilleure analyse des dépenses
- ✅ Utile pour grandes courses mixtes

**Complexité:** Moyenne (modification modèle Transaction, UI de split)

---

### 2. **🔁 Règles automatiques de catégorisation**

**Description:**
Créer des règles pour catégoriser automatiquement les transactions selon des patterns.

**Exemples:**
```
SI description contient "Migros" ALORS Catégorie = Alimentation
SI description contient "SBB" ALORS Catégorie = Transport
SI description contient "Netflix" ALORS Catégorie = Loisirs
SI montant > 1000 CHF ALORS Tag = #grosse-dépense
```

**Bénéfices:**
- ✅ Gain de temps énorme sur saisie
- ✅ Cohérence des catégories
- ✅ Import bancaire automatisé

**Complexité:** Moyenne (nouveau modèle Rules, pattern matching)

---

### 3. **📤 Export PDF/Excel mensuel**

**Description:**
Générer automatiquement un rapport mensuel professionnel exportable.

**Contenu du rapport:**
- Résumé revenus/dépenses
- Graphiques par catégorie
- Liste détaillée des transactions
- Comparaison avec mois précédent
- Progression vers objectifs

**Formats:**
- PDF (pour archivage)
- Excel (pour manipulation)
- CSV (pour import externe)

**Bénéfices:**
- ✅ Comptabilité/déclaration impôts
- ✅ Archivage légal
- ✅ Partage avec comptable

**Complexité:** Faible (librairies existantes: ReportLab, openpyxl)

---

### 4. **🏷️ Tags personnalisés**

**Description:**
Système de tags flexibles en complément des catégories fixes.

**Différence avec catégories:**
```
Catégories: Classification unique et fixe
  └─ Une transaction = 1 catégorie

Tags: Labels multiples et flexibles
  └─ Une transaction = plusieurs tags
```

**Exemples:**
```
Transaction: "Restaurant Italien - 85 CHF"
  Catégorie: Loisirs
  Tags: #vacances #anniversaire #taxdeductible
```

**Bénéfices:**
- ✅ Double classification
- ✅ Recherche avancée
- ✅ Filtres complexes

**Complexité:** Moyenne (modèle Tag, relation ManyToMany)

---

### 5. **👥 Budgets partagés** (pour couples/colocataires)

**Description:**
Permettre à 2+ utilisateurs de partager un compte et un budget commun.

**Fonctionnalités:**
- Compte "Commun" visible par tous les membres
- Chacun peut ajouter des transactions
- Historique des contributions de chacun
- Règlement automatique "qui doit quoi"
- Notifications push pour grosses dépenses

**Cas d'usage:**
```
Couple:
  ├─ Compte Personnel Alice
  ├─ Compte Personnel Bob
  └─ Compte Commun (partagé)
       ├─ Budget Courses: 600 CHF
       ├─ Budget Loyer: 1500 CHF
       └─ Alice a payé 800 → Bob doit 400
```

**Bénéfices:**
- ✅ Gestion familiale simplifiée
- ✅ Transparence financière
- ✅ Évite conflits d'argent

**Complexité:** Élevée (permissions, partage, sync)

---

### 6. **🔔 Notifications configurables**

**Description:**
Système d'alertes personnalisables par email/push.

**Types d'alertes:**
- 🔴 Budget atteint à 80%
- 🟠 Budget dépassé
- 🔵 Rappel transaction récurrente
- 🟣 Grosse dépense inhabituelle détectée
- 🟢 Objectif d'épargne atteint

**Configuration utilisateur:**
```
✅ Email: Oui/Non
✅ Push: Oui/Non (nécessite PWA ou app mobile)
✅ Fréquence: Immédiate / Quotidienne / Hebdomadaire
✅ Seuil personnalisé: "M'alerter si >500 CHF"
```

**Bénéfices:**
- ✅ Prévention dépassement budget
- ✅ Rappels automatiques
- ✅ Détection anomalies

**Complexité:** Moyenne (backend: Celery/tasks, frontend: notifications API)

---

### 7. **📸 Scan de reçus** (OCR)

**Description:**
Prendre photo du ticket de caisse → extraction automatique des données.

**Workflow:**
```
1. Photo du reçu avec smartphone
2. OCR extrait: montant, date, commerçant
3. Pré-remplit formulaire transaction
4. Utilisateur valide/corrige
5. Reçu archivé (attaché à transaction)
```

**Technologies:**
- Tesseract OCR (open source)
- Google Vision API (payant mais précis)
- Azure Form Recognizer

**Bénéfices:**
- ✅ Saisie ultra-rapide
- ✅ Aucune erreur de frappe
- ✅ Archive numérique des reçus

**Complexité:** Élevée (OCR, upload images, stockage)

---

### 8. **🎭 Mode "Enveloppes budgétaires"**

**Description:**
Méthode budgétaire populaire: allouer une somme fixe par catégorie en début de mois.

**Concept:**
```
Début du mois:
  ├─ Enveloppe Alimentation: 500 CHF
  ├─ Enveloppe Transport: 200 CHF
  └─ Enveloppe Loisirs: 300 CHF

Pendant le mois:
  ├─ Achat 45 CHF → Alimentation: 455 CHF restant
  └─ Quand enveloppe vide → STOP dépenser!
```

**Visualisation:**
- Barre de progression par enveloppe
- Couleur rouge quand proche de vide
- Suggestion réallocation si trop de surplus

**Bénéfices:**
- ✅ Très visuel et intuitif
- ✅ Discipline budgétaire forte
- ✅ Populaire (méthode Dave Ramsey)

**Complexité:** Faible (variante d'affichage des budgets)

---

## 🌟 **SUGGESTIONS AVANCÉES**

### 9. **🔮 Prévisions intelligentes**

**Description:**
Analyse de l'historique pour prédire l'avenir et alerter des anomalies.

**Fonctionnalités:**
```
📊 Prévisions:
  - "Si vous continuez ce rythme, vous économiserez 1200 CHF cette année"
  - "Votre budget Alimentation sera dépassé le 23 du mois"
  - "Objectif Vacances atteint dans 8 mois (au lieu de 12)"

⚠️ Alertes anomalies:
  - "Dépenses inhabituellement élevées ce mois (+35% vs moyenne)"
  - "Vous n'avez pas encore reçu votre salaire ce mois"
  - "Transaction suspecte: 3 paiements identiques le même jour"

💡 Suggestions:
  - "Vous pourriez économiser 50 CHF/mois en changeant d'abonnement"
  - "Budget Loisirs jamais utilisé: réallouer vers Alimentation?"
```

**Bénéfices:**
- ✅ Proactif vs réactif
- ✅ Évite mauvaises surprises
- ✅ Optimisation continue

**Complexité:** Élevée (ML, statistiques, calculs complexes)

---

### 10. **📅 Calendrier de paiements**

**Description:**
Vue calendrier avec toutes les échéances et transactions futures.

**Affichage:**
```
Février 2026:
  01: Salaire (+5000 CHF)
  05: Loyer (-1200 CHF)
  15: Assurance (-150 CHF)
  20: Netflix (-15 CHF)
  25: Courses estimées (-400 CHF)

Solde prévu fin de mois: 1850 CHF
```

**Fonctionnalités:**
- Drag & drop pour déplacer échéances
- Clic pour créer transaction
- Export iCal/Google Calendar
- Rappels automatiques

**Bénéfices:**
- ✅ Vision globale du mois
- ✅ Évite oublis de paiement
- ✅ Planification anticipée

**Complexité:** Moyenne (UI calendrier, gestion dates)

---

### 11. **🌍 Multi-devises avec conversion**

**Description:**
Gérer des comptes et transactions en différentes devises avec conversion automatique.

**Cas d'usage:**
```
Utilisateur:
  ├─ Compte Courant Suisse: CHF
  ├─ Compte Épargne France: EUR
  └─ Carte Crypto: USD

Conversion automatique:
  - Taux de change du jour (API)
  - Historique des taux
  - Dashboard unifié en CHF (devise principale)
```

**Fonctionnalités:**
- API taux de change (exchangerate.host, gratuit)
- Sélection devise par transaction
- Graphiques multi-devises
- Alerte variation taux

**Bénéfices:**
- ✅ Expatriés
- ✅ Voyages fréquents
- ✅ Investissements internationaux

**Complexité:** Moyenne (API externe, calculs conversion)

---

### 12. **🎨 Thèmes/Personnalisation avancée**

**Description:**
Dashboard personnalisable avec widgets drag & drop.

**Options:**
```
Widgets disponibles:
  ├─ Résumé mensuel (obligatoire)
  ├─ Graphique dépenses
  ├─ Liste transactions récentes
  ├─ Objectifs d'épargne
  ├─ Budgets en cours
  └─ Alertes/Notifications

Utilisateur choisit:
  ✅ Quels widgets afficher
  ✅ Ordre d'affichage (drag & drop)
  ✅ Taille des widgets
  ✅ Sauvegarde plusieurs "vues" (Perso/Pro/Famille)
```

**Thèmes visuels:**
- Minimaliste (peu d'infos)
- Détaillé (toutes les stats)
- Graphique (focus charts)

**Bénéfices:**
- ✅ Adapté à chaque utilisateur
- ✅ Focus sur ce qui compte
- ✅ UX personnalisée

**Complexité:** Élevée (drag & drop, sauvegarde layout)

---

### 13. **🤝 Import bancaire automatique**

**Description:**
Connexion directe avec banques pour import automatique des transactions.

**Technologies:**
- Open Banking API (PSD2 en Europe)
- Plaid API (USA/Canada)
- Tink API (Europe)
- Salt Edge (global)

**Workflow:**
```
1. Utilisateur connecte sa banque (OAuth)
2. API récupère transactions quotidiennement
3. Règles automatiques catégorisent
4. Utilisateur valide/corrige
5. Sync continue
```

**Bénéfices:**
- ✅ Zéro saisie manuelle
- ✅ Toujours à jour
- ✅ Aucun oubli

**Complexité:** Très élevée (sécurité, APIs bancaires, régulation)

---

### 14. **📊 Comparaison avec moyennes**

**Description:**
Comparer ses dépenses avec des références (moyennes nationales, son historique).

**Affichages:**
```
Alimentation:
  Vous: 650 CHF/mois
  Moyenne Suisse: 520 CHF/mois
  → Vous dépensez 25% de plus

Transport:
  Vous: 150 CHF/mois
  Moyenne Suisse: 280 CHF/mois
  → Vous économisez 46% 💚

Comparaison vs votre historique:
  Ce mois: 2300 CHF
  Moyenne (6 derniers mois): 1950 CHF
  → +18% ce mois ⚠️
```

**Sources données:**
- Office fédéral de la statistique (OFS)
- Données anonymisées utilisateurs (opt-in)
- Historique personnel

**Bénéfices:**
- ✅ Contextualisation des dépenses
- ✅ Gamification
- ✅ Motivation à optimiser

**Complexité:** Moyenne (données externes, calculs stats)

---

### 15. **🔐 Webhooks & API publique**

**Description:**
API pour intégrations tierces et automatisations.

**Cas d'usage:**
```
IFTTT/Zapier:
  - Quand budget dépassé → Envoyer SMS
  - Quand salaire reçu → Tweet "💰 C'est jour de paie!"
  - Quand objectif atteint → Célébration Slack

Custom Apps:
  - App mobile native iOS/Android
  - Extension navigateur
  - Widget desktop

Webhooks:
  - POST vers URL externe quand événement
  - Intégration Notion/Airtable
  - Sync avec autres outils financiers
```

**Endpoints API:**
```
GET    /api/v1/transactions
POST   /api/v1/transactions
GET    /api/v1/budgets
POST   /api/v1/budgets
GET    /api/v1/stats/monthly
...
```

**Bénéfices:**
- ✅ Écosystème d'apps
- ✅ Automatisations avancées
- ✅ Intégrations sur mesure

**Complexité:** Moyenne (API déjà existe, ajouter webhooks)

---

## ✅ **IMPLÉMENTÉ**

### ✓ Gestion du salaire récurrent

**Date:** 2026-02-13

**Description:**
Créer automatiquement une transaction récurrente mensuelle pour le salaire défini dans le profil utilisateur.

**Endpoint:** `POST /api/v1/profile/setup_recurring_salary/`

**Fichiers modifiés:**
- `backend/authentication/views.py` (nouveau endpoint)

---

### ✓ Épargne obligatoire vs objectifs ciblés

**Date:** 2026-02-13

**Description:**
Distinction entre épargne mensuelle générale (fond d'urgence) et objectifs d'épargne ciblés (vacances, achat). L'épargne obligatoire impacte maintenant le budget mensuel.

**Champ ajouté:** `Budget.is_mandatory_savings`

**Fichiers modifiés:**
- `backend/budgets/models.py` (nouveau champ)
- `backend/budgets/serializers.py` (ajout dans serializers)
- `backend/budgets/views.py` (calcul dashboard)
- Migration: `budgets/migrations/0006_budget_is_mandatory_savings.py`

---

## 📝 **NOTES**

- Ces suggestions sont des **idées** à considérer, pas des obligations
- Prioriser selon vos besoins et le feedback utilisateurs
- Certaines nécessitent des technologies tierces (APIs, services payants)
- Évaluer complexité vs valeur ajoutée avant implémentation

---

**Dernière mise à jour:** 2026-02-13
**Source:** Claude Sonnet 4.5
