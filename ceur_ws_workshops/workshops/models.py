from django.db import models
import uuid

class Editor(models.Model):
    volume_editor = models.CharField(max_length=100)

class Author(models.Model):
    author = models.CharField(max_length=100)

class Workshop(models.Model):
    volume_number = models.CharField(max_length=10)
    urn = models.CharField(max_length=50)
    publication_year = models.IntegerField()
    license = models.CharField(max_length=50)
    workshop_title = models.CharField(max_length=200)
    location_time = models.CharField(max_length=200)
    editors = models.ForeignKey(Editor, on_delete=models.CASCADE)
    # need to include table of contents 
    # need to include submitted papers 
    submitted_papers = models.ManyToManyField('Paper', related_name='submitted_papers')
    accepted_papers = models.ManyToManyField('Paper', related_name='accepted_papers')
    regular_accepted_papers = models.ManyToManyField('Paper', related_name='regular_accepted_papers')
    short_accepted_papers = models.ManyToManyField('Paper', related_name='short_accepted_papers')
    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.workshop_title   

class Paper(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    paper_title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    pages = models.CharField(max_length=10)
    metadata = models.JSONField()  # Assuming metadata is stored as JSON
    uploaded_file = models.FileField(upload_to='papers/')
    # Licensing information fields

    def __str__(self):
        return self.paper_title