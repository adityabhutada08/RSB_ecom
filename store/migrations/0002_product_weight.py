# Generated by Django 5.1 on 2024-08-15 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
