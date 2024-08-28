
from .models import *
from django import forms
from django.forms import modelformset_factory, inlineformset_factory, TextInput, FileInput, Textarea, CheckboxInput, URLInput, BaseModelFormSet
from django_countries.widgets import CountrySelectWidget
import os, json
from django.core.exceptions import ValidationError
# from signature_detect.loader import Loader
# from signature_detect.extractor import Extractor
# from signature_detect.cropper import Cropper
# from signature_detect.judger import Judger
from django.conf import settings
from django.core.files.storage import default_storage
from crispy_forms.helper import FormHelper
from django.forms import URLField
from functools import partial
from django.core.files.base import ContentFile
from django.core.validators import URLValidator
import PyPDF2

class DateInput(forms.DateInput):
    input_type = "date"
    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)

# def _detect_signature_in_image(file_path):
#         loader = Loader()
#         extractor = Extractor()
#         cropper = Cropper(border_ratio=0)
#         judger = Judger()

#         masks = loader.get_masks(file_path)
#         is_signed = False
#         for mask in masks:
#             labeled_mask = extractor.extract(mask)
#             results = cropper.run(labeled_mask)
#             for result in results.values():
#                 is_signed = judger.judge(result["cropped_mask"])
#                 if is_signed:
#                     break
#             if is_signed:
#                 break
#         return is_signed

class WorkshopForm(forms.ModelForm):
    workshop_language_iso = forms.ChoiceField(label="Language", choices=[], required=False)
    class Meta:
        model = Workshop
        fields = ['workshop_short_title', 'workshop_full_title', 'workshop_acronym',
                'workshop_language_iso', 'workshop_description', 'workshop_country',  'workshop_city', 'year_final_papers', 'workshop_colocated',
                'workshop_begin_date', 'workshop_end_date', 'year_final_papers', 'volume_owner',
                'volume_owner_email', 'total_submitted_papers', 'total_accepted_papers', 'total_reg_acc_papers', 'total_short_acc_papers', 'editor_agreement',
                'editor_agreement_signed']
        
        widgets = {
            'workshop_short_title': TextInput(attrs={'size': 100, 
                                            'placeholder': 'Provide the shorthand title of the workshop',
                                            'strip':True,
                                            }),
            'workshop_full_title': TextInput(attrs={'size': 100, 
                                            'placeholder': 'Provide the full title of the workshop',
                                            'strip':True,
                                            }),
            'workshop_acronym': TextInput(attrs={'size': 100, 
                                            'placeholder': 'Provide the acronym of the workshop',
                                            'strip':True,}),
            'workshop_language_iso': TextInput(attrs={'size': 100, 
                                            'placeholder': 'Enter ISO of the language of the workshop',
                                            'strip':True,
                                            },),
            'workshop_description': Textarea(attrs={'cols': 82, 'rows' : 10, 
                                                     'placeholder': 'Briefly describe the workshop',
                                                        'strip':True,
                                                     }),
            'workshop_city': TextInput(attrs={'size': 100, 
                                            'placeholder': 'The city the workshop took place in',
                                            'strip':True,}),
            'workshop_country': CountrySelectWidget(),

            'workshop_begin_date': DateInput(attrs={'id': 'workshop_begin_date'}),

            'workshop_end_date': DateInput(attrs={'id': 'workshop_end_date'}),

            'year_final_papers': TextInput(attrs={'size': 100, 
                                            'placeholder': 'Provide the year the final papers of the proceedings were produced',
                                            'strip':True,}),
            'workshop_colocated': TextInput(attrs={'size': 100, 
                                            'placeholder': '(optional) Provide the workshop with which this workshop was colocated',
                                            'strip':True,}),
            'license': TextInput(attrs={'size': 100, 
                                            'placeholder': 'MIT',
                                            'strip':True,}),
            'volume_owner': TextInput(attrs={'size': 100,
                                            'placeholder': 'Provide the volume creator\'s (your) name',
                                            'strip':True,}),
            'volume_owner_email': TextInput(attrs={'size': 100,
                                            'placeholder': 'Provide the volume creator\'s (your) e-mail',
                                            'strip':True,}),
            'total_submitted_papers': TextInput(attrs={'size': 100,
                                            'placeholder': 'Provide the total number of papers submitted to the workshop',
                                            'strip':True,}),
            'total_accepted_papers': TextInput(attrs={'size': 100,
                                            'placeholder': 'Provide the total number of accepted papers submitted to the workshop',
                                            'strip':True,}),
            'total_reg_acc_papers': TextInput(attrs={'size': 100,
                                            'placeholder': '(optional) Provide the total number of regular length papers submitted',
                                            'strip':True,}),
            'total_short_acc_papers': TextInput(attrs={'size': 100,
                                            'placeholder': '(optional) Provide the total number of short length papers submitted',
                                            'strip':True,}),
            'editor_agreement': FileInput(attrs={'accept': '.pdf', 
                                                 'placeholder': 'Upload the agreement file'}),                
            'editor_agreement_signed': CheckboxInput(attrs={'required': True}),
       }
        
        labels = {
            'total_submitted_papers': "Total number of submitted papers",
            'total_short_acc_papers': "Total number of short accepted papers",
            'total_reg_acc_papers': "Total number of regular accepted papers",
        },
        
    def __init__(self, *args, **kwargs):
        # loads language options and returns proper ISO
        fields_not_required = kwargs.pop('fields_not_required', False)
        super(WorkshopForm, self).__init__(*args, **kwargs)
        json_file_path = os.path.join(os.path.dirname(__file__), 'static', 'workshops', 'languages.json')
        
        # Load JSON data from the file
        with open(json_file_path, 'r') as file:
            languages = json.load(file)
        
        # Populate dropdown choices from JSON data
        choices = [(data['639-2'], data['name']) for code, data in languages.items()]
        self.fields['workshop_language_iso'].choices = choices
        # default language 
        self.fields['workshop_language_iso'].initial = 'eng'
        self.fields['workshop_country'].initial = 'NL'
        email = kwargs.pop('volume_owner_email', None)
        
        self.fields['volume_owner_email'] = forms.EmailField(initial=email, required=True, max_length=200, label='Volume owner email', help_text='<br><i>Provide the email of the volume owner</i>')
        self.fields['volume_owner_email'].widget.attrs['placeholder'] = 'Enter the email of the volume owner'
        self.fields['volume_owner_email'].widget.attrs['size'] = 100
        self.fields['workshop_colocated'].help_text = "<i>Please provide the acronym (acronym-YYYY) of the conference with which this workshop was colocated; if the workshop was not colocated with any conference, leave this field empty.</i>"
        self.fields['workshop_acronym'].help_text ='<i>Please provide the acronym of the workshop plus YYYY (year of the workshop in exactly 4 digits, e.g. 2012). Between the acronym and the year a \'-\' should be placed.</i>'

        if fields_not_required: 
            self.fields['workshop_short_title'].required = False
            self.fields['workshop_full_title'].required = False
            self.fields['workshop_acronym'].required = False
            self.fields['workshop_description'].required = False
            self.fields['workshop_country'].required = False
            self.fields['workshop_city'].required = False
            self.fields['year_final_papers'].required = False
            self.fields['workshop_begin_date'].required = False
            self.fields['workshop_end_date'].required = False
            self.fields['volume_owner'].required = False
            self.fields['volume_owner_email'].required = False
            self.fields['total_submitted_papers'].required = False
            self.fields['total_accepted_papers'].required = False

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return valid

        total_submitted_papers = self.cleaned_data.get('total_submitted_papers', 0)
        total_accepted_papers = self.cleaned_data.get('total_accepted_papers', 0)
        total_reg_acc_papers = self.cleaned_data.get('total_reg_acc_papers', 0)  
        total_short_acc_papers = self.cleaned_data.get('total_short_acc_papers', 0)  
    
        if total_accepted_papers is not None and total_submitted_papers is not None: 
            if total_accepted_papers > total_submitted_papers:
                self.add_error('total_accepted_papers', "The number of accepted papers cannot exceed the number of submitted papers.")
                return False

        if total_reg_acc_papers is not None and total_short_acc_papers is not None:
            if (total_reg_acc_papers + total_short_acc_papers) != total_accepted_papers:
                self.add_error('total_reg_acc_papers', "The sum of regular and short accepted papers must equal the total number of accepted")
                return False
            
        return True

class PaperForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        file_uploaded = kwargs.pop('file_uploaded', False)
        self.workshop = kwargs.pop('workshop', None)
        hide_pages = kwargs.pop('hide_pages', False)
        pages = kwargs.pop('pages', None)
        self.hide_agreement = kwargs.pop('hide_agreement', False)
        hide_has_third_party_material = kwargs.pop('hide_has_third_party_material', True)
        self.agreement_file = kwargs.pop('agreement_file', False)
        self.clean_enabled = kwargs.pop('clean_enabled', False)
        self.agreement_not_required = kwargs.pop('agreement_not_required', False)
        super(PaperForm, self).__init__(*args, **kwargs)
 
        self.fields['session'].queryset = self.workshop.sessions.all() if self.workshop else Session.objects.none()

        self.fields['uploaded_file'].label = 'Change current file' if file_uploaded else 'Upload file'

        self.fields['agreement_file'].label = 'Upload agreement file' if self.agreement_file else 'Please Upload the hand signed agreement file'

        if hide_pages:
            self.fields['pages'].widget = forms.HiddenInput()

        if pages is not None:
            self.fields['pages'].initial = pages

        if self.agreement_not_required:
            self.fields['agreement_file'].required = False
            self.fields['agreement_file'].widget.attrs.pop('required', None)
            
        if self.hide_agreement:
            self.fields['agreement_file'].widget = forms.HiddenInput()
            self.fields['agreement_file'].required = False

        if hide_has_third_party_material:
            self.fields['has_third_party_material'].widget = forms.HiddenInput()

    class Meta:
        model = Paper
        fields = ['paper_title', 'pages', 'session', 'agreement_file', 'has_third_party_material','uploaded_file', 'complete']
        help_texts = {'pages': '<br><i>Provide the length(number of pages) of the paper</i>.<br>',
                      'has_third_party_material': '<i>Check this box if the paper contains third-party material</i>'}
        widgets = {
            'paper_title': forms.TextInput(attrs={'size': 70, 'placeholder': 'Enter the title of the paper', 'strip': True}),
            'pages': forms.TextInput(attrs={'size': 70, 'placeholder': 'Enter the number of pages'}),
            'uploaded_file': forms.FileInput(attrs={'accept': '.pdf'}),
            'agreement_file': forms.FileInput(attrs={'accept': '.pdf, .html'}),

            #  required: True is needed here for the __init__ to work in author_upload
            'complete' : CheckboxInput(attrs={}),
        }
        labels = {
            'complete': 'Check this box if the details of this paper are complete and final',
        }

        paper_title = forms.CharField(strip=True)

    def clean(self):
        cleaned_data = super().clean()
        uploaded_file = cleaned_data.get('uploaded_file')

        if self.clean_enabled:
            pdfReader = PyPDF2.PdfReader(uploaded_file)
            num_pages = len(pdfReader.pages)
            cleaned_data['pages'] = num_pages
        return cleaned_data
        
        # if not self._detect_signature_in_image(agreement_file_path):
        #     print("Agreement file is not signed. Please upload a hand-signed agreement file.")
        #     raise ValidationError("Agreement file is not signed. Please upload a hand-signed agreement file.")
        
class CustomBaseModelFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.agreement_not_required = kwargs.pop('agreement_not_required', False)
        self.hide_agreement = kwargs.pop('hide_agreement', False)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['agreement_not_required'] = self.agreement_not_required
        kwargs['hide_agreement'] = self.hide_agreement
        return super()._construct_form(i, **kwargs)

    def __iter__(self):
        sorted_forms = sorted(self.forms, key=lambda form: form.instance.order if form.instance.pk else 0)
        return iter(sorted_forms)

    def __getitem__(self, index):
        sorted_forms = sorted(self.forms, key=lambda form: form.instance.order if form.instance.pk else 0)
        return sorted_forms[index]

PaperFormset = modelformset_factory(
    Paper, 
    form=PaperForm, 
    formset=CustomBaseModelFormSet,
    extra=0,
)

# function to generate formsets, so the extra parameter can be set dynamically in case of initial data.
def get_author_formset(extra=0):
    return modelformset_factory(
        Author, fields=('author_name', 'author_university', 'author_uni_url', 'author_email'), extra=extra,
        widgets={
            'author_name': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Enter the name of the author',
                                            'strip':True,}),
            'author_university': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Enter the university of the author',
                                            'strip':True}),
            'author_uni_url': TextInput(attrs={'size': 70, 
                                            'placeholder': 'Enter the URL of the university which the author is affiliated to',
                                            'strip':True,}),
            'author_email': TextInput(attrs={'size': 50,
                                            'placeholder': 'Enter the email of the author',
                                            'strip':True,}),
        },
        labels={
            'author_uni_url': "University URL",
        },
    )

class EditorForm(forms.ModelForm):
    
    class Meta:
        model = Editor
        fields = ['editor_name', 'editor_url', 'institution', 'institution_country', 'institution_url', 'research_group']
        widgets = {
            'editor_name': forms.TextInput(attrs={'size': 100, 
                                                  'placeholder': 'Provide the name of the editor',
                                                  'strip':True,}),
            'editor_url': forms.TextInput(attrs={'size': 100, 
                                                 'placeholder': '(optional) Provide the URL of the editor e.g. https://www.example.com',
                                                 'strip':True,}),
            'institution': forms.TextInput(attrs={'size': 100, 
                                                  'placeholder': 'Provide the institution (company or university)',
                                                  'strip':True,}),
            'institution_country': CountrySelectWidget(),
            'institution_url': forms.TextInput(attrs={'size': 100, 
                                                      'placeholder': 'Provide the URL of the institution e.g. https://www.example.com',
                                                      'strip':True,}),
            'research_group': forms.TextInput(attrs={'size': 70, 
                                                     'placeholder': '(optional) Provide the research group of the editor',
                                                     'strip':True,}),
        }

EditorFormSet = modelformset_factory(
    Editor, form=EditorForm, extra=0,
)

SessionFormSet = modelformset_factory(
    Session, fields=('session_title',), extra=0,
    widgets = {
        'session_title': TextInput(attrs={'size': 70, 
                                            'placeholder': '(optional) Title of the session'}),
    }
)
class WorkshopPrefaceForm(forms.ModelForm):
    class Meta:
        model = Preface
        fields = ['preface']

PrefaceFormset = inlineformset_factory(Workshop, Preface, form=WorkshopPrefaceForm, extra=0, can_delete=False)