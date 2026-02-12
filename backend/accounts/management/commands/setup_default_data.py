"""
Commande Django pour créer des données par défaut pour un utilisateur.

Usage:
    python manage.py setup_default_data <username>
    python manage.py setup_default_data --all  # Pour tous les utilisateurs
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from accounts.models import Account
from categories.models import Category
from budgets.models import Budget, SavingsGoal
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée des catégories, comptes, budgets et objectifs d\'épargne par défaut pour un utilisateur'

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            nargs='?',
            type=str,
            help='Nom d\'utilisateur pour lequel créer les données par défaut'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Créer les données par défaut pour tous les utilisateurs qui n\'en ont pas'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la création même si l\'utilisateur a déjà des données'
        )

    def handle(self, *args, **options):
        if options['all']:
            users = User.objects.all()
            for user in users:
                if options['force'] or not self._user_has_data(user):
                    self._setup_user_data(user)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Données créées pour {users.count()} utilisateur(s)')
            )
        elif options['username']:
            try:
                user = User.objects.get(username=options['username'])
                if not options['force'] and self._user_has_data(user):
                    raise CommandError(
                        f'L\'utilisateur {user.username} a déjà des données. '
                        f'Utilisez --force pour écraser.'
                    )
                self._setup_user_data(user)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Données créées pour {user.username}')
                )
            except User.DoesNotExist:
                raise CommandError(f'Utilisateur "{options["username"]}" n\'existe pas')
        else:
            raise CommandError('Vous devez spécifier un username ou --all')

    def _user_has_data(self, user):
        """Vérifie si l'utilisateur a déjà des données"""
        return (
            Account.objects.filter(user=user).exists() or
            Category.objects.filter(user=user).exists() or
            Budget.objects.filter(user=user).exists()
        )

    def _setup_user_data(self, user):
        """Crée les données par défaut pour un utilisateur"""
        self.stdout.write(f'\n📊 Configuration pour {user.username}...')

        # 1. Créer les comptes
        self.stdout.write('  💳 Création des comptes...')
        compte_courant = Account.objects.create(
            user=user,
            name='Compte courant',
            account_type='checking',
            balance=Decimal('1000.00'),
            currency='CHF',
            description='Compte courant principal'
        )
        compte_epargne = Account.objects.create(
            user=user,
            name='Compte épargne',
            account_type='savings',
            balance=Decimal('5000.00'),
            currency='CHF',
            description='Compte d\'épargne'
        )
        self.stdout.write(self.style.SUCCESS('    ✓ 2 comptes créés'))

        # 2. Créer les catégories de dépenses
        self.stdout.write('  🏷️  Création des catégories...')

        # Catégories de dépenses
        cat_alimentation = Category.objects.create(
            user=user,
            name='Alimentation',
            type='expense',
            icon='i-heroicons-shopping-cart',
            color='orange'
        )
        cat_transport = Category.objects.create(
            user=user,
            name='Transport',
            type='expense',
            icon='i-heroicons-truck',
            color='blue'
        )
        cat_logement = Category.objects.create(
            user=user,
            name='Logement',
            type='expense',
            icon='i-heroicons-home',
            color='purple'
        )
        cat_loisirs = Category.objects.create(
            user=user,
            name='Loisirs',
            type='expense',
            icon='i-heroicons-film',
            color='pink'
        )
        cat_sante = Category.objects.create(
            user=user,
            name='Santé',
            type='expense',
            icon='i-heroicons-heart',
            color='red'
        )
        cat_autres = Category.objects.create(
            user=user,
            name='Autres dépenses',
            type='expense',
            icon='i-heroicons-ellipsis-horizontal',
            color='gray'
        )

        # Catégories de revenus
        cat_salaire = Category.objects.create(
            user=user,
            name='Salaire',
            type='income',
            icon='i-heroicons-banknotes',
            color='green'
        )
        cat_autres_revenus = Category.objects.create(
            user=user,
            name='Autres revenus',
            type='income',
            icon='i-heroicons-currency-dollar',
            color='emerald'
        )

        self.stdout.write(self.style.SUCCESS('    ✓ 8 catégories créées'))

        # 3. Créer les budgets
        self.stdout.write('  💰 Création des budgets...')

        today = date.today()
        start_of_month = date(today.year, today.month, 1)

        Budget.objects.create(
            user=user,
            category=cat_alimentation,
            name='Budget Alimentation',
            amount=Decimal('500.00'),
            period='monthly',
            start_date=start_of_month,
            alert_threshold=80
        )
        Budget.objects.create(
            user=user,
            category=cat_transport,
            name='Budget Transport',
            amount=Decimal('200.00'),
            period='monthly',
            start_date=start_of_month,
            alert_threshold=80
        )
        Budget.objects.create(
            user=user,
            category=cat_loisirs,
            name='Budget Loisirs',
            amount=Decimal('300.00'),
            period='monthly',
            start_date=start_of_month,
            alert_threshold=80
        )

        self.stdout.write(self.style.SUCCESS('    ✓ 3 budgets créés'))

        # 4. Créer un objectif d'épargne
        self.stdout.write('  🎯 Création d\'un objectif d\'épargne...')

        target_date = today + timedelta(days=365)  # Dans 1 an

        savings_goal = SavingsGoal.objects.create(
            user=user,
            label='Vacances d\'été',
            target_amount=Decimal('3000.00'),
            target_date=target_date,
            saving_amount=Decimal('250.00'),
            saving_frequency='monthly',
            status='active'
        )

        # Créer un budget lié à l'objectif d'épargne
        Budget.objects.create(
            user=user,
            name='Épargne vacances',
            amount=Decimal('250.00'),
            period='monthly',
            start_date=start_of_month,
            is_savings_goal=True,
            savings_goal=savings_goal,
            alert_threshold=90
        )

        self.stdout.write(self.style.SUCCESS('    ✓ 1 objectif d\'épargne créé'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Configuration terminée pour {user.username}!'))
        self.stdout.write('\n📋 Résumé:')
        self.stdout.write(f'  • 2 comptes (Courant: 1000 CHF, Épargne: 5000 CHF)')
        self.stdout.write(f'  • 8 catégories (6 dépenses, 2 revenus)')
        self.stdout.write(f'  • 3 budgets mensuels')
        self.stdout.write(f'  • 1 objectif d\'épargne (Vacances: 3000 CHF)')
