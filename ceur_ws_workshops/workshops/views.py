from typing import Any
from django.shortcuts import render, redirect
from .models import Workshop, Paper, Editor, Author
import uuid
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import MultipleObjectsReturned
from django.views import View

from .forms import WorkshopForm, EditorFormSet, AuthorFormSet, PaperForm

def index(request):
    """
    Renders the home page of the workshop site.
    """
    return render(request, 'workshops/index.html')
    
def author_upload_check(request, secret_token):
    """
    Displays a success message after metadata has been successfully added.
    """
    paper = get_object_or_404(Paper, secret_token=secret_token)
    editors = paper.workshop.editors.all()  

    return render(request, 'workshops/author_upload_success.html', {
        'paper': paper,
        'editors': editors,
        'workshop_id': paper.workshop.id
    })

class CreateWorkshop(View):
    
    def get(self, request):
        form = WorkshopForm()
        editor_form = EditorFormSet(queryset=Editor.objects.none())
        return render(request, "workshops/create_workshop.html", {'form':form, 'editor_form':editor_form})

    def post(self,request):
        if 'submit_button' in request.POST:
            formset = EditorFormSet(request.POST)
            form = WorkshopForm(request.POST)

            if form.is_valid() and formset.is_valid():
                workshop = form.save()  
                instances = formset.save()
                workshop.editors.add(*instances)
                return HttpResponseRedirect(reverse('workshops:workshop_edit_success', args=[workshop.id]))

        else:
            # Create a bound form
            form = WorkshopForm(request.POST)
            editor_form = EditorFormSet(queryset=Editor.objects.none(),data = request.POST)

            if form.is_valid():
                return render(request, 'workshops/edit_workshop.html', {'form': form, 'editor_form':editor_form})
            

def workshop_edit_success(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    organizer_url = reverse('workshops:workshop_overview', args=[workshop.secret_token])
    author_url = reverse('workshops:author_upload', args=[workshop.secret_token])

    return render(request, "workshops/workshop_edit_success.html", {
        'organizer_url': organizer_url,
        'author_url': author_url
    })

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

    def post(self, request, secret_token):
        if request.POST["submit_button"] == "Edit":
            return self.render_workshop(request, edit_mode = True)

        elif request.POST["submit_button"] == "Confirm":
            workshop_form = WorkshopForm(instance = self.get_workshop(), data = request.POST)
            updated_papers = [PaperForm(instance=paper_instance, data = request.POST) for paper_instance in self.get_workshop().accepted_papers.all()]
        
            if workshop_form.is_valid():
                workshop_form.save()
                [paperform.save() for paperform in updated_papers]
                return self.render_workshop(request, edit_mode = False)
    
        elif request.POST["submit_button"] == "Submit Workshop":
            return redirect(reverse('submit_workshop', kwargs={'secret_token': secret_token}))


class author_upload_class(View):
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
                if 'uploaded_file' not in request.FILES and 'uploaded_file_url' in request.session:
                    paper_instance.uploaded_file.name = request.session['uploaded_file_url']
                
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
                    paper_instance.save()  
                    request.session['uploaded_file_url'] = paper_instance.uploaded_file.name

                return render(request, 'workshops/edit_author.html', {
                    'paper_form': paper_form, 
                    'author_formset': author_formset}) 
            
def submit_workshop(request, secret_token):
    return render(request, 'workshops/submit_workshop.html')

    
