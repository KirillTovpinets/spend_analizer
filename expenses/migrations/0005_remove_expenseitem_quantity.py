# Generated by Django 4.2.17 on 2025-02-03 18:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0004_expenseitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expenseitem',
            name='quantity',
        ),
    ]
