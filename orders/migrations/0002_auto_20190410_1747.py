# Generated by Django 2.1.5 on 2019-04-10 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeraddress',
            name='lag',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='customeraddress',
            name='lat',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
