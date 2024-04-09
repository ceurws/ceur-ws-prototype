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

        # workshops = Workshop.objects.prefetch_related('editors').all()

        # editors = Editor.objects.all()
        # context = {
        #     'workshops': workshops,
        #     'editors': editors,
        # }
        return render(request, 'workshops/submit_workshop.html')
    
    def post(self, request, secret_token):

        # renders the workshop overview page in edit mode, allowing to edit all fields
        if request.POST["submit_button"] == "Edit":
            return self.render_workshop(request, edit_mode = True)

            # title_list = request.POST.getlist('paper_title')
            # page_list = request.POST.getlist('pages')

        # saves the changes when user is in edit mode and takes user out of edit mode.
        elif request.POST["submit_button"] == "Confirm":
        #     workshop_form = WorkshopForm(instance = self.get_workshop(), data = request.POST)

        #     for i, paper_instance in enumerate(self.get_workshop().accepted_papers.all()):

        #         paper_data = {
        #         'paper_title': request.POST.getlist('paper_title', '')[i],
        #         'pages': request.POST.getlist('pages', '')[i],
        #         'uploaded_file': request.FILES  # this line puts the uploaded file in every paper form, so it's obviously wrong but I don't know how to fix it
        #         }

        #         paper_form = PaperForm(paper_data, request.FILES, instance=paper_instance,)

        #         if paper_form.is_valid():
        #             paper_form.save()

        #     if workshop_form.is_valid():
        #         workshop_form.save()
        #         return self.render_workshop(request, edit_mode = False)

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
                    paper_form = PaperForm(paper_form_data, {'uploaded_file': uploaded_files[i]}, instance=paper_instance)
                else:
                    paper_form = PaperForm(paper_form_data, instance=paper_instance)

                if i < len(agreement_files):
                    paper_form = PaperForm(paper_form_data, {'agreement_file': agreement_files[i]}, instance=paper_instance)
                else:
                    paper_form = PaperForm(paper_form_data, instance=paper_instance)

                if paper_form.is_valid():
                    paper_form.save()

            return self.render_workshop(request, edit_mode=False)
        
        elif request.POST["submit_button"] == "Submit Workshop":
            return self.submit_workshop(request, secret_token)
            
class AuthorUpload(View):
    def get_workshop(self):
        workshop = get_object_or_404(Workshop, secret_token=self.kwargs['secret_token'])
        return workshop

    def get(self, request, secret_token):
        author_formset = AuthorFormSet(queryset=Author.objects.none())
        paper_form = PaperForm(file_uploaded=False)

        return render(request, "workshops/author_upload.html", {
            'workshop': self.get_workshop(), 'author_formset': author_formset, 'paper_form': paper_form
        })

    def post(self, request, secret_token):
        
        if 'confirm_button' in request.POST:
            author_formset = AuthorFormSet(request.POST)
            paper_form = PaperForm(request.POST, request.FILES, file_uploaded=True)
            
            if paper_form.is_valid() and author_formset.is_valid():

                paper_instance = paper_form.save(commit=False)

                workshop_instance = self.get_workshop()
                paper_instance.workshop = workshop_instance
                if ('uploaded_file' and 'agreement_file') not in request.FILES and ('uploaded_file_url' and 'agreement_file_url') in request.session:
                    paper_instance.uploaded_file.name = request.session['uploaded_file_url']
                    paper_instance.agreement_file.name = request.session['agreement_file_url']
                paper_instance.save()
                author_instances = author_formset.save()
                paper_instance.authors.add(*author_instances)

                self.get_workshop().accepted_papers.add(paper_instance)
                return render(request, 'workshops/author_upload_success.html', {
                    'workshop': self.get_workshop(), 
                    'paper': paper_instance, 
                    'authors': author_instances})
            

        else:
            author_formset = AuthorFormSet(request.POST)
            paper_form = PaperForm(request.POST, request.FILES, file_uploaded=True)
            if paper_form.is_valid() and author_formset.is_valid():

                
                if 'uploaded_file' in request.FILES:
                    paper_instance = paper_form.save(commit=False)
                    paper_instance.workshop = self.get_workshop()
                    paper_instance.save()
                    request.session['uploaded_file_url'] = paper_instance.uploaded_file.name
                    request.session['agreement_file_url']  = paper_instance.agreement_file.name
                return render(request, 'workshops/edit_author.html', {
                    'paper_form': paper_form, 
                    'author_formset': author_formset}) 
