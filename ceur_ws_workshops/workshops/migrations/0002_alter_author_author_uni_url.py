# Generated by Django 5.0.6 on 2024-06-14 10:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workshops", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="author_uni_url",
            field=models.CharField(max_length=200),
        ),
    ]
