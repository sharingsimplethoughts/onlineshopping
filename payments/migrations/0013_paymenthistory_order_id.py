# Generated by Django 2.1.5 on 2019-05-08 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0012_auto_20190508_1801'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenthistory',
            name='order_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]