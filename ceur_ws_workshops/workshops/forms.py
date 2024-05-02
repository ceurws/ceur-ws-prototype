
from .models import Workshop, Editor, Paper, Author, Session
from django import forms
from django.forms import modelformset_factory
from django.forms import TextInput, FileInput, NumberInput
from django_countries.widgets import CountrySelectWidget
from django.utils.translation import gettext_lazy as _

class DateInput(forms.DateInput):
    input_type = "date"
    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)


class WorkshopForm(forms.ModelForm):

    class Meta:
        model = Workshop
        fields = ['workshop_short_title', 'workshop_full_title', 'workshop_acronym',
                'workshop_language_iso', 'workshop_description', 'workshop_country',  'workshop_city', 'year_final_papers', 'workshop_colocated',
                'workshop_begin_date', 'workshop_end_date', 'year_final_papers', 'volume_owner',
                'volume_owner_email', 'total_submitted_papers', 'total_accepted_papers', 'total_reg_acc_papers', 'total_short_acc_papers']
        
        widgets = {
            'workshop_short_title': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the shorthand title of the workshop'}),
            'workshop_full_title': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the full title of the workshop'}),
            'workshop_acronym': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the acronym of the workshop'}),
            'workshop_language_iso': TextInput(attrs={'size': 50, 
                                            'placeholder': '''<br> <br> The main language of the proceedings (eng, deu, fra, spa, rus, ita, por, ...) according to ISO 639-2/T (http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes)'''}),
            'workshop_description': TextInput(attrs={'size': 50,
                                                     'placeholder': 'Briefly describe the workshop'}),
            'workshop_city': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Amsterdam'}),
            'workshop_country': CountrySelectWidget(),
            'workshop_begin_date': DateInput(attrs={'id': 'id_workshop_begin_date'}),
            'workshop_end_date': DateInput(attrs={'id': 'id_workshop_end_date'}),
            'year_final_papers': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the year in which the final papers of the proceedings were produced'}),
            'workshop_colocated': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter with which workshop this workshop was colocated'}),
            'license': TextInput(attrs={'size': 50, 
                                            'placeholder': 'MIT'}),
            'volume_owner': TextInput(attrs={'size': 50,
                                            'placeholder': 'John Doe'}),
            'volume_owner_email': TextInput(attrs={'size': 50,
                                            'placeholder': 'johndoe@email.com'}),
            'year_final_papers': TextInput(attrs={'size': 50,
                                            'placeholder': 'Enter the year final paper was uploaded'}),
            'total_submitted_papers': TextInput(attrs={'size': 50,
                                            'placeholder': 'Total amount of papers submitted'}),
            'total_accepted_papers': TextInput(attrs={'size': 50,
                                            'placeholder': 'Total amount of accepted papers'}),
            'total_reg_acc_papers': TextInput(attrs={'size': 50,
                                            'placeholder': '(optional) Total amount of regular size accepted papers'}),
            'total_short_acc_papers': TextInput(attrs={'size': 50,
                                            'placeholder': '(optional) Total amount of short size accepted papers'})
                                        
       }

        help_texts = {
            'workshop_short_title': '<br> <br> This is the shorthand title of the workshop',
            'workshop_full_title': '<br> <br> This is the long title of the proceedings',
            'workshop_acronym': '''<br> <br> The acronym of the workshop plus YYYY (year of the workshop)
                 the acronym may contain '-'; between acronym and year is either a blank
                 or a '-'. The year is exactly 4 digits, e.g. 2012''',
            'workshop_language_iso': '''<br> <br> The main language of the proceedings (eng, deu, fra, spa, rus, ita, por, ...) according to ISO 639-2/T (http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes)''',
            'workshop_description': '''<br> <br> A brief description of the workshop. This will be displayed on the CEUR-WS.org page of the workshop.''',
            'workshop_city': '''<br> <br> The city where the workshop was held.''',
            'workshop_country': '''<br> <br> The country where the workshop was held.''',
            'workshop_begin_date': '''<br> <br> The date when the workshop started.''',
            'workshop_end_date': '''<br> <br> The date when the workshop ended. If the workshop was a one-day event, the begin and end date are the same.''',
            'year_final_papers': '''<br> <br> The year in which the final papers of the proceedings were produced''',
            'workshop_colocated': '''<br> <br> The name of the workshop with which this workshop was colocated''',
            'volume_owner': '''<br> <br> The full name  of the person who is responsible for the proceedings''',
            'volume_owner_email': '''<br> <br> The email address of the person who is responsible for the proceedings''',
            'total_submitted_papers': '''<br> <br> The total amount of papers submitted''',
            'total_accepted_papers': '''<br> <br> The total amount of accepted papers, from the total amount of papers submitted, including regular and short papers''',
            'total_reg_acc_papers': '''<br> <br> The total amount of regular-size accepted peer-reviewed papers''',
            'total_short_acc_papers': '''<br> <br> The total amount of short size accepted papers'''
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
        Author, fields=('author_name', 'author_university', 'author_uni_url', 'author_email'), extra=1,
        # CSS styling but for formsets
        widgets = {
            'author_name': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the name of the author'}),
            'author_university': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the university of the author'}),
            'author_uni_url': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the URL of the university'}),
            'author_email': TextInput(attrs={'size': 50,
                                            'placeholder': 'Enter the email of the author'})
        })

EditorFormSet = modelformset_factory(
    Editor, fields=('editor_name','editor_url' ,'institution', 'institution_country', 'institution_url', 'research_group'), extra=1,
    # CSS styling but for formsets
    widgets = {
        'editor_name': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the name of the editor'}),
        'editor_url': TextInput(attrs={'size': 50, 
                                            'placeholder': '(optional) Enter the personal url of the editor'}),
        'institution': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the institution of the editor'}),
        'institution_country': CountrySelectWidget(),

        'institution_url': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the URL of the institution'}),
        'research_group': TextInput(attrs={'size': 50, 
                                            'placeholder': '(optional) Enter the research group of the editor'})
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