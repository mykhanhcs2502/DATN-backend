# Generated by Django 5.0.6 on 2024-05-14 15:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customer", "0001_initial"),
        ("order_feedback", "0001_initial"),
        ("tour", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="addrequest",
            name="places",
        ),
        migrations.RemoveField(
            model_name="addrequest",
            name="request_ID",
        ),
        migrations.RemoveField(
            model_name="cancelrequest",
            name="request_ID",
        ),
        migrations.RemoveField(
            model_name="customer",
            name="user",
        ),
        migrations.AlterField(
            model_name="order",
            name="user_ID",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="customer.customer",
            ),
        ),
        migrations.AlterField(
            model_name="feedback",
            name="user_ID",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="customer.customer"
            ),
        ),
        migrations.RemoveField(
            model_name="customer_views_place",
            name="user_ID",
        ),
        migrations.RemoveField(
            model_name="customer_views_place",
            name="place_ID",
        ),
        migrations.RemoveField(
            model_name="editrequest",
            name="request_ID",
        ),
        migrations.RemoveField(
            model_name="manager",
            name="user",
        ),
        migrations.RemoveField(
            model_name="staff",
            name="managerID",
        ),
        migrations.RemoveField(
            model_name="request",
            name="manager_ID",
        ),
        migrations.RemoveField(
            model_name="placeimages",
            name="place_ID",
        ),
        migrations.RemoveField(
            model_name="tour",
            name="places",
        ),
        migrations.DeleteModel(
            name="Profile",
        ),
        migrations.RemoveField(
            model_name="request",
            name="staff_ID",
        ),
        migrations.RemoveField(
            model_name="request",
            name="tour_ID",
        ),
        migrations.RemoveField(
            model_name="staff",
            name="user",
        ),
        migrations.RemoveField(
            model_name="tour",
            name="staff",
        ),
        migrations.AlterField(
            model_name="order",
            name="tour_ID",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, to="tour.tour"
            ),
        ),
        migrations.DeleteModel(
            name="AddRequest",
        ),
        migrations.DeleteModel(
            name="CancelRequest",
        ),
        migrations.DeleteModel(
            name="Customer",
        ),
        migrations.DeleteModel(
            name="Customer_views_Place",
        ),
        migrations.DeleteModel(
            name="EditRequest",
        ),
        migrations.DeleteModel(
            name="Manager",
        ),
        migrations.DeleteModel(
            name="PlaceImages",
        ),
        migrations.DeleteModel(
            name="Place",
        ),
        migrations.DeleteModel(
            name="Request",
        ),
        migrations.DeleteModel(
            name="Staff",
        ),
        migrations.DeleteModel(
            name="Tour",
        ),
    ]
