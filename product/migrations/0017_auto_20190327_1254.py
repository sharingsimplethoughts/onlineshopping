# Generated by Django 2.1.5 on 2019-03-27 07:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0016_auto_20190327_1253'),
    ]

    operations = [
        migrations.RenameField(
            model_name='colour',
            old_name='code',
            new_name='name',
        ),
    ]
