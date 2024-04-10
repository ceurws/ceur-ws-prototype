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
from signature_detect import is_signed
import tempfile 

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
        context = {
                'workshop': self.get_workshop(), 
                'author_formset': author_formset, 
                'paper_form': paper_form
                }
        return render(request, "workshops/author_upload.html", context)
    
    def get_context(self, paper_instance, author_instances, success = True):
        
        if success:
            return {
                'workshop': self.get_workshop(),
                'paper': paper_instance,
                'authors': author_instances
            }
        return {'paper_form': paper_instance, 
                    'author_formset': author_instances
        }

    def post(self, request, secret_token):
        # Initialize forms
        author_formset = AuthorFormSet(request.POST)
        paper_form = PaperForm(request.POST, request.FILES, file_uploaded=True)
        
        # Check form validity
        if paper_form.is_valid() and author_formset.is_valid():
            if 'confirm_button' in request.POST:
                return self.handle_confirmation(request, author_formset, paper_form)
            else:
                return self.handle_editing(request, author_formset, paper_form)
        else:
            # Handle the case where forms are not valid, maybe render a form error page
            pass
        
    def handle_confirmation(self, request, author_formset, paper_form):
        paper_instance = self.prepare_paper_instance(request, paper_form)
        author_instances = author_formset.save()
        paper_instance.authors.add(*author_instances)
        self.get_workshop().accepted_papers.add(paper_instance)

        # Render success template
        context = self.get_context(paper_instance, author_instances, success = True)
        return render(request, 'workshops/author_upload_success.html', context)

    def handle_editing(self, request, author_formset, paper_form):
        if 'uploaded_file' and 'agreement_file' in request.FILES:
            self.prepare_paper_instance(request, paper_form, save_to_session=True)

        context = self.get_context(paper_form, author_formset, success = False)
        return render(request, 'workshops/edit_author.html', context)
    
    
    def prepare_paper_instance(self, request, paper_form, save_to_session=False):
        paper_instance = paper_form.save(commit=False)
        paper_instance.workshop = self.get_workshop()
        
        # Checking for hand-signed agreement if the file is in the request
        if 'agreement_file' in request.FILES:
            agreement_file = request.FILES['agreement_file']
            is_hand_signed = self.check_hand_signed(agreement_file)
            if not is_hand_signed:
                # Handle the case where the agreement is not hand-signed
                # This could involve setting an error and re-rendering the form with a message,
                # or any other logic you see fit
                pass
            else:
                # Save the paper instance and update the session if required
                if save_to_session:
                    paper_instance.save()
                    request.session['uploaded_file_url'] = paper_instance.uploaded_file.name
                    request.session['agreement_file_url'] = paper_instance.agreement_file.name
                paper_instance.save()
                return paper_instance

    def check_hand_signed(self, agreement_file):
        # Convert the InMemoryUploadedFile to a format that can be analyzed by the library
        # Temporarily save the file to disk if necessary
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in agreement_file.chunks():
                tmp.write(chunk)
            tmp.seek(0)
            # Use the is_signed function to check for a signature
            result = is_signed(tmp.name)
        os.unlink(tmp.name)  # Clean up the temporary file
        return result
    
    

    

    