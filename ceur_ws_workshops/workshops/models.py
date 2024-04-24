from django.db import models
import uuid
from django.utils import timezone
from django.contrib import admin
from datetime import date
from django_countries.fields import CountryField
from django.utils.text import slugify
from django.db.models import Q


class Editor(models.Model):
    name = models.CharField(max_length=100)
    university = models.CharField(max_length=200)
    editor_country_choices = [('', 'Select a country')] + list(CountryField().choices)
    university_country = models.CharField(max_length=200, choices=editor_country_choices)
    university_url = models.URLField(max_length=200)
    research_group = models.CharField(max_length=100)
    research_group_url = models.URLField(max_length=200)

    def __str__(self):
        # return self.name
        return f"{self.name}, {self.university}, {self.university_country}"

class Author(models.Model):
    author_name = models.CharField(max_length=100)
    author_university = models.CharField(max_length=100)
    author_uni_url = models.URLField(max_length=200)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.author_name

class Session(models.Model):
    session_title = models.CharField(max_length=100)

    def __str__(self):
        return self.session_title

class Workshop(models.Model):
    workshop_full_title = models.CharField(max_length=200)
    workshop_short_title = models.CharField(max_length=200)
    workshop_acronym = models.CharField(max_length=50)
    workshop_description = models.TextField(max_length=500)
    workshop_city = models.CharField(max_length=200) 
    workshop_country_choices = [('', 'Select a country')] + list(CountryField().choices)
    workshop_country = models.CharField(max_length=200, choices=workshop_country_choices)
    workshop_begin_date = models.DateField(default=date.today)

    workshop_end_date = models.DateField(default=date.today)
    urn = models.CharField(max_length=50)
    volume_owner = models.CharField(max_length=200)
    volume_owner_email = models.EmailField(max_length=200)
    
    workshop_language_iso = models.CharField(max_length=50)
    workshop_colocated = models.CharField(max_length=200)

    # not filled in by user
    volume_number = models.IntegerField(null=True, blank=True)
    publication_year = models.IntegerField()
    license = models.CharField(max_length=50)

    # KEYS
    editors = models.ManyToManyField(Editor, blank=True, related_name='workshops_editors')  
    accepted_papers = models.ManyToManyField('Paper', related_name='accepted_papers')
    sessions = models.ManyToManyField(Session, blank=True, related_name='workshop_sessions')

    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return self.workshop_full_title
 

def paper_upload_path(instance, filename):
    """
    Generate a custom upload path for papers.
    Assumes instance has a direct foreign key to Workshop.
    Format: "papers/Vol-{workshop_volume}/{filename}"
    """
    workshop_volume = instance.workshop.id
    return f"papers/Vol-{workshop_volume}/{filename}"

def agreement_file_path(instance, filename):
    agreement_file = instance.workshop.id
    return f"agreement/Vol-{agreement_file}/{filename}"
    
class Paper(models.Model):
    paper_title = models.CharField(max_length=200)
    pages = models.CharField(max_length=10)
    uploaded_file = models.FileField(upload_to=paper_upload_path, null=True, blank=True)
    agreement_file = models.FileField(upload_to=agreement_file_path, null=True, blank=True)
    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # KEYS
    authors = models.ManyToManyField(Author)  
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='papers')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):

        return self.paper_title




