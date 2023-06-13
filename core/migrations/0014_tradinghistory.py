# Generated by Django 3.2 on 2023-06-13 10:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_account_trading_progress'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('trading_type', models.CharField(choices=[('p', 'profit'), ('l', 'lose')], max_length=2)),
                ('status', models.CharField(choices=[('approved', 'Approved'), ('declined', 'Declined'), ('pending', 'Pending')], default='pending', max_length=10)),
                ('currency', models.CharField(max_length=30)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
