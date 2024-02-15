# Generated by Django 5.0.1 on 2024-02-15 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshops', '0016_remove_workshop_regular_accepted_papers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='author',
        ),
        migrations.AddField(
            model_name='paper',
            name='authors',
            field=models.ManyToManyField(to='workshops.author'),
        ),
    ]
