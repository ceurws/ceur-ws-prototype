# Generated by Django 5.0.1 on 2024-02-06 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workshops', '0009_merge_20240206_1358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workshop',
            name='editor',
        ),
        migrations.RemoveField(
            model_name='workshop',
            name='workshop_summary',
        ),
    ]
