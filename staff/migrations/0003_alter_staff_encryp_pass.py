# Generated by Django 5.0.6 on 2024-05-24 16:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("staff", "0002_alter_staff_encryp_pass"),
    ]

    operations = [
        migrations.AlterField(
            model_name="staff",
            name="encryp_pass",
            field=models.TextField(default="123456"),
        ),
    ]
