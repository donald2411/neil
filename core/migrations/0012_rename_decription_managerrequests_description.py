# Generated by Django 3.2 on 2023-05-31 18:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_managerrequests_decription'),
    ]

    operations = [
        migrations.RenameField(
            model_name='managerrequests',
            old_name='decription',
            new_name='description',
        ),
    ]
