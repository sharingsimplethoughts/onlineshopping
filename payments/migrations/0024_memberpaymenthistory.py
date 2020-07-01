# Generated by Django 2.1.5 on 2019-07-31 15:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0042_auto_20190730_2003'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0023_auto_20190731_1801'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberPaymentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('amount', models.CharField(blank=True, max_length=30, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('order_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.CustomerOrders')),
                ('send_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='send_by', to=settings.AUTH_USER_MODEL)),
                ('send_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='send_to', to=settings.AUTH_USER_MODEL)),
                ('sub_order_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.OrderedProductStatus')),
            ],
        ),
    ]