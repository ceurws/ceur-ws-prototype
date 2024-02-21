from django.shortcuts import render, redirect
from .models import Workshop, Paper, Editor, Author
import uuid
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings

def index(request):
    """
    Renders the home page of the workshop site.
    """
    return render(request, 'workshops/index.html')
    
# def metadata_added_success(request, paper_id):
#     """
#     Displays a success message after metadata has been successfully added.
#     """
#     paper = get_object_or_404(Paper, id = paper_id)
#     editors = paper.workshop.editors.all()  

#     return render(request, 'workshops/author_upload_success.html', {
#         'paper': paper,
#         'editors': editors,
#         'workshop_id': paper.workshop.id
#     })
def metadata_added_success(request):
    # Fetch data from session
    author_data = request.session.get('author_data')
    if not author_data:
        # If session data is missing, redirect to author upload page
        return redirect('workshops:author_upload')

    # Extract workshop ID from the session and fetch workshop and editors
    workshop_id = author_data.get('workshop_id')
    workshop = get_object_or_404(Workshop, id=workshop_id)
    editors = workshop.editors.all()

    # Pass the session data to the template
    return render(request, 'workshops/author_upload_success.html', {
        'author_data': author_data,
        'workshop': workshop,
        'editors': editors,
    })

def create_workshop(request):
    if request.method == "POST":
        # Temporarily store the data in the session instead of saving to the database
        request.session['workshop_data'] = request.POST.dict()
        return redirect('workshops:edit_workshop')

    return render(request, "workshops/create_workshop.html")

def edit_workshop(request, workshop_id=None):
    workshop = None
    editors = []

    if 'workshop_data' in request.session:
        workshop_data = request.session.get('workshop_data')
        
        if request.method == "POST":
            # Pop and clean data from session, then create the workshop
            clean_data = {key: value for key, value in workshop_data.items() if key not in ['csrfmiddlewaretoken', 'editor_1', 'editor_2', 'editor_3']}
            workshop = Workshop.objects.create(**clean_data, secret_token=uuid.uuid4())
            
            # Handle editors creation and association with the workshop
            for editor_key in ['editor_1', 'editor_2', 'editor_3']:
                editor_name = workshop_data.get(editor_key)
                if editor_name:
                    editor, created = Editor.objects.get_or_create(name=editor_name)
                    workshop.editors.add(editor)
            return HttpResponseRedirect(reverse('workshops:workshop_edit_success', args=[workshop.id]))

        # Preparing for the confirmation page but not saving anything yet
        editors = [Editor(name=workshop_data.get(key)) for key in ['editor_1', 'editor_2', 'editor_3'] if key in workshop_data]
        
    elif workshop_id:
        workshop = get_object_or_404(Workshop, id=workshop_id)
        editors = workshop.editors.all()
        context = {
            'workshop': workshop,
            'confirming': False,
            'editors': editors
        }

    if request.method == "POST" and workshop:
        # Handle potential post-save logic here if needed
        pass

    return render(request, "workshops/edit_workshop.html", {
        'workshop': workshop_data,
        'confirming': 'workshop_data' in request.session,
        'editors': editors,
    })
def workshop_edit_success(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    editors = workshop.editors.all()
    organizer_url = reverse('workshops:workshop_overview', args=[workshop.id])
    author_url = reverse('workshops:author_upload', args=[workshop.id])
    return render(request, "workshops/workshop_edit_success.html", {
        'organizer_url': organizer_url,
        'author_url': author_url
    })

def workshop_overview(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    return render(request, 'workshops/workshop_overview.html', {'workshop': workshop})   

def author_upload(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    
    if request.method == "POST":
        # Handle the uploaded file
        uploaded_file = request.FILES['uploaded_file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        uploaded_file_url = fs.url(filename)

        # Store the form data and the path to the uploaded file in the session
        request.session['author_data'] = {
            'author_name': request.POST.get("author_name"),
            'paper_title': request.POST.get("paper_title"),
            'pages': request.POST.get("pages"),
            'uploaded_file_url': uploaded_file_url,
            'workshop_id': workshop_id,
        }
        return redirect('workshops:metadata_added_success')

    return render(request, "workshops/author_upload.html", {
        'workshop': workshop,
    })

def confirm_and_save_author_data(request):
    author_data = request.session.pop('author_data', None)

    if author_data:
        workshop = get_object_or_404(Workshop, id=author_data['workshop_id'])
        author= Author.objects.create(author_name=author_data['author_name'])
        
        # Assuming Paper model has a 'file' or similar field for the uploaded file
        paper = Paper.objects.create(
            paper_title=author_data['paper_title'],
            author=author,
            pages=author_data['pages'],
            uploaded_file=author_data['uploaded_file_url'],
            workshop=workshop
        )

        # Redirect to a page showing the paper details or a success message
        return redirect('workshops:author_overview', paper_id=paper.id)
    else:
        # Handle case where session data is missing, e.g., redirect to upload form
        return redirect('some_error_handling_view')

def author_overview(request, paper_id):
    # Fetch the paper based on `paper_id`
    paper = get_object_or_404(Paper, id=paper_id)
    
    editors = paper.workshop.editors.all() if paper.workshop else []

    return render(request, 'workshops/author_overview.html', {
        'paper': paper,
        'editors': editors
    })


    
