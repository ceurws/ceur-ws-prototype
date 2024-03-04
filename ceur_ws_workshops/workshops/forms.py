from .models import Workshop, Editor
from django import forms
from django.forms import modelformset_factory


class EditorForm(forms.ModelForm):
    class Meta:
        model = Editor
        fields = ['name', 'university', 'university_country', 'university_url', 'research_group', 'research_group_url']

class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = ['workshop_title', 'workshop_description', 'workshop_city', 'workshop_country',
                   'workshop_begin_date', 'workshop_end_date', 'urn', 'submitted_by']
        

EditorFormSet = modelformset_factory(
    Editor, fields=('name', 'university', 'university_country', 'university_url', 'research_group', 'research_group_url'), extra=1
)
