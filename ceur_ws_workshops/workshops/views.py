from django.shortcuts import render, redirect
from .models import Workshop, Paper, Editor, Author
import uuid
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.exceptions import MultipleObjectsReturned

def index(request):
    """
    Renders the home page of the workshop site.
    """
    return render(request, 'workshops/index.html')
    
def metadata_added_success(request):
    """
    Displays a success message after metadata has been successfully added.
    """
    return render(request, 'workshops/author_upload_success.html')

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
            clean_data = {key: value for key, value in workshop_data.items() if key not in ['csrfmiddlewaretoken', 'editor_1', 'editor_2', 'editor_3']}

            # Create the workshop instance
            workshop = Workshop.objects.create(**clean_data, secret_token=uuid.uuid4())

            for editor_key in ['editor_1', 'editor_2', 'editor_3']:
                editor_name = workshop_data.get(editor_key)
                if editor_name:
                    try:
                        editor, created = Editor.objects.get_or_create(name=editor_name)
                        workshop.editors.add(editor)
                    except MultipleObjectsReturned:
                        editor = Editor.objects.filter(name=editor_name).first()
                        workshop.editors.add(editor)

            return HttpResponseRedirect(reverse('workshops:workshop_edit_success', args=[workshop.id]))
    
        else:
            # Render form for final confirmation using session data
            workshop_data = request.session.get('workshop_data')
            editors = [Editor(name=workshop_data.get(key)) for key in ['editor_1', 'editor_2', 'editor_3'] if workshop_data.get(key)]
            return render(request, "workshops/edit_workshop.html", {
                'workshop': workshop_data,
                'confirming': True,
                'editors': editors
            })
    else:
        workshop = get_object_or_404(Workshop, id=workshop_id) if workshop_id else None
        editors = workshop.editors.all()
        if request.method == "POST":
            workshop.save()
            return HttpResponseRedirect(reverse('workshops:workshop_edit_success', args=[workshop.id]))
        return render(request, "workshops/edit_workshop.html", {'workshop': workshop, 'confirming': False})

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
        author_name = request.POST.get("author_name")
        paper_title = request.POST.get("paper_title")
        pages = request.POST.get("pages")
        uploaded_file = request.FILES.get("uploaded_file")

        if author_name:
            author = Author.objects.create(author_name=author_name)

            # Create the paper with the provided metadata and file
            paper = Paper.objects.create(
                paper_title=paper_title,
                workshop=workshop,
                author=author,
                pages=pages,
                uploaded_file=uploaded_file
            )

            return redirect('workshops:metadata_added_success')

    return render(request, "workshops/author_upload.html", {'workshop': workshop})
