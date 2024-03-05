from django.shortcuts import render, redirect
from .models import Workshop, Paper, Editor, Author
import uuid
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import MultipleObjectsReturned

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

def create_workshop(request):
    # handles the second post of form data and saves the data to the database
    if request.method == "POST" and 'submit_button' in request.POST: 
        formset = EditorFormSet(request.POST)
        form = WorkshopForm(request.POST)

        if form.is_valid() and formset.is_valid():
            workshop = form.save()  # Save the workshop object and get the instance with an ID
            instances = formset.save()

            workshop.editors.add(*instances)

            return HttpResponseRedirect(reverse('workshops:workshop_edit_success', args=[workshop.id]))


    # handles first post of form data
    elif request.method == "POST":
        # Create a bound form
        form = WorkshopForm(request.POST)
        editor_form = EditorFormSet(queryset=Editor.objects.none(),data = request.POST)
        print('editor form', editor_form.total_form_count())

        if form.is_valid():
            return render(request, 'workshops/edit_workshop.html', {'form': form, 'editor_form':editor_form})

    else:
        form = WorkshopForm()
        editor_form = EditorFormSet(queryset=Editor.objects.none())
        print('editor form at GET', editor_form.total_form_count())

        return render(request, "workshops/create_workshop.html", {'form': form, 'editor_form':editor_form})

def workshop_edit_success(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    organizer_url = reverse('workshops:workshop_overview', args=[workshop.secret_token])
    author_url = reverse('workshops:author_upload', args=[workshop.secret_token])

    return render(request, "workshops/workshop_edit_success.html", {
        'organizer_url': organizer_url,
        'author_url': author_url
    })

def workshop_overview(request, secret_token):    
    workshop = get_object_or_404(Workshop, secret_token=secret_token)

    # check this if papers are not being added
    papers = [paper for paper in workshop.accepted_papers.all()]
    context = {
        'papers' : papers,
        'workshop' : workshop
    }

    return render(request, 'workshops/workshop_overview.html', context)

def author_upload(request, secret_token):
    workshop = get_object_or_404(Workshop, secret_token=secret_token)
    
    if request.method == "POST" and 'confirm_button' in request.POST:
        author_formset = AuthorFormSet(request.POST)
        paper_form = PaperForm(request.POST, request.FILES)  

        # save files and add authors to model
        if paper_form.is_valid() and author_formset.is_valid():

            paper_instance = paper_form.save()  
            author_instances = author_formset.save()
            paper_instance.authors.add(*author_instances)
            workshop.accepted_papers.add(paper_instance)

            return render(request, 'workshops/author_upload_success.html', {'workshop':workshop, 'paper': paper_instance, 'authors': author_instances})

    elif request.method == "POST":
        author_formset = AuthorFormSet(request.POST)
        paper_form = PaperForm(request.POST, request.FILES)  

        if paper_form.is_valid() and author_formset.is_valid():
            return render(request, 'workshops/edit_author.html', {'paper_form': paper_form, 'author_formset': author_formset})

    else:
        author_formset = AuthorFormSet()
        paper_form = PaperForm()

        return render(request, "workshops/author_upload.html", {
            'workshop': workshop, 'author_formset': author_formset, 'paper_form': paper_form
        })


def author_overview(request, secret_token):
    # Fetch the paper based on `paper_id`
    paper = get_object_or_404(Paper, secret_token=secret_token)
    # Assuming Paper model has a relation to Workshop and Author
    editors = paper.workshop.editors.all() if paper.workshop else []

    return render(request, 'workshops/author_overview.html', {
        'paper': paper,
        'editors': editors
    })
    
