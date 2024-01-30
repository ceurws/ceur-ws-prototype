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

def editor_added_success(request):
    """
    Displays a success message after an editor has been successfully added.
    """
    return render(request, 'workshops/editor_added_success.html')

def add_editor(request):
    """
    Handles the submission of the 'Add Editor' form. On POST, it saves the new editor to the database.
    If the request is GET, it renders the form for adding a new editor.
    """
    if request.method == "POST":
        editor_name = request.POST.get("editor_name")
        editor = Editor(volume_editor=editor_name)
        editor.save()
        return redirect('workshops:editor_added_success')
    else:
        return render(request, "workshops/editor_form.html")

def paper_added_success(request):
    """
    Displays a success message after a paper has been successfully added.
    """
    return render(request, 'workshops/paper_added_success.html')

def add_paper(request):
    """
    Handles the submission of the 'Add Paper' form. On POST, it saves the new paper to the database.
    If the request is GET, it renders the form for adding a new paper, along with the list of available workshops and authors.
    """
    if request.method == "POST":
        paper_title = request.POST.get("paper_title")
        workshop_id = request.POST.get("workshop")
        author_id = request.POST.get("author")
        pages = request.POST.get("pages")

        workshop = Workshop.objects.get(id=workshop_id)
        author = Author.objects.get(id=author_id)

        paper = Paper(paper_title=paper_title, workshop=workshop, author=author, pages=pages)
        paper.save()

        return redirect('workshops:paper_added_success')  # Redirect to a success page

    else:
        workshops = Workshop.objects.all()
        authors = Author.objects.all()
        return render(request, "workshops/paper_form.html", {'workshops': workshops, 'authors': authors})

def author_added_success(request):
    """
    Displays a success message after an author has been successfully added.
    """
    return render(request, 'workshops/author_added_success.html')

def add_author(request):
    """
    Handles the submission of the 'Add Author' form. On POST, it saves the new author to the database.
    If the request is GET, it renders the form for adding a new author.
    """
    if request.method == "POST":
        author_name = request.POST.get("author_name")
        if author_name:  # Check if author_name is not empty
            author = Author(author_name=author_name)
            author.save()
            return redirect('workshops:author_added_success')

    return render(request, "workshops/author_form.html")


def workshop_created_success(request):
    """
    Displays a success message after a workshop has been successfully created.
    """
    return render(request, "workshops/workshop_created_success.html")

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
        # Fetch other fields similarly

        # Handle the editor. Here, we allow null for simplicity.
        editor = Editor.objects.first()  # Or handle editor selection differently

        # Create Workshop instance with a generated secret token
        new_workshop = Workshop(
            workshop_title=workshop_title,
            volume_number=volume_number,
            urn=urn,
            publication_year=publication_year,
            license=license,
            location_time=location_time,
            editors=editor,
            secret_token=uuid.uuid4(),
            # Set other fields as necessary
        )
        new_workshop.save()

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
        organizer_url = "workshops:workshop_overview/{}".format(workshop.id)
        author_url = "workshops:author_upload/{}".format(workshop.id)

        # Redirect to a confirmation page or pass the URLs to the template
        return render(request, "workshops/workshop_edit_success.html", {'organizer_url': organizer_url, 'author_url': author_url})
    
    return render(request, "workshops/edit_workshop.html", {'workshop': workshop})


