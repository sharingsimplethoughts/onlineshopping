# Generated by Django 2.1.5 on 2019-05-07 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_auto_20190507_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripecustomer',
            name='card',
            field=models.CharField(max_length=40),
        ),
    ]
