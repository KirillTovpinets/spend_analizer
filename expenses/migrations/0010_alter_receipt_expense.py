# Generated by Django 4.2.17 on 2025-02-04 21:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0009_remove_expense_receipts_receipt_expense'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='expense',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='expenses.expense'),
        ),
    ]
