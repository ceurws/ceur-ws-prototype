from django.shortcuts import render, get_object_or_404
from ..models import Workshop, Paper, Author
from ..forms import get_author_formset, PaperForm
import PyPDF2, os


def _get_agreement_filename(paper_instance, original_filename):
        paper_title = paper_instance.paper_title.replace(' ', '')
        extension = os.path.splitext(original_filename)[1]
        new_filename = f'AUTHOR-AGREEMENT-{paper_title}{extension}'
        return new_filename

def edit_author_post_view(request, paper_id, author_upload_secret_token):
    workshop = get_object_or_404(Workshop, author_upload_secret_token=author_upload_secret_token)
    paper = get_object_or_404(Paper, secret_token=paper_id)

    context = {
        'workshop' : workshop,
        'paper_form' : None,
        'paper' : paper, 
        'author_formset' : None,
        'edit_mode': False
    }
    if request.method == "POST":
        paper_form = PaperForm(data=request.POST, instance=paper, workshop=workshop)

        author_formset = get_author_formset()(data = request.POST, queryset=Author.objects.filter(paper = paper), prefix = 'author')

        
        if 'edit_button' in request.POST:
            paper_form = PaperForm(instance=paper, workshop=workshop)
            author_formset = get_author_formset()(queryset=Author.objects.filter(paper = paper), prefix = 'author')
            context.update({'paper_form': paper_form, 'author_formset': author_formset, 'edit_mode': True})

        elif 'submit_button' in request.POST and paper_form.is_valid() and author_formset.is_valid():

            paper_instance = paper_form.save(commit = False)

            if request.FILES.get('uploaded_file', False):
                paper_instance.uploaded_file = request.FILES['uploaded_file']
                pdfReader = PyPDF2.PdfReader(paper_instance.uploaded_file)
                paper_instance.pages = len(pdfReader.pages)
            if request.FILES.get('agreement_file', False):
                paper_instance.agreement_file = request.FILES['agreement_file']
                paper_instance.agreement_file.name = _get_agreement_filename(paper_instance, paper_instance.agreement_file.name)

            paper_instance.save()

            paper.authors.add(*author_formset.save())
            
            authors_to_delete = request.POST.getlist('authors_to_delete')

            for author_id in authors_to_delete:
                author = get_object_or_404(Author, id=author_id)
                paper.authors.remove(author)
                author.delete()
            context.update({'paper_form': paper_form, 'paper': paper, 'edit_mode': False})
    else:
        paper_form = PaperForm(instance=paper)
        author_formset = get_author_formset()(queryset=paper.authors.all())

    
    return render(request, 'workshops/author_upload_success.html', context)