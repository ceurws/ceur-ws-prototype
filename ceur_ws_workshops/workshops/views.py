from django.shortcuts import render, get_object_or_404, redirect
from .models import Workshop, Paper, Editor, Author, Session
from django.conf import settings
from django.urls import reverse
from django.views import View
from .forms import WorkshopForm, EditorFormSet, AuthorFormSet, PaperForm, SessionFormSet
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
import json, os, zipfile
from datetime import date
from django.core.serializers.json import DjangoJSONEncoder
from signature_detect.loader import Loader
from signature_detect.extractor import Extractor
from signature_detect.cropper import Cropper
from signature_detect.judger import Judger
from django.conf import settings

def index(request):
    """
    Renders the home page of the workshop site.
    """
    return render(request, 'workshops/index.html')
    
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
    
    def post(self,request):
        success_path = "workshops/workshop_edit_success.html"
        edit_path = "workshops/edit_workshop.html"

        editor_form = EditorFormSet(queryset=Editor.objects.none(),data = request.POST,prefix="editor")
        session_form = SessionFormSet(queryset=Session.objects.none(),data = request.POST,prefix="session")
        form = WorkshopForm(data = request.POST, files = request.FILES)

        if 'submit_button' in request.POST:
            if all([form.is_valid(), editor_form.is_valid(), session_form.is_valid()]):
                workshop = form.save(commit=False)  
                workshop.save()  
                workshop.editor_agreement = request.FILES['editor_agreement']
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
                form.save(commit=False)
                if 'editor_agreement' not in request.FILES:
                    print(request.FILES['editor_agreement'])
                    workshop.editor_agreement = request.FILES['editor_agreement']
                context = {'form': form, 
                           'editor_form':editor_form, 
                           'session_form':session_form}
                return render(request, edit_path, context)
            else:
                context = {'form': form, 
                           'editor_form':editor_form, 
                           'session_form':session_form}
                return render(request, edit_path, context)

class WorkshopOverview(View):
    def get_workshop(self):
        workshop = get_object_or_404(Workshop, secret_token=self.kwargs['secret_token'])
        return workshop
    
    def render_workshop(self, request, edit_mode = False):
        workshop = self.get_workshop()

        return render(request, 'workshops/workshop_overview.html', context = {
            'papers' : [paper for paper in workshop.accepted_papers.all()],
            'workshop' : workshop,
            'workshop_form': WorkshopForm(instance=workshop),
            'paper_forms' : [PaperForm(instance=paper_instance) for paper_instance in workshop.accepted_papers.all()],
            'session_title_list' : [session_object.session_title for session_object in workshop.sessions.all()],
            'edit_mode': edit_mode,
            'secret_token': self.kwargs['secret_token']
        })

    def get(self, request, secret_token):
        return self.render_workshop(request)        
    
    def _get_workshop_data(self, workshop):
        return {
            "JJJJ":	workshop.year_final_papers,
            "YYYY": workshop.workshop_begin_date.year, 
            "NNNN": workshop.workshop_acronym,
            # "DD": date.today().day,
            # "MM": date.today.month,
            "XXX": workshop.volume_number,
            "CEURLANG": workshop.workshop_language_iso,
            "CEURVOLNR": workshop.pk,
            "CEURPUBYEAR":str(workshop.workshop_begin_date.year), #workshop_begin_date
            "CEURURN": workshop.urn,
            "CEURVOLACRONYM": workshop.workshop_acronym,
            "CEURVOLTITLE": workshop.workshop_short_title,
            "CEURFULLTITLE": workshop.workshop_full_title,
            "CEURDESCRIPTION": workshop.workshop_description,
            "CEURCOLOCATED": workshop.workshop_colocated,
            "CEURLOCTIME":{
                "CEURCITY": workshop.workshop_city,
                "CEURCOUNTRY": workshop.workshop_country,
                "CEURBEGINDATE": workshop.workshop_begin_date,
                "CEURENDDATE": workshop.workshop_end_date,
            },
            "CEUREDITORS": [],
            "email_address": workshop.volume_owner_email,
            
            "CEURSESSIONS": [],
            "CEURPAPERS": [],
            "CEURPUBDATE": date.today(),
            "CEURSUBMITTEDPAPERS": workshop.total_submitted_papers,
            "CEURACCEPTEDPAPERS": workshop.total_accepted_papers,
            "CEURACCEPTEDSHORTPAPERS": workshop.total_reg_acc_papers,
            "CEURACCEPTEDSHORTPAPERS": workshop.total_short_acc_papers,
            "CEURLIC": workshop.license,
            "secret_token": str(workshop.secret_token),
        }
    
    def add_editors_data(self, workshop, workshop_data):
        editors_data = [
        {
            "CEURVOLEDITOR": editor.editor_name,
            "CEUREDITOREMAIL": editor.editor_url,
            "CEURINSTITUTION": editor.institution,
            "CEURCOUNTRY": editor.institution_country,
            "CEURINSTITUTIONURL": editor.institution_url,
            "CEURRESEARCHGROUP": editor.research_group 
        }
        for editor in workshop.editors.all()
        ]
        workshop_data['CEUREDITORS'] = editors_data

    def add_papers_data(self, workshop, workshop_data):
        if workshop.sessions.exists():
            sessions_data = []
            for session in workshop.sessions.all():
                session_data = {
                    "session_title": session.session_title,
                    "papers": [
                        {
                            "CEURTITLE": paper.paper_title,
                            "CEURPAGES": paper.pages,
                            "CEURAUTHOR": [str(author) for author in paper.authors.all()],
                            "uploaded_file_url": paper.uploaded_file.url if paper.uploaded_file else None,
                            "agreement_file_url": paper.agreement_file.url if paper.agreement_file else None,
                        }
                        for paper in session.paper_set.all()
                    ]
                }
                sessions_data.append(session_data)
            workshop_data['CEURSESSIONS'] = sessions_data
            del(workshop_data['CEURPAPERS'])
        else:
            papers_data = [
                {
                    "CEURTITLE": paper.paper_title,
                    "CEURPAGES": paper.pages,
                    "CEURAUTHOR": [str(author) for author in paper.authors.all()],
                    "uploaded_file_url": paper.uploaded_file.url if paper.uploaded_file else None,
                    "agreement_file_url": paper.agreement_file.url if paper.agreement_file else None,
                }
                for paper in workshop.accepted_papers.all()
            ]
            del(workshop_data['CEURSESSIONS'])
            workshop_data['CEURPAPERS'] = papers_data

    def _save_workshop_data(self, workshop_data, workshop):
        directory_path = os.path.join(settings.BASE_DIR, 'workshop_metadata')
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path, f'workshop_{workshop.id}_metadata.json')

        with open(file_path, 'w') as file:
            json.dump(workshop_data, file, cls=DjangoJSONEncoder, indent=4)

    def _zip_agreement_files(self, workshop):
        agreement_path = os.path.join(settings.MEDIA_ROOT, 'agreement', f'Vol-{workshop.id}', )
        os.makedirs('zipped_agreements', exist_ok=True)
        zip_filename = os.path.join(settings.BASE_DIR, 'zipped_agreements', f'AGREEMENTS-Vol-{workshop.id:04d}.zip')
    
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, _, files in os.walk(agreement_path):
                for file in files:
                    print("Adding file", os.path.join(root, file))
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), agreement_path))
    
    def submit_workshop(self, request, secret_token):
        submit_path = 'workshops/submit_workshop.html'

        workshop = get_object_or_404(Workshop, secret_token=secret_token)
        workshop_data = self._get_workshop_data(workshop)

        self.add_editors_data(workshop, workshop_data)
        self.add_papers_data(workshop, workshop_data)   
        self._save_workshop_data(workshop_data, workshop)
        request.session['json_saved'] = True

        self._zip_agreement_files(workshop)
        messages.success(request, 'Workshop submitted successfully.')

        return render(request, submit_path)
    
    def post(self, request, secret_token):

        if request.POST["submit_button"] == "Edit":
            return self.render_workshop(request, edit_mode = True)
        elif request.POST["submit_button"] == "Confirm":
            workshop_form = WorkshopForm(instance=self.get_workshop(), data=request.POST)

            if workshop_form.is_valid():
                workshop_form.save()

            uploaded_files = request.FILES.getlist('uploaded_file')
            agreement_files = request.FILES.getlist('agreement_file')

            existing_paper_ids = request.POST.getlist('paper_id')  
            papers_to_delete = request.POST.getlist('papers_to_delete') 

            for paper_id in papers_to_delete:
                Paper.objects.filter(id=paper_id).delete()

            for i, paper_id in enumerate(existing_paper_ids):
                if paper_id in papers_to_delete:
                    continue  

                paper_instance = Paper.objects.filter(id=paper_id).first() if paper_id else None
                paper_form_data = request.POST.copy()
                if i < len(uploaded_files):
                    paper_form_data['uploaded_file'] = uploaded_files[i]
                if i < len(agreement_files):
                    paper_form_data['agreement_file'] = agreement_files[i]

                paper_form = PaperForm(paper_form_data, instance=paper_instance)
                if paper_form.is_valid():
                    paper_form.save()

            return self.render_workshop(request, edit_mode=False)
        elif request.POST["submit_button"] == "Submit Workshop":
            return self.submit_workshop(request, secret_token)
        
class AuthorUpload(View):
    upload_path = "workshops/author_upload.html"
    edit_path  = "workshops/edit_author.html"
    success_path = "workshops/author_upload_success.html"
    
    def get_workshop(self):
        workshop = get_object_or_404(Workshop, secret_token=self.kwargs['secret_token'])
        return workshop
    
    def get_context(self, author_formset, paper_form, condition='default', edit_paper_url=None):
        if condition == 'author':
            return {'author_formset': author_formset, 'paper_form': paper_form}
        elif condition == "confirm":
            return {'workshop': self.get_workshop(), 'paper': paper_form, 'authors': author_formset, 'edit_paper_url': edit_paper_url}
        return {'workshop': self.get_workshop(), 'author_formset': author_formset, 'paper_form': paper_form}
    
    def _get_agreement_filename(self, paper_instance, original_filename):
        paper_title = paper_instance.paper_title.replace(' ', '')
        extension = os.path.splitext(original_filename)[1]
        new_filename = f'AUTHOR-AGREEMENT-{paper_title}{extension}'
        return new_filename
    
    def submit_paper(self, request, author_formset, paper_form):

        author_instances = None

        if paper_form.is_valid() and author_formset.is_valid():
            paper_instance = paper_form.save(commit=False)
            paper_instance.workshop = self.get_workshop()
            paper_instance.save()

            author_instances = author_formset.save()

            if request.POST['session'] != '':
                session_instance = Session.objects.get(pk=request.POST['session'])
                paper_instance.session = session_instance
            
            paper_instance.authors.add(*author_instances)
            self.get_workshop().accepted_papers.add(paper_instance)

            return redirect('workshops:edit_author_post', paper_id = paper_instance.secret_token, secret_token = self.kwargs['secret_token'])
        else:
            print("Paperform not valid")
            return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))
        
    def create_paper(self, request, author_formset, paper_form):

        # check whether files are signed
        if paper_form.is_valid() and author_formset.is_valid():
            paper_instance = paper_form.save(commit=False) 
            paper_instance.workshop = self.get_workshop()
            paper_instance.uploaded_file = request.FILES['uploaded_file']
            paper_instance.agreement_file = request.FILES['agreement_file']
            paper_instance.agreement_file.name = self._get_agreement_filename(paper_instance, paper_instance.agreement_file.name)
            
            paper_instance.save()  
            # author_instances = author_formset.save()

            if request.POST['session'] != '':
                session_instance = Session.objects.get(pk=request.POST['session'])
                paper_instance.session = session_instance

            # paper_instance.authors.add(*author_instances)  
            self.get_workshop().accepted_papers.add(paper_instance)  
            
            return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))
        else:
            return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))

    def get(self, request, secret_token):
        author_formset = AuthorFormSet(queryset=Author.objects.none(), prefix="author")
        paper_form = PaperForm(file_uploaded=False, workshop=self.get_workshop())
        context = self.get_context(author_formset, paper_form)
        return render(request, self.upload_path, context)

    def post(self, request, secret_token):
        
        # if statement to check if request.FILES has any new files attached. 
        if bool(request.FILES.get('agreement_file', False)) == True and bool(request.FILES.get('uploaded_file', False)) == True:
            author_formset = AuthorFormSet(queryset=Author.objects.none(), data = request.POST, prefix="author")
            paper_form = PaperForm(request.POST, request.FILES, file_uploaded=True, workshop=self.get_workshop())
       
        # if no files are attached we extract the files uploaded 
        else:
            author_formset = AuthorFormSet(request.POST, prefix="author")

            paper_instance = Paper.objects.filter(paper_title=request.POST.get('paper_title'), workshop = self.get_workshop()).first()

            paper_form = PaperForm(request.POST, file_uploaded=True, workshop=self.get_workshop(), instance = paper_instance)
        # print(author_formset)
        if 'confirm_button' in request.POST:
            return self.submit_paper(request, author_formset, paper_form)
        
        else:
            return self.create_paper(request, author_formset, paper_form)
        
def edit_author_post_view(request, paper_id, secret_token):
    workshop = get_object_or_404(Workshop, secret_token=secret_token)
    paper = get_object_or_404(Paper, secret_token=paper_id)

    context = {
        'workshop' : workshop,
        'paper_form' : None,
        'paper' : paper, 
        'author_formset' : None,
        'edit_mode': False
    }

    if request.method == "POST":
        paper_form = PaperForm(data=request.POST, instance=paper, workshop=workshop)
        author_formset = AuthorFormSet(data = request.POST, queryset=Author.objects.filter(paper = paper), prefix = 'author')
        
        if 'edit_button' in request.POST:
            paper_form = PaperForm(instance=paper, workshop=workshop)
            author_formset = AuthorFormSet(queryset=Author.objects.filter(paper = paper), prefix = 'author')
            context.update({'paper_form': paper_form, 'author_formset': author_formset, 'edit_mode': True})

        elif 'submit_button' in request.POST and paper_form.is_valid() and author_formset.is_valid():
            paper_form.save()
            author_formset.save()
            context.update({'paper_form': paper_form, 'author_formset': author_formset, 'edit_mode': False})
    return render(request, 'workshops/author_upload_success.html', context)