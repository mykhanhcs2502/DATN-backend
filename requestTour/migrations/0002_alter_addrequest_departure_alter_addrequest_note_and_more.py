# Generated by Django 5.0.6 on 2024-05-23 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requestTour', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addrequest',
            name='departure',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='addrequest',
            name='note',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='editrequest',
            name='edit_info',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='reply',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='request',
            name='request_ID',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]
