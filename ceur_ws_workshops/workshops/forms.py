
from .models import Workshop, Editor, Paper, Author
from django import forms
from django.forms import modelformset_factory
from django.forms import TextInput, FileInput
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
                   'workshop_begin_date', 'workshop_end_date', 'urn', 'submitted_by']
        
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
            'urn': TextInput(attrs={'size': 50, 
                                   'placeholder': 'urn:nbn:de:0074-2019-001'}),
            'submitted_by': TextInput(attrs={'size': 50,
                                            'placeholder': 'John Doe'}),
        }

class PaperForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        file_uploaded = kwargs.pop('file_uploaded', False)
        super(PaperForm, self).__init__(*args, **kwargs)

        if file_uploaded:
            # If the file is uploaded, change the field to indicate it's for changing the file.
            self.fields['uploaded_file'].label = 'Change current file'
        else:
            # If the file is not uploaded, you might want to customize the field to indicate it's for uploading.
            self.fields['uploaded_file'].label = 'Upload file'
    class Meta:
        model = Paper
        fields = ['paper_title', 'pages', 'uploaded_file']

        widgets = {
            'paper_title': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the title of the paper'}),
            'pages': TextInput(attrs={'size': 50, 
                                            'placeholder': 'Enter the number of pages'}),
            # 'uploaded_file': CustomClearableFileInput,
            'uploaded_file': FileInput(attrs={'accept': '.pdf'}),
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
