from django.db import migrations, models
import decimal


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_userprofile_salary_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Téléphone'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date de naissance'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='language',
            field=models.CharField(default='fr-CH', max_length=10, verbose_name='Langue'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='timezone_pref',
            field=models.CharField(default='Europe/Zurich', max_length=50, verbose_name='Fuseau horaire'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='city',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Ville'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='country',
            field=models.CharField(default='CH', max_length=2, verbose_name='Pays'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='budget_start_day',
            field=models.IntegerField(default=1, verbose_name='Début du mois budgétaire'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='budget_rollover',
            field=models.BooleanField(default=True, verbose_name='Reporter les soldes'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='budget_roundup',
            field=models.BooleanField(default=False, verbose_name='Arrondi automatique'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='budget_roundup_amount',
            field=models.DecimalField(decimal_places=2, default=decimal.Decimal('1.00'), max_digits=5, verbose_name="Montant d'arrondi"),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='show_cents',
            field=models.BooleanField(default=True, verbose_name='Afficher les centimes'),
        ),
    ]
