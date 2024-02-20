from django.forms import ModelForm
from .models import Workshop
from django import forms

class CreateWorkshopForm(forms.Form):
    workshop_title = forms.CharField(label='Workshop Title', max_length=100, required=True)
    volume_number = forms.CharField(label='Volume Number', max_length=100, required=True)
    urn = forms.CharField(label='URN', max_length=100, required=True)
    publication_year = forms.IntegerField(label='Publication Year', required=True)
    license = forms.CharField(label='License', max_length=100, required=True)
    location_time = forms.CharField(label='Location and Time', max_length=100, required=True)
    editor_1 = forms.CharField(label='Workshop Editor 1', max_length=100, required=True)
    editor_2 = forms.CharField(label='Workshop Editor 2', max_length=100, required=True)
    editor_3 = forms.CharField(label='Workshop Editor 3', max_length=100, required=True)
    # Add other necessary fields here
