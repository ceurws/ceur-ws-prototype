# Generated by Django 5.0.1 on 2024-02-06 12:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshops', '0007_remove_workshop_editor'),
    ]

    operations = [
        migrations.AddField(
            model_name='workshop',
            name='editor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='workshops.editor'),
        ),
    ]
