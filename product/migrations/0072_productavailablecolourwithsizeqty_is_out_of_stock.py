# Generated by Django 2.1.5 on 2019-06-11 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0071_auto_20190607_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='productavailablecolourwithsizeqty',
            name='is_out_of_stock',
            field=models.BooleanField(default=False),
        ),
    ]
