# Generated by Django 5.0.6 on 2024-05-24 15:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer", "0002_alter_customer_password_alter_customer_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="password",
            field=models.TextField(),
        ),
    ]
