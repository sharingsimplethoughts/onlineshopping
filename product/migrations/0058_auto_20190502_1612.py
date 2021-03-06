# Generated by Django 2.1.5 on 2019-05-02 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0057_product_isfree_delivery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='min_price',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='offer_of_min',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
