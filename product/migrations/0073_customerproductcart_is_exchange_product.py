# Generated by Django 2.1.5 on 2019-07-24 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0072_productavailablecolourwithsizeqty_is_out_of_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerproductcart',
            name='is_exchange_product',
            field=models.BooleanField(default=False),
        ),
    ]
