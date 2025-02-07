# Generated by Django 4.2.17 on 2025-02-03 20:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0005_remove_expenseitem_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receipt',
            name='image',
        ),
        migrations.CreateModel(
            name='ReceiptImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='receipts/')),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='expenses.receipt')),
            ],
        ),
    ]
