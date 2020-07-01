# Generated by Django 2.1.5 on 2019-03-27 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0018_auto_20190327_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerproductwishlist',
            name='selected_colour',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.Colour'),
        ),
        migrations.AlterField(
            model_name='customerproductwishlist',
            name='selected_size',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.Size'),
        ),
    ]
