"""
Mapping des noms de champs techniques vers des labels français user-friendly.
"""

FIELD_LABELS = {
    # Transaction fields
    'account': 'Compte',
    'destination_account': 'Compte de destination',
    'category': 'Catégorie',
    'amount': 'Montant',
    'description': 'Description',
    'date': 'Date',
    'transaction_type': 'Type de transaction',
    'is_planned': 'Transaction planifiée',

    # Account fields
    'name': 'Nom',
    'account_type': 'Type de compte',
    'balance': 'Solde',
    'initial_balance': 'Solde initial',
    'currency': 'Devise',
    'is_active': 'Compte actif',
    'credit_limit': 'Limite de crédit',

    # Category fields
    'category_type': 'Type de catégorie',
    'color': 'Couleur',
    'icon': 'Icône',
    'parent': 'Catégorie parente',

    # Budget fields
    'period': 'Période',
    'start_date': 'Date de début',
    'end_date': 'Date de fin',
    'target_amount': 'Montant cible',

    # Authentication fields
    'username': "Nom d'utilisateur",
    'password': 'Mot de passe',
    'email': 'Email',
    'old_password': 'Ancien mot de passe',
    'new_password': 'Nouveau mot de passe',

    # Common fields
    'user': 'Utilisateur',
    'created_at': 'Date de création',
    'updated_at': 'Date de modification',
    'non_field_errors': 'Erreur générale',
}


def get_field_label(field_name: str) -> str:
    """
    Retourne le label français d'un champ technique.
    Si le champ n'est pas dans le mapping, retourne le nom original.

    Args:
        field_name: Nom technique du champ

    Returns:
        Label français du champ
    """
    return FIELD_LABELS.get(field_name, field_name)
