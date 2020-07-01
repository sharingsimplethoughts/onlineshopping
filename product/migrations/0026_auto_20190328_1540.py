# Generated by Django 2.1.5 on 2019-03-28 10:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0025_auto_20190328_1349'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoupanCodeUseLimit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used', models.CharField(max_length=2)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.CouponCode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='coupancodeuselimit',
            unique_together={('user', 'coupon')},
        ),
    ]
