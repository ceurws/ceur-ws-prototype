from django.shortcuts import render, redirect
from .models import Workshop, Paper, Editor, Author
import uuid
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

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
    if request.method == "POST":
        # Temporarily store the data in the session instead of saving to the database
        request.session['workshop_data'] = request.POST.dict()
        return redirect('workshops:edit_workshop')

    return render(request, "workshops/create_workshop.html")

def edit_workshop(request, workshop_id=None):
    # Check if there's a new workshop to confirm
    if 'workshop_data' in request.session:
        workshop_data = request.session.get('workshop_data')
        
        if request.method == "POST":
            clean_data = {key: value for key, value in workshop_data.items() if key not in ['csrfmiddlewaretoken']}
            workshop = Workshop.objects.create(**clean_data)
            workshop = get_object_or_404(Workshop, id=workshop.id)
            request.session.pop('workshop_data', None)  # Clear the session data

            # Generate the URLs for the organizer and the author
            organizer_url = reverse('workshops:workshop_overview', args=[workshop.id])
            author_url = "/workshops/author_upload/{}".format(workshop.id)

            return render(request, "workshops/workshop_edit_success.html", {
                'organizer_url': organizer_url,
                'author_url': author_url
            })
        
        else:
            return render(request, "workshops/edit_workshop.html", {'workshop': workshop_data})
    
    else:
        # Handle the case for editing existing workshops
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
            return redirect(reverse('workshops:workshop_overview', args=[workshop.id]))
        return render(request, "workshops/edit_workshop.html", {'workshop': workshop})

def workshop_overview(request, workshop_id):
    workshop = get_object_or_404(Workshop, id=workshop_id)
    return render(request, 'workshops/workshop_overview.html', {'workshop': workshop})   
