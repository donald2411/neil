# Generated by Django 3.2 on 2023-06-20 16:53

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='leverage',
            field=models.DecimalField(decimal_places=4, default=Decimal('0.0000'), max_digits=6),
        ),
    ]