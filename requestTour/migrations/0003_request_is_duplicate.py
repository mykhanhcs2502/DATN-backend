# Generated by Django 5.0.6 on 2024-06-01 11:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "requestTour",
            "0002_alter_addrequest_departure_alter_addrequest_note_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="request",
            name="is_duplicate",
            field=models.ManyToManyField(blank=True, to="requestTour.request"),
        ),
    ]
