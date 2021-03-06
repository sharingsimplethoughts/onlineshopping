# Generated by Django 2.1.5 on 2019-05-01 10:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0050_auto_20190501_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerproductcart',
            name='selected_colour',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.Colour'),
        ),
        migrations.AlterField(
            model_name='customerproductcart',
            name='selected_size',
            field=models.CharField(default='XL', max_length=10),
            preserve_default=False,
        ),
    ]
