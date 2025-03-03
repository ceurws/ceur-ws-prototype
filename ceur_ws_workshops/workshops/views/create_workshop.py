from django.shortcuts import render, get_object_or_404, redirect
from ..models import Workshop, Paper, Editor, Author, Session, Preface
from django.urls import reverse
from django.views import View
from django.http import HttpResponse


from ..forms import WorkshopForm, EditorFormSet, PaperForm, SessionFormSet, get_author_formset, PrefaceFormset
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
                all_submissions = ORC_instance.get_all_notes(invitation=f'{venue_id}/-/Submission')

            except:
                pass 

        paper_form_list = []
        author_form_list = []

        if all_submissions != []:
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
                except:
                    # if a pdf isn't connected to the paper title it's probably a desk rejected paper.
                    pass
                
                # we save the paper form here to store the files.
                paper_form = PaperForm(form_data, form_files, workshop = workshop, agreement_not_required = True)
                if paper_form.is_valid():
                    paper_instance = paper_form.save(commit=False)
                    paper_instance.uploaded_file = in_memory_pdf
                    paper_instance.workshop = workshop
                    paper_instance.save()
                    paper_form_list.append(paper_form)
                else:
                    # validation errors can be printed here
                    pass
                
                # add the authors
                try:
                    list_of_authors = submission.content['authors']['value']
                    data = [{'author_name' : author_name} for author_name in list_of_authors]
                    # generate author formset for every author listed.
                    author_formset = get_author_formset(extra=len(data))(queryset=Author.objects.none(), initial = data, prefix=f"author{i}")
                    author_form_list.append(author_formset)
                except:
                    author_form_list.append('') 
                
            paper_author_combinations = zip(paper_form_list, author_form_list)             

        else:
            paper_author_combinations = None                                

        return paper_author_combinations

    def get(self, request):
        editor_form = EditorFormSet(queryset=Editor.objects.none(), 
                                    prefix='editor')
        session_form = SessionFormSet(queryset=Session.objects.none(), 
                                      prefix='session')

        preface_formset = PrefaceFormset(queryset=Preface.objects.none(),
                                        prefix = 'preface')
        workshop_id = request.GET.get('workshop_id')
        workshop_instance = self.get_workshop(workshop_id) if workshop_id else None

        form = WorkshopForm(instance=workshop_instance)

        context = {'form':form, 
                   'editor_form':editor_form, 
                   'session_form':session_form, 
                   'preface_formset': preface_formset}
        return render(request, "workshops/create_workshop.html", context)
    

    def post(self, request):
        if 'submit_button' in request.POST: 
            workshop_instance = self.get_workshop(request.POST.get('workshop_id')) if request.POST.get('workshop_id') else None

            if workshop_instance.submitted:

                # If the workshop is already submitted, show a pop-up and redirect to the workshop overview
                return HttpResponse(
                    f"""
                    <script type="text/javascript">
                        alert("This workshop has already been submitted.");
                        window.location.href = "{request.build_absolute_uri(redirect('workshops:workshop_overview', secret_token=workshop_instance.secret_token).url)}";
                    </script>
                    """
                )

            editor_formset = EditorFormSet(queryset=Editor.objects.none(), data=request.POST, prefix="editor")
            session_formset = SessionFormSet(queryset=Session.objects.none(), data=request.POST, prefix="session")
            
            workshop_form = WorkshopForm(data=request.POST, files=request.FILES, instance=workshop_instance)
            preface_formset = PrefaceFormset(data = request.POST, files = request.FILES, instance = workshop_instance, prefix = "preface")
            
            # Once forms have been bound (either using old or new editor agreement), we validate and save to the database.
            if all([workshop_form.is_valid(), editor_formset.is_valid(), session_formset.is_valid()
                    , preface_formset.is_valid()]):
                workshop = workshop_form.save()  

                editor_instances = editor_formset.save()
                session_instances = session_formset.save()

                # Save the formset, but don't commit to the database yet
                prefaces = preface_formset.save(commit=False)

                # Loop over deleted objects and delete them from the database
                for deleted_obj in preface_formset.deleted_objects:
                    deleted_obj.delete()

                # Save each preface that is not marked for deletion
                for preface in prefaces:
                    if preface not in preface_formset.deleted_objects:
                        preface.workshop = workshop
                        preface.save()

                # Add related editors and sessions
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

                workshop.submitted = True
                workshop.save()
                
                return redirect('workshops:workshop_overview', secret_token=workshop.secret_token)


            else:
                # if the forms are not valid we return the form with the errors
                # https://stackoverflow.com/questions/3097982/how-to-make-a-django-form-retain-a-file-after-failing-validation
                if workshop_form.instance.editor_agreement.url:
                    workshop_form.instance.editor_agreement = None

                if preface_formset.instance.preface.url:
                    preface_formset.instance.preface = None
                
                context = {
                    'form': workshop_form,
                    'editor_form': editor_formset,
                    'session_form': session_formset,
                    'preface_formset': preface_formset
                }
                return render(request, self.edit_path, context)

        else:
            workshop_form = WorkshopForm(data = request.POST, 
                                         files = request.FILES)
            editor_formset = EditorFormSet(queryset=Editor.objects.none(),
                                           data = request.POST, 
                                           prefix="editor")
            session_formset = SessionFormSet(queryset=Session.objects.none(),data = request.POST, prefix="session")
            preface_formset = PrefaceFormset(data = request.POST, files = request.FILES, prefix = "preface")
            
            # before rendering we check if the bound forms are valid and we save a workshop instance so that the editor agreement can be extracted in a later stage
            if all([workshop_form.is_valid(), editor_formset.is_valid(), session_formset.is_valid()
                    , preface_formset.is_valid()]):

                workshop_instance = workshop_form.save()  
                workshop_instance.openreview_url = request.POST['openreview_url']
                workshop_instance.save()
                
                bound_workshop_form = WorkshopForm(instance = workshop_instance)
                
                prefaces = preface_formset.save(commit=False)
                for preface in prefaces:
                    preface.workshop = workshop_instance
                    preface.save()

                context = {
                    'form': bound_workshop_form,
                    'editor_form': editor_formset,
                    'session_form': session_formset,
                    'workshop_instance': workshop_instance,
                    'preface_formset': preface_formset
                }
                return render(request, self.edit_path, context)
            else:
                context = {
                    'form': workshop_form,
                    'editor_form': editor_formset,
                    'session_form': session_formset,
                    'preface_formset': preface_formset
                }
                return render(request, self.edit_path, context)