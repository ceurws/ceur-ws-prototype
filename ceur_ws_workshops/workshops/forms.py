from .models import Workshop, Editor, Author, Paper
from django import forms
from django.forms import modelformset_factory


class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = ['workshop_title', 'workshop_description', 'workshop_city', 'workshop_country',
                   'workshop_begin_date', 'workshop_end_date', 'urn', 'submitted_by']

class PaperForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = ['paper_title', 'pages', 'uploaded_file']
                
AuthorFormSet = modelformset_factory(
        Author, fields=('author_name', 'author_university', 'author_uni_url'), extra=1
)

EditorFormSet = modelformset_factory(
    Editor, fields=('name', 'university', 'university_country', 'university_url', 'research_group', 'research_group_url'), extra=1
)
