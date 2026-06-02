from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0007_savingsgoal_display_fields'),
        ('transactions', '0005_add_recurring_series_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='refund_budget',
            field=models.ForeignKey(
                blank=True,
                help_text="Si renseigné, ce revenu réduit les dépenses de cette enveloppe budget",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='refund_transactions',
                to='budgets.budget',
                verbose_name="Rembourse l'enveloppe",
            ),
        ),
    ]
