# Generated by Django 2.1.5 on 2019-10-16 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0074_productimagefor3dview'),
        ('unity', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbodymeasurementdata',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='product.Product'),
            preserve_default=False,
        ),
    ]
