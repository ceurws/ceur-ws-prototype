from django.shortcuts import render, get_object_or_404, redirect
from ..models import Workshop, Paper, Editor, Author, Session
from django.urls import reverse
from django.views import View

from ..forms import WorkshopForm, EditorFormSet, PaperForm, SessionFormSet, get_author_formset
from urllib.parse import urlparse, parse_qs
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from PyPDF2 import PdfReader
from django.forms import formset_factory



class CreateWorkshop(View):
    success_path = "workshops/workshop_edit_success.html"
    overview_path = "workshops/workshop_overview.html"
    edit_path = "workshops/edit_workshop.html"

    openreview_url = None
    
    def get_workshop(self, workshop_id):
        return get_object_or_404(Workshop, id = workshop_id)
    
    def find_ws_id(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        venue_id = query_params.get('id', [None])[0]
        return venue_id
    
    def add_papers_openreview(self, workshop):
        from . import OpenReviewClient as ORC

        # finds and adds all papers that are associated with a Workshop in OpenReview. 
        ORC_instance = ORC().openreview_object
        venue_id = self.find_ws_id(workshop.openreview_url)
        all_submissions = None
        if venue_id:
            try:
                venue_group = ORC_instance.get_group(id=venue_id)
                print(venue_group)
                submission_name = venue_group.content['submission_name']['value']
                all_submissions = ORC_instance.get_all_notes(invitation=f'{venue_id}/-/{submission_name}')

            except:
                pass 

        paper_form_list = []
        author_form_list = []
        print(all_submissions)
        if all_submissions is not None:
            for i,submission in enumerate(all_submissions):
                paper_title = submission.content['title']['value']

                form_data = {
                    'paper_title': paper_title,
                }
                form_files = {}

                # Get the PDF binary data
                try:
                    pdf_binary = ORC_instance.get_pdf(id=submission.id)

                    # Convert the binary data to an in-memory file object
                    pdf_io = io.BytesIO(pdf_binary)
                    pdf_io.seek(0)  # Move cursor to the start of the file

                    # Create an InMemoryUploadedFile object
                    in_memory_pdf = InMemoryUploadedFile(
                        file=pdf_io,
                        field_name='uploaded_file',
                        name=f"{paper_title}.pdf",
                        content_type='application/pdf',
                        size=pdf_io.getbuffer().nbytes,
                        charset=None
                    )
                    form_data['pages'] = len(PdfReader(pdf_io).pages)
                    form_files['uploaded_file'] = in_memory_pdf
                    # add agreement file here
                except:
                    # if a pdf isn't connected to the paper title it's probably a desk rejected paper.
                    pass
                
                # we save the paper form here to store the files.
                paper_form = PaperForm(form_data, form_files, workshop = workshop)
                if paper_form.is_valid():
                    paper_instance = paper_form.save(commit=False)
                    paper_instance.uploaded_file = in_memory_pdf
                    paper_instance.workshop = workshop
                    paper_instance.save()
                    paper_form_list.append(paper_form)
                else:
                    print(paper_form.errors)
                
                # add the authors
                try:
                    list_of_authors = submission.content['authors']['value']
                    data = [{'author_name' : author_name} for author_name in list_of_authors]
                    # generate author formset for every author listed.
                    author_formset = get_author_formset(extra=len(data))(queryset=Author.objects.none(), initial = data, prefix=f"author{i}")
                    author_form_list.append(author_formset)
                except:
                    author_form_list = ['' for _ in range(len(paper_form_list))]
                    pass

                        
        paper_author_combinations = zip(paper_form_list, author_form_list)             

        return paper_author_combinations
    
    def get(self, request):
        form = WorkshopForm()
        editor_form = EditorFormSet(queryset=Editor.objects.none(), 
                                    prefix='editor')
        session_form = SessionFormSet(queryset=Session.objects.none(), 
                                      prefix='session')
        context = {'form':form, 
                   'editor_form':editor_form, 
                   'session_form':session_form}
        return render(request, "workshops/create_workshop.html", context)
    

    def post(self, request):
        if 'submit_button' in request.POST: 
               
            workshop_instance = self.get_workshop(request.POST.get('workshop_id')) if request.POST.get('workshop_id') else None

            editor_formset = EditorFormSet(queryset=Editor.objects.none(), data=request.POST, prefix="editor")
            session_formset = SessionFormSet(queryset=Session.objects.none(), data=request.POST, prefix="session")

            workshop_form = WorkshopForm(data=request.POST, files=request.FILES, instance=workshop_instance)

            # Once forms have been bound (either using old or new editor agreement), we validate and save to the database.
            if all([workshop_form.is_valid(), editor_formset.is_valid(), session_formset.is_valid()]):

                workshop = workshop_form.save()  

                editor_instances = editor_formset.save()
                session_instances = session_formset.save()
                workshop.editors.add(*editor_instances)
                workshop.sessions.add(*session_instances)

                # if we have a linked open review page we extract the openreview papers and display them on a page where they can be reviewed
                if workshop.openreview_url:
                    paper_author_combinations = self.add_papers_openreview(workshop)
                    context = {
                        'workshop_id' : workshop.id,
                        'paper_author_combinations' : paper_author_combinations,
                    }
                    return render(request, 'workshops/open_review_editpage.html', context)
                    
                return redirect('workshops:workshop_overview', secret_token=workshop.secret_token)

        else:

            workshop_form = WorkshopForm(data = request.POST, 
                                         files = request.FILES)
            editor_formset = EditorFormSet(queryset=Editor.objects.none(),
                                           data = request.POST, 
                                           prefix="editor")
            session_formset = SessionFormSet(queryset=Session.objects.none(),data = request.POST, prefix="session")
            # before rendering we check if the bound forms are valid and we save a workshop instance so that the editor agreement can be extracted in a later stage
            if all([workshop_form.is_valid(), editor_formset.is_valid(), session_formset.is_valid()]):

                workshop_instance = workshop_form.save()  
                workshop_instance.openreview_url = request.POST['openreview_url']
                workshop_instance.save()


                bound_workshop_form = WorkshopForm(instance = workshop_instance)

                context = {
                    'form': bound_workshop_form,
                    'editor_form': editor_formset,
                    'session_form': session_formset,
                    'workshop_instance': workshop_instance
                }
                return render(request, self.edit_path, context)
            else:
                context = {
                    'form': workshop_form,
                    'editor_form': editor_formset,
                    'session_form': session_formset
                }
                return render(request, self.edit_path, context)