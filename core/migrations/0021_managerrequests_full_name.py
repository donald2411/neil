# Generated by Django 3.2 on 2023-06-18 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_alter_withdraw_withdraw_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='managerrequests',
            name='full_name',
            field=models.CharField(default='name', max_length=200),
            preserve_default=False,
        ),
    ]