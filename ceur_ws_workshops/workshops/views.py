from django.shortcuts import render, redirect
from .models import Workshop, Paper, Editor, Author
import uuid
from django.shortcuts import get_object_or_404
from django.urls import reverse

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
    """
    Handles the submission of the 'Create Workshop' form. On POST, it saves the new workshop to the database.
    If the request is GET, it renders the form for creating a new workshop.
    """
    if request.method == "POST":
        workshop_title = request.POST.get("workshop_title")
        volume_number = request.POST.get("volume_number")
        urn = request.POST.get("urn")
        publication_year = request.POST.get("publication_year")
        license = request.POST.get("license")
        location_time = request.POST.get("location_time")
        
        # Fetch editors (change later to something more pretty)
        editor_1 = request.POST.get("editor_1")
        editor_2 = request.POST.get("editor_2")
        editor_3 = request.POST.get("editor_3")

        # Create new Editors for each editor name
        editor_1 = Editor.objects.create(name=editor_1)
        editor_2 = Editor.objects.create(name=editor_2)
        editor_3 = Editor.objects.create(name=editor_3)

        # Create Workshop instance with a generated secret token
        new_workshop = Workshop(
            workshop_title=workshop_title,
            volume_number=volume_number,
            urn=urn,
            publication_year=publication_year,
            license=license,
            location_time=location_time,
            secret_token=uuid.uuid4(),
            # Set other fields as necessary
        )
        new_workshop.save()
        
        new_workshop.editors.add(editor_1, editor_2, editor_3)

        return redirect(reverse('workshops:edit_workshop', args=(new_workshop.id,)))

    return render(request, "workshops/create_workshop.html")


def edit_workshop(request, workshop_id):
    """
    Handles the editing of an existing workshop. On POST, it updates the workshop details in the database.
    If the request is GET, it renders the form pre-filled with the existing workshop details for editing.
    """
    workshop = get_object_or_404(Workshop, id=workshop_id)

    if request.method == "POST":
        workshop.workshop_title = request.POST.get("workshop_title")
        workshop.volume_number = request.POST.get("volume_number")
        workshop.urn = request.POST.get("urn")
        workshop.publication_year = request.POST.get("publication_year")
        workshop.license = request.POST.get("license")
        workshop.location_time = request.POST.get("location_time")
        # Update other fields as necessary

        workshop.save()

        organizer_url = reverse('workshops:workshop_overview', args=[workshop.id])
        author_url = reverse('workshops:author_upload', args=[workshop.id])

        # Redirect to a confirmation page or pass the URLs to the template
        return render(request, "workshops/workshop_edit_success.html", {'organizer_url': organizer_url, 'author_url': author_url})
    
    return render(request, "workshops/edit_workshop.html", {'workshop': workshop})


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
