
from django.db import migrations, models
import uuid

def generate_secret_tokens(apps, schema_editor):
    Paper = apps.get_model('workshops', 'Paper')
    for paper in Paper.objects.all():
        paper.secret_token = uuid.uuid4()
        paper.save()

    Workshop = apps.get_model('workshops', 'Workshop')
    for workshop in Workshop.objects.all():
        workshop.secret_token = uuid.uuid4()
        workshop.save()
        
class Migration(migrations.Migration):

    dependencies = [
        ("workshops", "0017_remove_paper_author_paper_authors"),
    ]

    operations = [
        migrations.RunPython(generate_secret_tokens, reverse_code=migrations.RunPython.noop),
    ]

