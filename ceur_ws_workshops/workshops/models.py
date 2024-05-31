from django.db import models
import uuid
from django.utils import timezone
from django.contrib import admin
from datetime import date
from django_countries.fields import CountryField
import os 

class Editor(models.Model):
    editor_name = models.CharField(max_length=100)
    editor_url = models.URLField(max_length=200,null=True, blank=True)
    institution = models.CharField(max_length=200)
    editor_country_choices = [('', 'Select a country')] + list(CountryField().choices)
    institution_country = models.CharField(max_length=200, choices=editor_country_choices)
    institution_url = models.URLField(max_length=200,null=True, blank=True)
    editor_agreement = models.FileField(upload_to='agreement',null=True, blank=True)
    # optional
    research_group = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        # return self.name
        return f"{self.editor_name}, {self.institution}, {self.institution_country}"

class Author(models.Model):
    author_name = models.CharField(max_length=100)
    author_university = models.CharField(max_length=100)
    author_uni_url = models.URLField(max_length=200)
    author_email = models.EmailField(max_length=200)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.author_name

class Session(models.Model):
    session_title = models.CharField(max_length=100)

    def __str__(self):
        return self.session_title
    
class Workshop(models.Model):
    
    def workshop_agreement_file_path(instance, filename):
        acronym = instance.workshop_acronym
        filename = f"EDITOR-AGREEMENT-{acronym}.pdf"
        workshop_id = instance.id
        return f"agreement/Vol-{workshop_id}/{filename}"
    
    # Filled in by user
    workshop_full_title = models.CharField(max_length=200,)
    workshop_short_title = models.CharField(max_length=200)
    workshop_acronym = models.CharField(max_length=50)
    workshop_description = models.TextField(max_length=500)
    workshop_city = models.CharField(max_length=200) 
    workshop_country_choices = [('', 'Select a country')] + list(CountryField().choices)
    workshop_country = models.CharField(max_length=200, choices=workshop_country_choices)
    workshop_begin_date = models.DateField(default=date.today)
    workshop_end_date = models.DateField(default=date.today)
    volume_owner = models.CharField(max_length=200)
    volume_owner_email = models.EmailField(max_length=200)
    workshop_language_iso = models.CharField(max_length=5)
    workshop_colocated = models.CharField(max_length=200,null=True, blank=True)
    year_final_papers = models.CharField(max_length=4)
    total_submitted_papers = models.IntegerField()
    total_accepted_papers = models.IntegerField()
    total_reg_acc_papers = models.IntegerField(null=True, blank=True)
    total_short_acc_papers = models.IntegerField(null=True, blank=True)

    # Filled in by CEUR
    volume_number = models.IntegerField(null=True, blank=True)
    submission_date = models.DateField(null=True, blank=True) # date the submit button is clicked by volume owner
    license = models.CharField(max_length=50,null=True, blank=True)
    urn = models.CharField(max_length=50,null=True, blank=True)

    editor_agreement = models.FileField(upload_to=workshop_agreement_file_path)

    # KEYS
    editors = models.ManyToManyField(Editor, blank=True, related_name='workshops_editors')  
    accepted_papers = models.ManyToManyField('Paper', related_name='accepted_papers')
    sessions = models.ManyToManyField(Session, blank=True, related_name='workshop_sessions')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return self.workshop_full_title

class Language(models.Model):
    iso_639_2 = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Paper(models.Model):
    def paper_upload_path(instance, filename):
        workshop_volume = instance.workshop.id
        return f"papers/Vol-{workshop_volume}/{filename}"

    def agreement_file_path(instance, filename):
        agreement_file = instance.workshop.id
        original_filename = instance.agreement_file.name
        paper_title = instance.paper_title.replace(' ', '')
        extension = os.path.splitext(original_filename)[1]
        filename = f'AUTHOR-AGREEMENT-{paper_title}{extension}'
        return f"agreement/Vol-{agreement_file}/{filename}"
    paper_title = models.CharField(max_length=200)
    pages = models.CharField(max_length=10)
    uploaded_file = models.FileField(upload_to=paper_upload_path, blank = True)
    agreement_file = models.FileField(upload_to=agreement_file_path, blank = True)
    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sort_order = models.PositiveIntegerField(default=0)
    # KEYS
    authors = models.ManyToManyField(Author)  
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='papers')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.paper_title



