# Generated by Django 2.1.5 on 2019-07-30 08:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0038_auto_20190729_1547'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStatusChangeDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('order_status', models.CharField(choices=[('1', '0rdered'), ('2', 'Packed'), ('3', 'Shipped'), ('4', 'Delivered'), ('5', 'Cancelled'), ('6', 'Out for delivery'), ('7', 'returned'), ('8', 'return accepted'), ('9', 'return completed and refuned'), ('10', 'exchange'), ('11', 'pickup and exchanged'), ('12', 'delivered and exchanged')], default=1, max_length=2)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.OrderedProductStatus')),
            ],
        ),
    ]
