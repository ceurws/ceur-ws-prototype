# Generated by Django 5.0.6 on 2024-08-15 06:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workshops", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paper",
            name="complete",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
