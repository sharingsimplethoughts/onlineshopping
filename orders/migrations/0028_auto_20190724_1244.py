# Generated by Django 2.1.5 on 2019-07-24 07:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0027_auto_20190724_1227'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exchangecart',
            old_name='previous_order',
            new_name='order',
        ),
        migrations.RemoveField(
            model_name='exchangecart',
            name='created',
        ),
        migrations.RemoveField(
            model_name='exchangecart',
            name='product',
        ),
        migrations.RemoveField(
            model_name='exchangecart',
            name='selected_colour',
        ),
        migrations.RemoveField(
            model_name='exchangecart',
            name='selected_quantity',
        ),
        migrations.RemoveField(
            model_name='exchangecart',
            name='selected_size',
        ),
    ]
