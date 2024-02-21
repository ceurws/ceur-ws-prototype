from django.shortcuts import render, redirect
from .models import Workshop, Paper, Editor, Author
import uuid
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import MultipleObjectsReturned

from .forms import CreateWorkshopForm

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
    if request.method == "POST":
        # Temporarily store the data in the session instead of saving to the database
        request.session['workshop_data'] = request.POST.dict()
        return redirect('workshops:edit_workshop')

    return render(request, "workshops/create_workshop.html")

def edit_workshop(request, workshop_id=None):
    if 'workshop_data' in request.session:
        if request.method == "POST":
            workshop_data = request.session.pop('workshop_data')

            # extract editors and create editor objects
            editors = [workshop_data[key] for key in workshop_data if key.startswith('editor')]
            editor_objects = [Editor.objects.create(name=editor_name)for editor_name in editors]

            # create workshop instance by extracting unnecessary data
            clean_data = {key: value for key, value in workshop_data.items() if key not in ['csrfmiddlewaretoken','editor_1','editor_2','editor_3','editor_4','editor_5']}
            workshop = Workshop.objects.create(**clean_data, secret_token=uuid.uuid4())

            # add all editor objects to the workshop
            workshop.editors.add(*editor_objects)

            return HttpResponseRedirect(reverse('workshops:workshop_edit_success', args=[workshop.id]))
    
        else:
            # Render form for final confirmation using session data
            workshop_data = request.session.get('workshop_data')
            editor_names = [workshop_data[key] for key in workshop_data if key.startswith('editor')]
            editors = [Editor(name=name) for name in editor_names]
            return render(request, "workshops/edit_workshop.html", {
                'workshop': workshop_data,
                'confirming': True,
                'editors': editors
            })
    else:
        workshop = None  
        if workshop_id:
            workshop = get_object_or_404(Workshop, id=workshop_id)
        editors = workshop.editors.all() if workshop else []  
        
        if request.method == "POST" and workshop:  
            workshop.save()
            return HttpResponseRedirect(reverse('workshops:workshop_edit_success', args=[workshop.id]))
        
        # The confirming context variable needs careful handling; it should be true if in session-related logic
        confirming = 'workshop_data' in request.session
        return render(request, "workshops/edit_workshop.html", {
            'workshop': workshop,
            'confirming': confirming,
            'editors': editors
        })

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

    context = {
        'papers' : [paper for paper in Paper.objects.filter(workshop=workshop)],
        'workshop' : workshop
    }

    return render(request, 'workshops/workshop_overview.html', context)

def author_upload(request, secret_token):
    workshop = get_object_or_404(Workshop, secret_token=secret_token)
    if request.method == "POST":
        
        author_names = request.POST.getlist("author_name")
        paper_title = request.POST.get("paper_title")
        pages = request.POST.get("pages")
        uploaded_file = request.FILES.get("uploaded_file")

        if author_names:

            authors = [Author.objects.create(author_name=author_name)for author_name in author_names]

            # Create the paper with the provided metadata and file
            paper = Paper.objects.create(
                paper_title=paper_title,
                workshop=workshop,  
                pages=pages,
                uploaded_file=uploaded_file
            )

            paper.authors.add(*authors)

            return redirect('workshops:author_upload_check', secret_token = paper.secret_token)
    

    return render(request, "workshops/author_upload.html", {
        'workshop': workshop,
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


    
