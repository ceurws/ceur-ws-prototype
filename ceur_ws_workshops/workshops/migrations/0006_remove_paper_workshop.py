# Generated by Django 5.0.1 on 2024-03-04 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workshops', '0005_remove_editor_workshop_alter_workshop_volume_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='workshop',
        ),
    ]
