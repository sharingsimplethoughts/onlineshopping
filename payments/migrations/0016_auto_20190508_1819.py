# Generated by Django 2.1.5 on 2019-05-08 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0015_auto_20190508_1816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymenthistory',
            name='amount',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='paymenthistory',
            name='payment_detail',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
