# Generated by Django 5.0.6 on 2024-05-23 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tour', '0003_alter_tour_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='departure',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tour',
            name='tour_ID',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
