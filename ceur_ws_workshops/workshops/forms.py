
from .models import Workshop, Editor, Paper, Author, Session
from django import forms
from django.forms import modelformset_factory
from django.forms import TextInput, FileInput, NumberInput
from django_countries.widgets import CountrySelectWidget

class DateInput(forms.DateInput):
    input_type = "date"
    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)

class WorkshopForm(forms.ModelForm):

    class Meta:
        model = Workshop
        fields = ['workshop_title', 'workshop_description', 'workshop_city', 'workshop_country',
                     'publication_year',
                   'workshop_begin_date', 'workshop_end_date', 'license', 'submitted_by', 'email_address']
        
        widgets = {
            'workshop_title': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the title of the workshop'}),
            'workshop_description': TextInput(attrs={'size': 50,
                                                     'placeholder': 'Briefly describe the workshop'}),
            'workshop_city': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Amsterdam'}),
            'workshop_begin_date': DateInput(attrs={'id': 'id_workshop_begin_date'}),
            'workshop_end_date': DateInput(attrs={'id': 'id_workshop_end_date'}),
            'workshop_country': CountrySelectWidget(),
            'volume_number': NumberInput(attrs={'size': 50, 
                                            'placeholder': '1000'}),
            'license': TextInput(attrs={'size': 50, 
                                            'placeholder': 'MIT'}),
            'submitted_by': TextInput(attrs={'size': 50,
                                            'placeholder': 'John Doe'}),
            'email_address': TextInput(attrs={'size': 50,
                                            'placeholder': 'johndoe@email.com'}),
                                        
       }


class PaperForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        file_uploaded = kwargs.pop('file_uploaded', False)
        workshop = kwargs.pop('workshop', None)
        super(PaperForm, self).__init__(*args, **kwargs)

        if file_uploaded:
            self.fields['uploaded_file'].label = 'Change current file'
        else:
            self.fields['uploaded_file'].label = 'Upload file'

        # Dynamically set queryset for session field based on the workshop
        if workshop:
            self.fields['session'].queryset = workshop.sessions.all()

    class Meta:
        model = Paper
        fields = ['paper_title', 'pages', 'session', 'uploaded_file', 'agreement_file']

        widgets = {
            'paper_title': forms.TextInput(attrs={'size': 50, 'placeholder': 'Enter the title of the paper'}),
            'pages': forms.TextInput(attrs={'size': 50, 'placeholder': 'Enter the number of pages'}),
            'uploaded_file': forms.FileInput(attrs={'accept': '.pdf'}),
            'agreement_file': forms.FileInput(attrs={'accept': '.pdf'}),
        }



AuthorFormSet = modelformset_factory(
        Author, fields=('author_name', 'author_university', 'author_uni_url'), extra=1,
        # CSS styling but for formsets
        widgets = {
            'author_name': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the name of the author'}),
            'author_university': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the university of the author'}),
            'author_uni_url': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the URL of the university'}),
        })

EditorFormSet = modelformset_factory(
    Editor, fields=('name', 'university', 'university_country', 'university_url', 'research_group', 'research_group_url'), extra=1,
    # CSS styling but for formsets
    widgets = {
        'name': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the name of the editor'}),
        'university': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the university of the editor'}),
        'university_country': CountrySelectWidget(),

        'university_url': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the URL of the university'}),
        'research_group': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the research group of the editor'}),
        'research_group_url': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the URL of the research group'}),
    }
)

SessionFormSet = modelformset_factory(
    Session, fields=('session_title',), extra=5,
    # CSS styling but for formsets
    widgets = {
        'session_title': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Title of the session'}),

    }
)