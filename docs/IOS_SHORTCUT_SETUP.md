# 📱 Configuration du Raccourci iOS

Guide complet pour configurer un raccourci iOS Shortcuts afin d'ajouter des transactions à votre compte depuis votre iPhone.

## 📋 Table des matières

1. [Créer un API Token](#1-créer-un-api-token)
2. [Configurer le Raccourci iOS](#2-configurer-le-raccourci-ios)
3. [Tester le Raccourci](#3-tester-le-raccourci)
4. [Déboguer les Erreurs](#4-déboguer-les-erreurs)

---

## 1. Créer un API Token

### Option A : Via Postman, Insomnia ou curl

**Étape 1 : Se connecter et obtenir un JWT**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "votre_username",
    "password": "votre_password"
  }'
```

Réponse :
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Étape 2 : Créer un API Token**

```bash
curl -X POST http://localhost:8000/api/v1/auth/tokens/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_ACCESS_TOKEN" \
  -d '{
    "name": "iPhone Shortcut"
  }'
```

Réponse :
```json
{
  "id": 1,
  "name": "iPhone Shortcut",
  "token": "tk_abcd1234efgh5678ijkl9012mnop3456",
  "created_at": "2026-02-15T10:30:00Z"
}
```

**⚠️ IMPORTANT : Sauvegardez ce token immédiatement ! Il ne sera plus jamais affiché.**

---

## 2. Configurer le Raccourci iOS

### Étape 1 : Créer un nouveau raccourci

1. Ouvrez l'app **Raccourcis** sur votre iPhone
2. Appuyez sur **+** pour créer un nouveau raccourci
3. Nommez-le "Ajouter Dépense"

### Étape 2 : Ajouter les actions

#### Action 1 : Demander le montant
- Ajouter **"Demander une saisie"**
- Question : `Montant de la dépense`
- Type d'entrée : **Nombre**
- Variable : `Montant`

#### Action 2 : Demander la description
- Ajouter **"Demander une saisie"**
- Question : `Description (ex: Café)`
- Type d'entrée : **Texte**
- Variable : `Description`

#### Action 3 : Demander la catégorie (optionnel)
- Ajouter **"Demander une saisie"**
- Question : `Catégorie (ex: Alimentation)`
- Type d'entrée : **Texte**
- Variable : `Catégorie`

#### Action 4 : Envoyer la requête HTTP
- Ajouter **"Obtenir le contenu d'une URL"**

**Configuration de la requête :**

| Paramètre | Valeur |
|-----------|--------|
| **URL** | `http://VOTRE_IP:8000/api/v1/ios/transaction/` |
| **Méthode** | `POST` |
| **En-têtes** | `Authorization: Bearer tk_votre_token_ici` |
| **Corps de la requête** | `JSON` |

**Corps JSON :**
```json
{
  "amount": [Variable: Montant],
  "label": "[Variable: Description]",
  "category": "[Variable: Catégorie]"
}
```

#### Action 5 : Afficher la confirmation
- Ajouter **"Afficher la notification"**
- Texte : `Transaction ajoutée : [Description] - [Montant] CHF`

### Configuration visuelle du raccourci

```
┌─────────────────────────────────────┐
│ Demander une saisie                 │
│ Question: Montant de la dépense     │
│ Type: Nombre                        │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ Demander une saisie                 │
│ Question: Description               │
│ Type: Texte                         │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ Demander une saisie                 │
│ Question: Catégorie                 │
│ Type: Texte                         │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ Obtenir le contenu d'une URL        │
│ URL: http://192.168.1.X:8000/...    │
│ Méthode: POST                       │
│ En-têtes:                           │
│   Authorization: Bearer tk_...      │
│ Corps:                              │
│   {                                 │
│     "amount": [Montant],            │
│     "label": "[Description]",       │
│     "category": "[Catégorie]"       │
│   }                                 │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ Afficher la notification            │
│ Transaction ajoutée !               │
└─────────────────────────────────────┘
```

---

## 3. Tester le Raccourci

### Test 1 : Vérifier que votre serveur est accessible

Depuis Safari sur votre iPhone, accédez à :
```
http://VOTRE_IP:8000/api/v1/auth/tokens/
```

Si vous voyez une erreur de connexion, vérifiez :
- Votre iPhone est sur le même réseau WiFi que votre ordinateur
- Le serveur backend est bien démarré (`python manage.py runserver 0.0.0.0:8000`)
- Le pare-feu Windows autorise les connexions sur le port 8000

### Test 2 : Lancer le raccourci

1. Exécutez le raccourci
2. Entrez : `12.50` (montant)
3. Entrez : `Café` (description)
4. Entrez : `Alimentation` (catégorie)
5. Vous devriez voir une notification de confirmation

### Test 3 : Vérifier la transaction

Connectez-vous à votre application web et vérifiez que la transaction apparaît avec :
- Montant : 12.50 CHF
- Description : Café
- Type : Dépense
- Source : iOS

---

## 4. Déboguer les Erreurs

### ❌ Erreur 400 Bad Request

**Causes possibles :**

#### 1. Format JSON incorrect
- **Vérifiez** que le corps de la requête est bien en JSON
- **Dans Raccourcis** : Assurez-vous d'avoir sélectionné "JSON" comme type de corps

#### 2. Token invalide
```json
{
  "error": "Token invalide"
}
```
- **Solution** : Créez un nouveau token via l'API

#### 3. Champs manquants ou invalides
```json
{
  "error": "Le montant est requis."
}
```
- **Vérifiez** que vous passez bien `amount` et `label`
- **Vérifiez** que `amount` est un nombre positif

#### 4. Aucun compte actif
```json
{
  "error": "Aucun compte actif trouvé."
}
```
- **Solution** : Créez au moins un compte actif via l'application web

### ❌ Erreur 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Solution** : Vérifiez le header Authorization
- Format correct : `Authorization: Bearer tk_votre_token`
- Pas d'espace avant "Bearer"
- Le token commence par `tk_`

### ❌ Erreur 207 Multi-Status (Catégorie inconnue)

```json
{
  "id": 123,
  "amount": "12.50",
  "description": "Café",
  "category": null,
  "warning": "Catégorie \"Nourriture\" non trouvée. Transaction créée sans catégorie."
}
```

**C'est normal !** La transaction a été créée, mais :
- La catégorie n'existe pas ou est mal orthographiée
- Une alerte a été créée pour que vous puissiez catégoriser la transaction plus tard
- Consultez `/api/v1/alerts/` pour voir les alertes

### ❌ Erreur de connexion (Cannot connect)

**Solutions :**

1. **Vérifiez l'adresse IP** :
```bash
# Sur Windows
ipconfig
# Cherchez "Adresse IPv4" de votre carte WiFi
```

2. **Démarrez le serveur sur 0.0.0.0** :
```bash
python manage.py runserver 0.0.0.0:8000
```

3. **Autorisez le pare-feu Windows** :
- Panneau de configuration → Pare-feu Windows
- Autoriser une application → Python

4. **Vérifiez ALLOWED_HOSTS** :
```python
# backend/.env
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.X
```

---

## 5. Améliorations Possibles

### Raccourci avec Menu de Catégories

Remplacez "Demander une saisie" par "Choisir dans la liste" :

```
Catégories :
- Alimentation
- Transport
- Logement
- Loisirs
- Shopping
- Santé
- Autre
```

### Raccourci avec Montant Prédéfini

Créez plusieurs raccourcis :
- "Café" → 5 CHF, catégorie "Alimentation"
- "Essence" → 80 CHF, catégorie "Transport"
- "Restaurant" → demander montant, catégorie "Alimentation"

### Widget sur l'écran d'accueil

Ajoutez le raccourci comme widget pour un accès rapide.

---

## 6. Format de l'API

### Endpoint

```
POST /api/v1/ios/transaction/
```

### Headers requis

```
Authorization: Bearer tk_votre_token_ici
Content-Type: application/json
```

### Body (JSON)

```json
{
  "amount": 12.50,          // REQUIS - Nombre positif
  "label": "Description",   // REQUIS - Texte non vide
  "category": "Alimentation" // OPTIONNEL - Nom de catégorie
}
```

### Réponses

**201 Created** - Transaction créée avec succès
```json
{
  "id": 123,
  "amount": "12.50",
  "description": "Café",
  "category": "Alimentation",
  "date": "2026-02-15",
  "source": "ios"
}
```

**207 Multi-Status** - Transaction créée mais catégorie inconnue
```json
{
  "id": 123,
  "amount": "12.50",
  "description": "Café",
  "category": null,
  "warning": "Catégorie \"Nourriture\" non trouvée. Transaction créée sans catégorie."
}
```

**401 Unauthorized** - Token invalide ou manquant
```json
{
  "detail": "Invalid token."
}
```

**422 Unprocessable Entity** - Données invalides
```json
{
  "error": "Le montant est requis."
}
```

---

## 7. Sécurité

### ✅ Bonnes pratiques

- Ne partagez JAMAIS votre token API
- Créez un token spécifique pour chaque appareil
- Révoquez les tokens inutilisés via `/api/v1/auth/tokens/<id>/`
- Utilisez HTTPS en production (pas HTTP)

### 🔒 Pour la production

Quand vous déployez sur un serveur réel :

1. **Utilisez HTTPS** :
```
https://votre-domaine.com/api/v1/ios/transaction/
```

2. **Mettez à jour l'URL** dans le raccourci iOS

3. **Le token reste le même**, seule l'URL change

---

## 8. Exemple Complet de Test avec curl

```bash
# Test rapide depuis votre ordinateur
curl -X POST http://localhost:8000/api/v1/ios/transaction/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tk_votre_token_ici" \
  -d '{
    "amount": 15.50,
    "label": "Pizza",
    "category": "Alimentation"
  }'
```

Réponse attendue :
```json
{
  "id": 124,
  "amount": "15.50",
  "description": "Pizza",
  "category": "Alimentation",
  "date": "2026-02-15",
  "source": "ios"
}
```

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez les logs du serveur backend
2. Utilisez curl pour tester l'API directement
3. Vérifiez que votre compte a au moins un compte bancaire actif
4. Assurez-vous que les catégories existent dans votre base de données

---

**Dernière mise à jour** : 15 février 2026
