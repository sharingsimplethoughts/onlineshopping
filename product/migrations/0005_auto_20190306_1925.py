# Generated by Django 2.1.5 on 2019-03-06 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_product_usersection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='usercategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='designer_stylist.StylistDesignerCategory'),
        ),
        migrations.AlterField(
            model_name='product',
            name='usersection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='designer_stylist.StylistDesignerSection'),
        ),
    ]