# Generated by Django 2.1.5 on 2019-10-17 09:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('unity', '0002_userbodymeasurementdata_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbodymeasurementdata',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.Product'),
        ),
    ]
