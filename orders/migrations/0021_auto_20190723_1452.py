# Generated by Django 2.1.5 on 2019-07-23 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_refundmoneybankdetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedproductstatus',
            name='order_status',
            field=models.CharField(choices=[('1', 'Ordered'), ('2', 'Packed'), ('3', 'Shipped'), ('4', 'Delivered'), ('5', 'Canceled'), ('6', 'Out for delivery'), ('7', 'returned'), ('8', 'exchanged')], default=1, max_length=2),
        ),
    ]
