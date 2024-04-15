from typing import Any
from django.shortcuts import render, redirect
from .models import Workshop, Paper, Editor, Author
import uuid
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.core import serializers
from .forms import WorkshopForm, EditorFormSet, AuthorFormSet, PaperForm
from django.contrib import messages
from django.conf import settings
import os
from signature_detect.loader import Loader
from signature_detect.extractor import Extractor
from signature_detect.cropper import Cropper
from signature_detect.judger import Judger

def index(request):
    """
    Renders the home page of the workshop site.
    """
    return render(request, 'workshops/index.html')
    
class CreateWorkshop(View):
    def get(self, request):
        form = WorkshopForm()
        editor_form = EditorFormSet(queryset=Editor.objects.none())
        return render(request, "workshops/create_workshop.html", {'form':form, 'editor_form':editor_form})

    def post(self,request):

        # handles logic to save the data when the user has confirmed the changes
        if 'submit_button' in request.POST:
            formset = EditorFormSet(request.POST)
            form = WorkshopForm(request.POST)

            if form.is_valid() and formset.is_valid():
                workshop = form.save()  
                instances = formset.save()
                workshop.editors.add(*instances)

                organizer_url = reverse('workshops:workshop_overview', args=[workshop.secret_token])
                author_url = reverse('workshops:author_upload', args=[workshop.secret_token])

                return render(request, "workshops/workshop_edit_success.html", {
                    'organizer_url': organizer_url,
                    'author_url': author_url
                })
        
        # handles logic to showcase the data so that the user can confirm it
        else:
            form = WorkshopForm(request.POST)
            editor_form = EditorFormSet(queryset=Editor.objects.none(),data = request.POST)

            if form.is_valid():
                return render(request, 'workshops/edit_workshop.html', {'form': form, 'editor_form':editor_form})

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
            'edit_mode': edit_mode,
            'secret_token': self.kwargs['secret_token']
        })

    def get(self, request, secret_token):
        return self.render_workshop(request)

    def submit_workshop(self, request, secret_token):
        workshop = get_object_or_404(Workshop, secret_token=secret_token)

        workshop_json = serializers.serialize('json', [workshop,])
        directory_path = os.path.join(settings.BASE_DIR, 'workshop_metadata')
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path, f'workshop_{workshop.id}_metadata.json')
    
        with open(file_path, 'w') as file:
            file.write(workshop_json)
        request.session['json_saved'] = True
        messages.success(request, 'Workshop submitted successfully.')

        return render(request, 'workshops/submit_workshop.html')
    
    def post(self, request, secret_token):

        # renders the workshop overview page in edit mode, allowing to edit all fields
        if request.POST["submit_button"] == "Edit":
            return self.render_workshop(request, edit_mode = True)
        # saves the changes when user is in edit mode and takes user out of edit mode.
        elif request.POST["submit_button"] == "Confirm":

            # Modifies the first entry of the paper (regardless which one we want to update), not working
            # but thought it might be on the right track...
            workshop_form = WorkshopForm(instance=self.get_workshop(), data=request.POST)
            workshop = self.get_workshop()

            paper_instances = list(workshop.accepted_papers.all())
            uploaded_files = request.FILES.getlist('uploaded_file')  
            agreement_files = request.FILES.getlist('agreement_file')
            if workshop_form.is_valid():
                workshop_form.save()

            for i, paper_instance in enumerate(paper_instances):
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
    
    def get_context(self, author_formset, paper_form, condition='default'):
        if condition == 'author':
            return {'author_formset': author_formset, 'paper_form': paper_form}
        elif condition == "confirm":
            return {'workshop': self.get_workshop(), 'paper': paper_form, 'authors': author_formset}
        return {'workshop': self.get_workshop(), 'author_formset': author_formset, 'paper_form': paper_form}
    
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

    
    def construct_file_path(self, paper_instance, filename):
        """
        Constructs the file path for a Paper instance manually based on the workshop volume.
        This does not access the file system but constructs the path string as expected.
        """
        workshop_volume = paper_instance.workshop.id
        path = f'agreement/Vol-{workshop_volume}/{filename}'
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        return full_path
    def _create_or_update_paper_instance(self, request, paper_form):
        if not paper_form.is_valid():
                messages.error(request, 'OOOOOOOOOPS')
        
        workshop_instance = self.get_workshop()
        paper_title = paper_form.cleaned_data['paper_title']

        # Try to find an existing paper with the same title in the same workshop
        existing_paper = Paper.objects.filter(paper_title=paper_title, workshop=workshop_instance).first()

        if existing_paper:
            paper_instance = existing_paper
            
            existing_paper.paper_title = request.POST['paper_title']
            existing_paper.pages = request.POST['pages']
            
            if 'uploaded_file' in request.FILES:
                existing_paper.uploaded_file = request.FILES['uploaded_file']
            if 'agreement_file' in request.FILES:
                existing_paper.agreement_file = request.FILES['agreement_file']

            existing_paper.save()

            heloo = os.path.join(settings.MEDIA_ROOT, paper_instance.agreement_file.name)

            is_signed = self._detect_signature_in_image(heloo)

            if not is_signed:
                # Handle unsigned agreement file, e.g., by setting an error message
                print('Agreement file is not signed')
            else:
                print('Agreement file is signed')

            print(existing_paper.uploaded_file.url)
        else:
            paper_instance = paper_form.save(commit=False)
            paper_instance.workshop = workshop_instance
            if 'uploaded_file' not in request.FILES and 'agrement_file' not in request.FILES and ('uploaded_file_url' in request.session and 'agreement_file_url' in request.session):
                paper_instance.uploaded_file.name = request.session['uploaded_file_url']
                paper_instance.agreement_file.name = request.session['agreement_file_url']

            # elif 'agreement_file' in request.FILES:
            #     agreement_file_path = request.FILES['agreement_file_url'].temporary_file_path()
            #     is_signed = self._check_agreement_signature(agreement_file_path)
            #     if not is_signed:
            #         # Handle unsigned agreement file, e.g., by setting an error message
            #         print('Agreement file is not signed')
            #         exit()
            paper_instance.save()

        return paper_instance
    
    def submit_author(self, request, author_formset, paper_form):
        paper_instance = self._create_or_update_paper_instance(request, paper_form)
        
        if not paper_instance.authors.exists():  # Check if authors are already associated
            author_instances = author_formset.save()
            paper_instance.authors.add(*author_instances)
            self.get_workshop().accepted_papers.add(paper_instance)

        context = self.get_context(author_instances, paper_instance, 'confirm')
        return render(request, self.success_path, context)
    def edit_author(self, request, author_formset, paper_form):
        paper_instance = self._create_or_update_paper_instance(request, paper_form)

        context = self.get_context(author_formset, paper_form, 'author')
        return render(request, self.edit_path, context)
        
    def get(self, request, secret_token):
        author_formset = AuthorFormSet(queryset=Author.objects.none())
        paper_form = PaperForm(file_uploaded=False)
        context = self.get_context(author_formset, paper_form)
        return render(request, self.upload_path, context)

    def post(self, request, secret_token):
        author_formset = AuthorFormSet(request.POST)
        paper_form = PaperForm(request.POST, request.FILES, file_uploaded=True)
        if 'confirm_button' in request.POST:
            return self.submit_author(request, author_formset, paper_form)
        else:
            return self.edit_author(request, author_formset, paper_form)
        
    