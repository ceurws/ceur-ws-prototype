  
class CreateWorkshop(View):

    def get(self, request):
        form = WorkshopForm()
        editor_form = EditorFormSet(queryset=Editor.objects.none(), 
                                    prefix='editor')
        session_form = SessionFormSet(queryset=Session.objects.none(), 
                                      prefix='session')
        context = {'form':form, 
                   'editor_form':editor_form, 
                   'session_form':session_form}
        return render(request, "workshops/create_workshop.html", context)
    
    def post(self, request):
        success_path = "workshops/workshop_edit_success.html"
        edit_path = "workshops/edit_workshop.html"
        
        editor_form = EditorFormSet(queryset=Editor.objects.none(),data = request.POST, prefix="editor")
        session_form = SessionFormSet(queryset=Session.objects.none(),data = request.POST, prefix="session")

        workshop_instance = Workshop.objects.filter(workshop_acronym = request.POST.get('workshop_acronym')).first()
        form = WorkshopForm(data = request.POST, files = request.FILES, instance = workshop_instance) 


        if 'submit_button' in request.POST:
            if all([form.is_valid(), editor_form.is_valid(), session_form.is_valid()]):
                workshop = form.save(commit = False)  
                
                workshop.editor_agreement = request.FILES.get('editor_agreement')
                editor_instances = editor_form.save()
                session_instances = session_form.save()

                workshop.editors.add(*editor_instances)
                workshop.sessions.add(*session_instances)

                workshop.save()

                organizer_url = reverse('workshops:workshop_overview', args=[workshop.secret_token])
                author_url = reverse('workshops:author_upload', args=[workshop.secret_token])
                context = {
                    'organizer_url': organizer_url,
                    'author_url': author_url
                }
                return render(request, success_path, context)
            else:
                context = {'form': form, 
                           'editor_form':editor_form, 
                           'session_form':session_form}
                return render(request, edit_path, context)
        else:
            if all([form.is_valid(), editor_form.is_valid(), session_form.is_valid()]):
                workshop = form.save(commit=False)  
                workshop.editor_agreement = request.FILES.get('editor_agreement')
                workshop.save()
            
                context = {'form': form, 
                           'editor_form':editor_form, 
                           'session_form':session_form}
                return render(request, edit_path, context)
            else:
                context = {'form': form, 
                           'editor_form':editor_form, 
                           'session_form':session_form}
                return render(request, edit_path, context)



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
        editor_agreement = cleaned_data.get('editor_agreement')

        if total_accepted_papers > total_submitted_papers:
            raise ValidationError("The number of accepted papers cannot exceed the number of submitted papers.")

        if total_reg_acc_papers is not None and total_short_acc_papers is not None:
            if (total_reg_acc_papers + total_short_acc_papers) != total_accepted_papers:
                raise ValidationError("The sum of regular and short accepted papers must equal the total number of accepted")
            
        if not editor_agreement:
            raise ValidationError("Please upload the agreement file.")
        if editor_agreement:
            pass
            # editor_agreement_file_path = os.path.join(settings.MEDIA_ROOT, editor_agreement.name)
            # default_storage.save(editor_agreement.name, ContentFile(editor_agreement.read()))
            
            # if not self._detect_signature_in_image(editor_agreement_file_path):
            #     raise ValidationError("Agreement file is not signed. Please upload a hand-signed agreement file.")

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