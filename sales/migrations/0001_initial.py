# Generated by Django 5.2 on 2025-06-11 11:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0006_alter_product_quantity_and_more'),
        ('shops', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('selling_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sold_at', models.DateTimeField(auto_now_add=True)),
                ('product_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.productinstance')),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shops.shop')),
            ],
        ),
    ]
