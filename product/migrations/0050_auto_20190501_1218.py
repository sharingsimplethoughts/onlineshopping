# Generated by Django 2.1.5 on 2019-05-01 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0049_product_available_colours'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productimagebycolour',
            old_name='product_colour',
            new_name='product_colour_id',
        ),
    ]
