
from .models import Workshop, Editor, Paper, Author, Session
from django import forms
from django.forms import modelformset_factory, TextInput, FileInput, NumberInput
from django_countries.widgets import CountrySelectWidget
from django.templatetags.static import static
import os, json
from django.core.exceptions import ValidationError
from signature_detect.loader import Loader
from signature_detect.extractor import Extractor
from signature_detect.cropper import Cropper
from signature_detect.judger import Judger
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class DateInput(forms.DateInput):
    input_type = "date"
    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)

class WorkshopForm(forms.ModelForm):
    workshop_language_iso = forms.ChoiceField(label="Language", choices=[], required=False)

    class Meta:
        model = Workshop
        fields = ['workshop_short_title', 'workshop_full_title', 'workshop_acronym',
                'workshop_language_iso', 'workshop_description', 'workshop_country',  'workshop_city', 'year_final_papers', 'workshop_colocated',
                'workshop_begin_date', 'workshop_end_date', 'year_final_papers', 'volume_owner',
                'volume_owner_email', 'total_submitted_papers', 'total_accepted_papers', 'total_reg_acc_papers', 'total_short_acc_papers', 'editor_agreement']
        
        help_texts = {'workshop_acronym': '''    <br/><br/>Please provide the acronym of the workshop.  
                    the acronym of the workshop plus YYYY (year of the workshop)
                    the acronym may contain '-'; between acronym and year is either a blank
                    or a '-'. The year is exactly 4 digits, e.g. 2012''',
                    'workshop_colocated': '''<br> <br> The name of the workshop with which this workshop was colocated. Usually, this is the name of the main conference. If the workshop was not colocated, leave this field empty.'''
    }
        widgets = {
            'workshop_short_title': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Provide the shorthand title of the workshop'}),
            'workshop_full_title': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Provide the full title of the workshop'}),
            'workshop_acronym': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Provide the acronym of the workshop'}),
            'workshop_language_iso': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Enter ISO of the language of the workshop'}),
            'workshop_description': TextInput(attrs={'size': 70,
                                                     'placeholder': 'Briefly describe the workshop'}),
            'workshop_city': TextInput(attrs={'size': 70, 
                                            'placeholder': 'The city the workshop took place in'}),
            'workshop_country': CountrySelectWidget(),

            'workshop_begin_date': DateInput(attrs={'id': 'id_workshop_begin_date'}),

            'workshop_end_date': DateInput(attrs={'id': 'id_workshop_end_date'}),

            'year_final_papers': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Provide the year the final papers of the proceedings were produced'}),
            'workshop_colocated': TextInput(attrs={'size': 70, 
                                            'placeholder': '(optional) Provide the workshop with which this workshop was colocated'}),
            'license': TextInput(attrs={'size': 70, 
                                            'placeholder': 'MIT'}),
            'volume_owner': TextInput(attrs={'size': 70,
                                            'placeholder': 'Provide the volume creator\'s (your) name'}),
            'volume_owner_email': TextInput(attrs={'size': 70,
                                            'placeholder': 'Provide the volume creator\'s (your) e-mail'}),
            'total_submitted_papers': TextInput(attrs={'size': 70,
                                            'placeholder': 'Provide the total number of papers submitted to the workshop'}),
            'total_accepted_papers': TextInput(attrs={'size': 70,
                                            'placeholder': 'Provide the total number of accepted papers submitted to the workshop'}),
            'total_reg_acc_papers': TextInput(attrs={'size': 70,
                                            'placeholder': '(optional) Provide the total number of regular length papers submitted'}),
            'total_short_acc_papers': TextInput(attrs={'size': 70,
                                            'placeholder': '(optional) Provide the total number of short length papers submitted'}),
            'editor_agreement': FileInput(attrs={'accept': '.pdf', 
                                                 'placeholder': 'Upload the agreement file'}),
                                
       }
        
    def __init__(self, *args, **kwargs):
        # loads language options and returns proper ISO

        super(WorkshopForm, self).__init__(*args, **kwargs)
        json_file_path = os.path.join(os.path.dirname(__file__), 'static', 'workshops', 'languages.json')
        
        # Load JSON data from the file
        with open(json_file_path, 'r') as file:
            languages = json.load(file)
        
        # Populate dropdown choices from JSON data
        choices = [(data['639-2'], data['name']) for code, data in languages.items()]
        self.fields['workshop_language_iso'].choices = choices

    def clean(self):
        cleaned_data = super().clean()

        total_submitted_papers = cleaned_data.get('total_submitted_papers')
        total_accepted_papers = cleaned_data.get('total_accepted_papers')
        total_reg_acc_papers = cleaned_data.get('total_reg_acc_papers', 0)  
        total_short_acc_papers = cleaned_data.get('total_short_acc_papers', 0)  

        if total_accepted_papers > total_submitted_papers:
            raise ValidationError("The number of accepted papers cannot exceed the number of submitted papers.")

        if total_reg_acc_papers is not None and total_short_acc_papers is not None:
            if (total_reg_acc_papers + total_short_acc_papers) != total_accepted_papers:
                raise ValidationError("The sum of regular and short accepted papers must equal the total number of accepted")

        return cleaned_data

class PaperForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        file_uploaded = kwargs.pop('file_uploaded', False)
        self.workshop = kwargs.pop('workshop', None) 
        super(PaperForm, self).__init__(*args, **kwargs)
    
        if file_uploaded:
            self.fields['uploaded_file'].label = 'Change current file'
        else:
            self.fields['uploaded_file'].label = 'Upload file'

        if self.workshop: 
            self.fields['session'].queryset = self.workshop.sessions.all()
        else:
            self.fields['session'].queryset = Session.objects.none()  # No sessions available if workshop is not provided

    class Meta:
        model = Paper
        fields = ['paper_title', 'pages', 'session', 'uploaded_file', 'agreement_file']

        widgets = {
            'paper_title': forms.TextInput(attrs={'size': 70, 'placeholder': 'Enter the title of the paper'}),
            'pages': forms.TextInput(attrs={'size': 70, 'placeholder': 'Enter the number of pages'}),
            'uploaded_file': forms.FileInput(attrs={'accept': '.pdf'}),
            'agreement_file': forms.FileInput(attrs={'accept': '.pdf'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        agreement_file = cleaned_data.get('agreement_file')
        uploaded_file = cleaned_data.get('uploaded_file')
        
        if uploaded_file and agreement_file and self.workshop:
            directory_path = os.path.join('agreement', f'VOL-{self.workshop.id}')

            # agreement_file_name = os.path.join(directory_path, agreement_file.name)
            agreement_file_path = os.path.join(settings.MEDIA_ROOT, agreement_file.name)
            default_storage.save(agreement_file.name, ContentFile(agreement_file.read()))

            self.instance.agreement_file = agreement_file.name
            
            if not self._detect_signature_in_image(agreement_file_path):
                raise ValidationError("Agreement file is not signed. Please upload a hand-signed agreement file.")
    
        else: 
            raise ValidationError("Paper and/or agreement not saved.")
        
        return cleaned_data

    def _detect_signature_in_image(self, file_path):
        loader = Loader()
        extractor = Extractor()
        cropper = Cropper(border_ratio=0)
        judger = Judger()

        masks = loader.get_masks(file_path)
        is_signed = False
        for mask in masks:
            labeled_mask = extractor.extract(mask)
            results = cropper.run(labeled_mask)
            for result in results.values():
                is_signed = judger.judge(result["cropped_mask"])
                if is_signed:
                    break
            if is_signed:
                break
        return is_signed

AuthorFormSet = modelformset_factory(
        Author, fields=('author_name', 'author_university', 'author_uni_url', 'author_email'), extra=0,
        # CSS styling but for formsets
        widgets = {
            'author_name': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Enter the name of the author'}),
            'author_university': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Enter the university of the author'}),
            'author_uni_url': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Enter the URL of the university'}),
            'author_email': TextInput(attrs={'size': 50,
                                            'placeholder': 'Enter the email of the author'})
        })

EditorFormSet = modelformset_factory(
    Editor, fields=('editor_name','editor_url' ,'institution', 'institution_country', 'institution_url', 'research_group'), extra=0,
    # CSS styling but for formsets
    widgets = {
        'editor_name': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Provide the name of the editor'}),
        'editor_url': TextInput(attrs={'size': 70, 
                                            'placeholder': '(optional) Provide the personal url of the editor'}),
        'institution': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Provide the institution (company or university) of the editor'}),
        'institution_country': CountrySelectWidget(),

        'institution_url': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Provide the URL of the institution (company or university)'}),
        'research_group': TextInput(attrs={'size': 70, 
                                            'placeholder': '(optional) Provide the research group of the editor'})
    }
)

SessionFormSet = modelformset_factory(
    Session, fields=('session_title',), extra=0,
    # CSS styling but for formsets
    widgets = {
        'session_title': TextInput(attrs={'size': 70, 
                                            'placeholder': '(optional) Title of the session'}),

    }
)