# Generated by Django 4.2.17 on 2025-01-31 22:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0002_expense_merchant_expense_post_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='receipt',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='expenses.receipt'),
        ),
    ]
