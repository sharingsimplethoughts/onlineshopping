# Generated by Django 2.1.5 on 2019-04-12 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0034_customerproductcart_is_ordered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='cat_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='subcategory',
            name='subcat_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='subsubcategory',
            name='subsubcat_name',
            field=models.CharField(max_length=50),
        ),
    ]