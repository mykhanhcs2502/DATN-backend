# Generated by Django 5.0.6 on 2024-05-24 16:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("manager", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="manager",
            name="password",
            field=models.TextField(),
        ),
    ]
