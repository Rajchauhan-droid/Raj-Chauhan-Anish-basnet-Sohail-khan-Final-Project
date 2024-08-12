# Generated by Django 3.1 on 2023-11-06 06:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0007_coupon'),
        ('orders', '0004_auto_20231106_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='carts.coupon'),
        ),
    ]
