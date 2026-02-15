#!/usr/bin/env python
"""
Script pour créer un API Token pour iOS Shortcuts
Usage: python create_api_token.py
"""
import os
import django
import sys
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authentication.api_token import APIToken
from authentication.models import User


def create_token():
    print("=" * 60)
    print("  CRÉATION D'UN API TOKEN POUR iOS SHORTCUTS")
    print("=" * 60)
    print()

    # Demander le username
    username = input("Entrez votre nom d'utilisateur : ").strip()

    if not username:
        print("❌ Le nom d'utilisateur est requis.")
        return

    # Vérifier que l'utilisateur existe
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ L'utilisateur '{username}' n'existe pas.")
        print()
        print("Utilisateurs disponibles :")
        for u in User.objects.all():
            print(f"  - {u.username}")
        return

    # Demander le nom du token
    token_name = input("Nom du token (ex: iPhone Shortcut) : ").strip()

    if not token_name:
        token_name = "iOS Shortcut"

    # Créer le token
    api_token = APIToken(user=user, name=token_name)
    api_token.save()

    print()
    print("=" * 60)
    print("✅ TOKEN CRÉÉ AVEC SUCCÈS")
    print("=" * 60)
    print()
    print(f"Utilisateur : {user.username}")
    print(f"Nom du token : {api_token.name}")
    print(f"Date de création : {api_token.created_at}")
    print()
    print("🔑 VOTRE TOKEN API (SAUVEGARDEZ-LE MAINTENANT) :")
    print()
    print(f"    {api_token.token}")
    print()
    print("⚠️  IMPORTANT : Ce token ne sera plus jamais affiché !")
    print("    Copiez-le et collez-le dans votre raccourci iOS.")
    print()
    print("=" * 60)
    print()
    print("📱 CONFIGURATION DU RACCOURCI iOS")
    print()
    print("1. Ouvrez l'app Raccourcis sur votre iPhone")
    print("2. Dans la requête HTTP, ajoutez ce header :")
    print()
    print(f"   Authorization: Bearer {api_token.token}")
    print()
    print("3. URL de l'endpoint :")
    print()
    print("   http://VOTRE_IP:8000/api/v1/ios/transaction/")
    print()
    print("4. Corps JSON :")
    print()
    print('   {')
    print('     "amount": [Montant],')
    print('     "label": "[Description]",')
    print('     "category": "[Catégorie]"')
    print('   }')
    print()
    print("=" * 60)
    print()

    # Lister les tokens existants
    user_tokens = APIToken.objects.filter(user=user, is_active=True)
    if user_tokens.count() > 1:
        print(f"Tokens actifs pour {user.username} :")
        for t in user_tokens:
            print(f"  - {t.name} (créé le {t.created_at.strftime('%d/%m/%Y')})")
        print()


if __name__ == '__main__':
    try:
        create_token()
    except KeyboardInterrupt:
        print("\n\n❌ Annulé par l'utilisateur.")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
