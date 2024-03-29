# Generated by Django 3.0.7 on 2020-07-05 11:31

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0004_auto_20200621_0740'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='order',
            managers=[
                ('order', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(blank=True, choices=[(0, 'Aguardando Pagamento'), (1, 'Concluida'), (2, 'Cancelada')], default=0, verbose_name='Situação'),
        ),
    ]
