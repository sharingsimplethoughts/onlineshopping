# Generated by Django 2.1.5 on 2019-04-10 12:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20190305_1819'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customeraddress',
            name='user',
        ),
        migrations.DeleteModel(
            name='CustomerAddress',
        ),
    ]
