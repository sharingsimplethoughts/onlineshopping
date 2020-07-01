# Generated by Django 2.1.5 on 2019-05-08 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0011_auto_20190508_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenthistory',
            name='amount',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='captured',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='paymenthistory',
            name='payment_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='paymenthistory',
            name='status_message',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
