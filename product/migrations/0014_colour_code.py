# Generated by Django 2.1.5 on 2019-03-27 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_auto_20190312_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='colour',
            name='code',
            field=models.CharField(default='rgb(66, 134, 244)', max_length=30),
            preserve_default=False,
        ),
    ]