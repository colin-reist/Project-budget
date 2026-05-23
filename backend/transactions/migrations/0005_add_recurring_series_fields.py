import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0004_transaction_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='recurring_series_id',
            field=models.UUIDField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name='ID de série récurrente',
                help_text='UUID partagé par le template et toutes ses instances générées'
            ),
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_series_template',
            field=models.BooleanField(
                default=False,
                verbose_name='Template de série',
                help_text='True uniquement pour la transaction maître de la série récurrente'
            ),
        ),
    ]
