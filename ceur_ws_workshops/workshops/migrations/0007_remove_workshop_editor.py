# Generated by Django 5.0.1 on 2024-02-05 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workshops', '0006_workshop_workshop_summary_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workshop',
            name='editor',
        ),
    ]
