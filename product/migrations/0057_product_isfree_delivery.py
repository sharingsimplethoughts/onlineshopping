# Generated by Django 2.1.5 on 2019-05-02 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0056_auto_20190502_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='isfree_delivery',
            field=models.BooleanField(default=False),
        ),
    ]