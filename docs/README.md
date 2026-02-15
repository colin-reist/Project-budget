# 📚 Documentation Budget Tracker

Bienvenue dans la documentation complète du projet Budget Tracker.

---

## 📖 Guide de Démarrage

### Nouveau sur le projet ?

1. **[Retour au README principal](../README.md)** - Vue d'ensemble du projet
2. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Comprendre l'architecture technique
3. **[DATABASE.md](./DATABASE.md)** - Schéma de la base de données
4. **Choisir votre méthode d'installation :**
   - [Installation avec Docker](#-docker) (Recommandé)
   - [Déploiement sur Raspberry Pi](#-raspberry-pi)

---

## 🚀 Déploiement

**[DEPLOYMENT.md](./DEPLOYMENT.md)** - Guide complet de déploiement Docker

Tout ce que vous devez savoir sur Docker pour ce projet :

- ⚡ Quick Start (3 commandes)
- 🔄 Mises à jour sans perte de données
- 💾 Gestion des volumes et persistance
- 🗄️ Sauvegarde et restauration de la base de données
- 📊 Commandes utiles et debugging
- 🔐 Configuration de sécurité
- 🐛 Troubleshooting

**Idéal pour :**
- Développement local
- Déploiement sur serveur VPS
- Tests et CI/CD

---

## 🍓 Raspberry Pi

**[RASPBERRY_PI.md](./RASPBERRY_PI.md)** - Déploiement sur Raspberry Pi

Guide complet pour transformer votre Raspberry Pi en serveur web professionnel :

- ⚡ Installation automatisée (script bash)
- 🔧 Installation manuelle (étape par étape)
- 🌐 Configuration DNS avec Infomaniak
- 🔐 HTTPS automatique avec Caddy + Let's Encrypt
- 📊 Monitoring et maintenance
- 🆘 Dépannage

**Idéal pour :**
- Auto-hébergement à la maison
- Serveur personnel 24/7
- Apprentissage DevOps
- Solution économique

---

## 🏗️ Architecture

**[ARCHITECTURE.md](./ARCHITECTURE.md)** - Architecture technique détaillée

Comprendre la structure du projet :

- Stack technologique (Django, Nuxt, PostgreSQL)
- Architecture logicielle (patterns et design)
- Flux de données et communication
- Sécurité et authentification (WebAuthn, JWT)
- Diagrammes et schémas

**Utile pour :**
- Développeurs contribuant au projet
- Comprendre les choix techniques
- Étendre les fonctionnalités

---

## 🗄️ Base de Données

**[DATABASE.md](./DATABASE.md)** - Schéma et modèles de données

Documentation complète de la base de données :

- Schéma complet (diagrammes Mermaid)
- Modèles Django détaillés
- Relations entre tables
- Index et contraintes
- Exemples de requêtes

**Utile pour :**
- Comprendre le modèle de données
- Écrire des requêtes optimisées
- Ajouter de nouveaux modèles
- Migrations de base de données

---

## 🔌 API

**[API.md](./API.md)** - Documentation de l'API REST

Documentation complète des endpoints :

- Authentification et autorisation
- Endpoints CRUD pour tous les modèles
- Exemples de requêtes et réponses
- Codes d'erreur
- Rate limiting et pagination
- Tokens API pour applications mobiles

**Utile pour :**
- Développer des clients (web, mobile, CLI)
- Intégrations tierces
- Tests automatisés
- Documentation API publique

---

## 🎨 Design & UX

**[UX_AUDIT.md](./UX_AUDIT.md)** - Audit et recommandations UX

Documentation des améliorations UX à implémenter :

- 🔴 Problèmes critiques (onboarding, navigation, feedback)
- 🟠 Problèmes importants (dashboard, formulaires, accessibilité)
- 🟡 Améliorations souhaitables (mobile, recherche, dark mode)
- 🔵 Améliorations avancées (insights, personnalisation)
- 📊 Score UX et priorisation

**Utile pour :**
- Améliorer l'expérience utilisateur
- Prioriser les améliorations UX
- Référence lors du développement de nouvelles fonctionnalités
- Audit d'accessibilité (WCAG)

### 🎉 **Améliorations UX Implémentées (Nouveau !)**

Les améliorations UX prioritaires (P0 et P1) ont été implémentées ! Documentation complète :

**Documents disponibles :**
- **[UX_QUICK_START.md](./UX_QUICK_START.md)** - Démarrage rapide (5 min)
- **[UX_IMPROVEMENTS_IMPLEMENTED.md](./UX_IMPROVEMENTS_IMPLEMENTED.md)** - Détails techniques complets
- **[UX_DEVELOPER_GUIDE.md](./UX_DEVELOPER_GUIDE.md)** - Guide développeur
- **[UX_TESTING_CHECKLIST.md](./UX_TESTING_CHECKLIST.md)** - 50+ tests à valider
- **[CHANGELOG_UX.md](./CHANGELOG_UX.md)** - Historique des changements

**Améliorations implémentées (8/8) :**
- ✅ Tooltips explicatifs sur données futures
- ✅ Navigation réorganisée (dropdown Configuration)
- ✅ Empty states engageants avec illustrations
- ✅ Loading skeletons professionnels
- ✅ Onboarding wizard 4 étapes
- ✅ Raccourcis clavier (Ctrl+N, ?, Escape)
- ✅ Validation temps réel formulaires
- ✅ Bottom navigation mobile

**Score UX : 6.2/10 → 8.4/10 (+35%)** 🚀

---

## 💡 Idées de Fonctionnalités

**[FEATURE_IDEAS.md](./FEATURE_IDEAS.md)** - Backlog d'idées et suggestions

Catalogue de fonctionnalités potentielles suggérées par l'IA :

- 🎯 15 suggestions prioritaires (split transactions, règles auto, export PDF, tags, etc.)
- 🌟 7 suggestions avancées (prévisions IA, calendrier, multi-devises, etc.)
- ✅ Historique des fonctionnalités implémentées

**Utile pour :**
- Inspiration pour nouvelles features
- Planification du roadmap produit
- Évaluation de la complexité
- Priorisation par valeur ajoutée

---

## 🚀 Déploiement

**[DEPLOYMENT.md](./DEPLOYMENT.md)** - Guide de déploiement en production

Déployer en production :

- Checklist de sécurité
- Variables d'environnement
- Configuration HTTPS
- Reverse proxy (Nginx/Caddy)
- Optimisations de performance
- Monitoring et logs
- Backup automatique

**Utile pour :**
- Mise en production
- DevOps et SRE
- Optimisation des performances
- Gestion de l'infrastructure

---

## 🎯 Par Cas d'Usage

### Je veux développer localement

1. Lire le [README principal](../README.md#-installation-rapide)
2. Suivre la section "Développement local"
3. Consulter [ARCHITECTURE.md](./ARCHITECTURE.md) pour comprendre le code
4. Utiliser [API.md](./API.md) pour tester les endpoints

### Je veux déployer avec Docker

1. Lire [DOCKER.md](./DOCKER.md)
2. Suivre le Quick Start
3. Configurer `.env` (voir [DEPLOYMENT.md](./DEPLOYMENT.md))
4. Lancer `docker-compose up -d`

### Je veux déployer sur Raspberry Pi

1. Lire [RASPBERRY_PI.md](./RASPBERRY_PI.md)
2. Utiliser le script d'installation automatisée
3. Configurer le DNS chez Infomaniak
4. Activer HTTPS avec Caddy

### Je veux contribuer au projet

1. Lire [ARCHITECTURE.md](./ARCHITECTURE.md) - Comprendre la structure
2. Lire [DATABASE.md](./DATABASE.md) - Comprendre les modèles
3. Lire [API.md](./API.md) - Comprendre les endpoints
4. Fork et créer une Pull Request

### Je veux créer une app mobile

1. Lire [API.md](./API.md) - Documentation complète des endpoints
2. Générer un token API dans l'interface web
3. Utiliser les endpoints REST
4. Gérer l'authentification par token

### Je veux améliorer l'UX/UI

1. Lire [UX_AUDIT.md](./UX_AUDIT.md) - Audit complet et recommandations
2. Consulter la section priorisation (P0, P1, P2)
3. Choisir un point à implémenter
4. Tester avec de vrais utilisateurs

---

## 📊 Schémas et Diagrammes

- **Architecture système** → [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Schéma de base de données** → [DATABASE.md](./DATABASE.md)
- **Flux d'authentification** → [ARCHITECTURE.md](./ARCHITECTURE.md#authentification)
- **Diagramme réseau Docker** → [DOCKER.md](./DOCKER.md)

---

## 🆘 Besoin d'Aide ?

### Problèmes fréquents

- **Docker ne démarre pas** → [DOCKER.md - Troubleshooting](./DOCKER.md#-troubleshooting)
- **HTTPS ne fonctionne pas** → [RASPBERRY_PI.md - Dépannage](./RASPBERRY_PI.md#-dépannage)
- **Erreurs de base de données** → [DATABASE.md](./DATABASE.md)
- **Erreurs API** → [API.md](./API.md)

### Support

- 📧 Email : votre-email@example.com
- 🐛 Issues : [GitHub Issues](https://github.com/votre-utilisateur/budget-tracker/issues)
- 💬 Discussions : [GitHub Discussions](https://github.com/votre-utilisateur/budget-tracker/discussions)

---

## 📝 Structure de la Documentation

```
docs/
├── README.md                          ← Vous êtes ici (Index)
│
├── 🏗️ ARCHITECTURE.md                ← Architecture technique
├── 🔌 API.md                          ← Documentation API REST
├── 🗄️ DATABASE.md                     ← Schéma de base de données
├── 💡 FEATURE_IDEAS.md                ← Backlog d'idées de fonctionnalités
│
├── 🚀 DEPLOYMENT.md                   ← Guide de déploiement Docker
├── 🍓 RASPBERRY_PI.md                 ← Déploiement Raspberry Pi spécifique
│
├── 🎨 UX_AUDIT.md                     ← Audit et recommandations UX
├── ⚡ UX_QUICK_START.md               ← Démarrage rapide améliorations UX
├── 🔧 UX_IMPROVEMENTS_IMPLEMENTED.md  ← Détails techniques implémentation
├── 📖 UX_DEVELOPER_GUIDE.md           ← Guide développeur UX
├── ✅ UX_TESTING_CHECKLIST.md         ← Checklist de tests UX
└── 📝 CHANGELOG_UX.md                 ← Historique changements UX
```

---

## 🔄 Mises à Jour

Cette documentation est maintenue à jour avec le code. Si vous trouvez des erreurs ou des informations obsolètes, n'hésitez pas à ouvrir une issue ou une pull request.

**Dernière mise à jour : 2026-02-14** (Ajout documentation UX complète)

---

**Happy coding! 💻🚀**
