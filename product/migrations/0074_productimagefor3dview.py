# Generated by Django 2.1.5 on 2019-10-16 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0073_customerproductcart_is_exchange_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImageFor3DView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image1', models.ImageField(upload_to='Product/3DView')),
                ('image2', models.ImageField(upload_to='Product/3DView')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product')),
            ],
        ),
    ]
