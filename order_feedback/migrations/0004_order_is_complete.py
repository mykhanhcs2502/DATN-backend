# Generated by Django 5.0.6 on 2024-06-02 05:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "order_feedback",
            "0003_alter_feedback_reviews_alter_feedback_tour_id_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="is_complete",
            field=models.BooleanField(default=True),
        ),
    ]
