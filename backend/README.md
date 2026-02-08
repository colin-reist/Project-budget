# Backend - Django API

## Structure (à créer)

```
backend/
├── config/              # Configuration du projet Django
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/        # Gestion des comptes bancaires
│   ├── transactions/    # Gestion des transactions
│   ├── budgets/         # Gestion des budgets
│   ├── categories/      # Gestion des catégories
│   └── authentication/  # WebAuthn + JWT
├── manage.py
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

## Prochaines étapes

1. Initialiser le projet Django
2. Créer les apps Django
3. Configurer les modèles selon DATABASE.md
4. Créer les serializers et views
5. Configurer les URLs
6. Implémenter WebAuthn
