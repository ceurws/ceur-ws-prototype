from django.db import models
import uuid
from django.utils import timezone
from django.contrib import admin

class Editor(models.Model):
    name = models.CharField(max_length=100)

class Author(models.Model):
    author_name = models.CharField(max_length=100, null= True, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

class Workshop(models.Model):
    volume_number = models.CharField(max_length=10)
    urn = models.CharField(max_length=50)
    publication_year = models.IntegerField()
    license = models.CharField(max_length=50)
    workshop_title = models.CharField(max_length=200)
    location_time = models.CharField(max_length=200)

    # need to include table of contents 
    # need to include submitted papers 
    editors = models.ManyToManyField(Editor, blank=True)  
    authors = models.ManyToManyField(Author, related_name='workshops_authored')  # Many-to-Many with Author directly
    accepted_papers = models.ManyToManyField('Paper', related_name='accepted_papers')

    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.workshop_title   

class Paper(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    paper_title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    pages = models.CharField(max_length=10)
    uploaded_file = models.FileField(upload_to='papers/')  # Add this line for file upload
    
    # Add other fields as needed (JSON?)

    def __str__(self):
        return self.paper_title
