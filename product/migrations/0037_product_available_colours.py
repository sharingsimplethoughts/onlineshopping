# Generated by Django 2.1.5 on 2019-04-29 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0036_auto_20190429_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='available_colours',
            field=models.ManyToManyField(blank=True, related_name='allcolour', through='product.ProductAvailableAllColour', to='product.Colour'),
        ),
    ]
