# Generated by Django 5.0.1 on 2024-05-30 12:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workshops", "0002_alter_editor_institution_country_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="paper",
            name="sort_order",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
