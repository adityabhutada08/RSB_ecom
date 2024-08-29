# Generated by Django 5.1 on 2024-08-22 05:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_weight'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variation_category', models.CharField(choices=[('quantity', 'quantity'), ('weight', 'weight')], max_length=100)),
                ('variation_value', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
    ]
