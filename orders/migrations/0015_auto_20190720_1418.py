# Generated by Django 2.1.5 on 2019-07-20 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_auto_20190425_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderedproductstatus',
            name='track_id',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='orderedproductstatus',
            name='track_url',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
