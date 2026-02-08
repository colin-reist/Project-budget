# Projet : Application Web de Suivi de Budget

## Vue d'ensemble

Application web complète permettant la gestion et le suivi détaillé de budgets personnels avec support multi-comptes et analyse graphique.

---

## Fonctionnalités principales

### 1. Gestion des budgets

- Création de budgets personnalisés avec montant cible (ex: 500€ pour matériel sono/musique)
- Définition d'une date limite pour atteindre l'objectif
- Calcul automatique du montant mensuel à épargner en fonction de la date cible
- Suivi de la progression vers les objectifs fixés

### 2. Transactions automatiques

- **Paiements récurrents** : configuration de dépenses régulières (loyer, abonnements, etc.)
- **Revenus récurrents** : enregistrement des salaires et autres revenus périodiques
- Gestion des intervalles personnalisables (hebdomadaire, mensuel, annuel, etc.)

### 3. Gestion des transactions

- Ajout manuel de paiements et de recettes
- Système de catégorisation des transactions
- Création et personnalisation de catégories selon les besoins
- Fonction de recherche avancée dans l'historique des transactions

### 4. Multi-comptes

- Gestion de plusieurs comptes bancaires simultanément
- Support de différents types de comptes : courant, épargne, etc.
- Vue consolidée et vues individuelles par compte

### 5. Visualisation et rapports

- **Graphiques de dépenses** : analyse visuelle de la répartition des dépenses par catégorie
- **Graphiques de progression** : suivi de l'évolution des budgets dans le temps
- **Graphiques des comptes** : évolution du solde de chaque compte
- Tableaux de bord personnalisables

### 6. API et intégration mobile

- API RESTful sécurisée pour l'accès aux données
- Authentification par token pour garantir la sécurité
- Possibilité d'envoyer des transactions depuis un appareil mobile
- Documentation API pour faciliter l'intégration

### 7. Sécurité et authentification

- Système de connexion sécurisé via passkeys (WebAuthn)
- Support des gestionnaires de mots de passe modernes (Proton Pass, etc.)
- Authentification sans mot de passe pour une sécurité maximale
- Protection des données sensibles
- Gestion des sessions via JWT
- Tokens d'API révocables pour l'accès mobile

---

## Technologies envisagées

- **Frontend** : Nuxt.js avec Nuxt UI
- **Backend** : Django avec Django REST Framework
- **Base de données** : PostgreSQL
- **Authentification** : 
  - WebAuthn/FIDO2 pour les passkeys (Proton Pass)
  - JWT pour la gestion des sessions et tokens API
- **Graphiques** : D3.js

---

## Objectifs du projet

1. Centraliser la gestion financière personnelle
2. Offrir une vision claire et en temps réel de la situation budgétaire
3. Faciliter l'atteinte d'objectifs d'épargne
4. Automatiser le suivi des revenus et dépenses récurrents
5. Permettre une analyse approfondie des habitudes de consommation
6. Garantir la sécurité et la confidentialité des données financières

---

## Prochaines étapes

- [ ] Définir l'architecture technique
- [ ] Concevoir les maquettes de l'interface utilisateur
- [ ] Modéliser la base de données
- [ ] Développer le MVP (Minimum Viable Product)
- [ ] Implémenter les fonctionnalités avancées
- [ ] Tests et déploiement
