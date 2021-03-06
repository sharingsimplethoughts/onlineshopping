# Generated by Django 2.1.5 on 2019-05-07 08:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0004_auto_20190507_1339'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('payment_type', models.CharField(choices=[('1', 'Card'), ('2', 'Net banking'), ('3', 'Cash on delivery')], max_length=30)),
                ('status_code', models.CharField(max_length=10)),
                ('payment_id', models.CharField(max_length=200)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='stripepaymenthistory',
            name='user',
        ),
        migrations.DeleteModel(
            name='StripePaymentHistory',
        ),
    ]
