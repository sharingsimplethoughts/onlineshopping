# Generated by Django 2.1.5 on 2019-07-24 06:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_exchangereason'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exchangereason',
            old_name='return_description',
            new_name='exchange_description',
        ),
    ]