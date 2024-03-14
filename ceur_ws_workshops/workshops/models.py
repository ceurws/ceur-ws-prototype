from django.db import models
import uuid
from django.utils import timezone
from django.contrib import admin
from datetime import date
from django_countries.fields import CountryField


class Editor(models.Model):
    name = models.CharField(max_length=100)
    university = models.CharField(max_length=200)
    editor_country_choices = [('', 'Select a country')] + list(CountryField().choices)
    university_country = models.CharField(max_length=200, choices=editor_country_choices)
    university_url = models.URLField(max_length=200)
    research_group = models.CharField(max_length=100)
    research_group_url = models.URLField(max_length=200)

class Author(models.Model):
    author_name = models.CharField(max_length=100)
    author_university = models.CharField(max_length=100)
    author_uni_url = models.URLField(max_length=200)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)



class Workshop(models.Model):
    workshop_title = models.CharField(max_length=200)
    workshop_description = models.TextField(max_length=500)
    workshop_city = models.CharField(max_length=200) 
    # workshop_country = models.CharField(max_length=200) 
    workshop_country_choices = [('', 'Select a country')] + list(CountryField().choices)
    workshop_country = models.CharField(max_length=200, choices=workshop_country_choices)
    workshop_begin_date = models.DateField(default=date.today)

    workshop_end_date = models.DateField(default=date.today)
    urn = models.CharField(max_length=50)
    submitted_by = models.CharField(max_length=200)
    email_address = models.EmailField(max_length=200)
    
    volume_number = models.IntegerField(default=1000)
    publication_year = models.IntegerField(default=2024)
    license = models.CharField(max_length=50,default='License')

    # KEYS
    editors = models.ManyToManyField(Editor, blank=True, related_name='workshops_editors')  
    accepted_papers = models.ManyToManyField('Paper', related_name='accepted_papers')

    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return self.workshop_title   

class Paper(models.Model):
    paper_title = models.CharField(max_length=200)
    pages = models.CharField(max_length=10)
    uploaded_file = models.FileField(upload_to='papers/', null = True, blank = True)
    
    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # KEYS
    authors = models.ManyToManyField(Author)  # Use ManyToManyField for multiple authors

    def __str__(self):
        return self.paper_title
