# Generated by Django 2.1.5 on 2019-04-25 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_orderedproductreviews'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeraddress',
            name='country_code',
            field=models.CharField(default='+91', max_length=10),
            preserve_default=False,
        ),
    ]
