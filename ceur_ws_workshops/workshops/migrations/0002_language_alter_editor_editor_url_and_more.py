# Generated by Django 5.0.1 on 2024-05-10 10:10

import workshops.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workshops", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Language",
            fields=[
                (
                    "iso_639_2",
                    models.CharField(max_length=3, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name="editor",
            name="editor_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="workshop",
            name="editor_agreement",
            field=models.FileField(
                default=1,
                upload_to=workshops.models.Workshop.workshop_agreement_file_path,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="workshop",
            name="license",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="workshop",
            name="urn",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="workshop",
            name="workshop_colocated",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="workshop",
            name="workshop_language_iso",
            field=models.CharField(max_length=5),
        ),
    ]
