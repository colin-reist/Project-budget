from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0006_budget_is_mandatory_savings'),
    ]

    operations = [
        migrations.AddField(
            model_name='savingsgoal',
            name='current_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15, verbose_name='Montant épargné'),
        ),
        migrations.AddField(
            model_name='savingsgoal',
            name='color',
            field=models.CharField(default='#2563eb', max_length=20, verbose_name='Couleur'),
        ),
        migrations.AddField(
            model_name='savingsgoal',
            name='icon',
            field=models.CharField(default='banknotes', max_length=50, verbose_name='Icône'),
        ),
        migrations.AddField(
            model_name='savingsgoal',
            name='note',
            field=models.CharField(blank=True, default='', max_length=300, verbose_name='Note'),
        ),
        migrations.AddField(
            model_name='savingsgoal',
            name='priority',
            field=models.IntegerField(default=0, verbose_name='Priorité'),
        ),
    ]
