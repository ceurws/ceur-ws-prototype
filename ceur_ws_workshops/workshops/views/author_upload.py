from django.shortcuts import render, get_object_or_404, redirect
from ..models import Workshop, Paper, Author, Session
from django.views import View
from ..forms import PaperForm, get_author_formset
import  PyPDF2
from django.core.files.base import ContentFile
from .util import *

class AuthorUpload(View):
    upload_path = "workshops/author_upload.html"
    edit_path  = "workshops/edit_author.html"
    success_path = "workshops/author_upload_success.html"
    
    def get_workshop(self):
        workshop = get_object_or_404(Workshop, author_upload_secret_token=self.kwargs['author_upload_secret_token'])
        return workshop
    
    def get_context(self, author_formset, paper_form, condition='default', edit_paper_url=None):
        if condition == 'author':
            return {'author_formset': author_formset, 'paper_form': paper_form}
        elif condition == "confirm":
            return {'workshop': self.get_workshop(), 'paper': paper_form, 'authors': author_formset, 'edit_paper_url': edit_paper_url}
        return {'workshop': self.get_workshop(), 'author_formset': author_formset, 'paper_form': paper_form}
    
    def generate_agreement_html(self, paper, author_upload_secret_token, author_formset):
        template_name = 'workshops/ntp_agreement.html' if not paper.has_third_party_material else 'workshops/tp_agreement.html'
        context = {'paper': paper, 
                   'author_upload_secret_token': author_upload_secret_token,
                   'author_formset': author_formset,
                   'workshop': self.get_workshop()}
        html_content = render_to_string(template_name, context)
        return html_content, paper.has_third_party_material
    
    def generate_agreement(self, request, paper_id, author_upload_secret_token, author_formset):
        paper = get_object_or_404(Paper, id=paper_id)
        html_content, has_third_party_material = self.generate_agreement_html(paper, author_upload_secret_token, author_formset)
        response = HttpResponse(html_content, content_type='text/html')
        name = 'ntp_agreement.html' if not has_third_party_material else'tp_agreement.html'
        response['Content-Disposition'] = f'attachment; filename="{name}"'
        return name, html_content
    
    def check_paper_exists(self, paper_form, workshop):
        paper_title = paper_form.cleaned_data.get('paper_title')
        return Paper.objects.filter(paper_title=paper_title, workshop=workshop).exists()
    
    def submit_paper(self, request, author_formset, paper_form):

        if paper_form.is_valid() and author_formset.is_valid():
            
            # save paper and assign workshop
            paper_instance = paper_form.save(commit=False)
            paper_instance.workshop = self.get_workshop()
            
            # if any new files uploaded in the edit stage they get added here. Also amount of pages is added
            if request.FILES.get('uploaded_file', False):
                paper_instance.uploaded_file = request.FILES['uploaded_file']
                pdfReader = PyPDF2.PdfReader(paper_instance.uploaded_file)
                paper_instance.pages = len(pdfReader.pages)

            # handling of agreement_file if it has been uploaded in the edit stage
            if request.FILES.get('agreement_file', False):
                paper_instance.agreement_file = request.FILES['agreement_file']
            
            # if the paper already has authors we remove them to replace them with existing authors. This is only the case if paper has been uploaded with openreview.
            if paper_instance.authors.exists():
                paper_instance.authors.clear()

            
            # handles paper session if it has been added or changed.
            if request.POST['session'] != '':
                session_instance = Session.objects.get(pk=request.POST['session'])
                paper_instance.session = session_instance
            
            # saves and adds author instances from author formset.
            author_instances = author_formset.save()
            paper_instance.authors.add(*author_instances)

            # adds paper_instances to workshop
            self.get_workshop().accepted_papers.add(paper_instance)

            # save paper
            paper_instance.save()

            return redirect('workshops:edit_author_post', paper_id = paper_instance.secret_token, author_upload_secret_token = self.kwargs['author_upload_secret_token'])
        else:
            
            return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))
    
    def create_paper(self, request, author_formset, paper_form, author_upload_secret_token):

        if paper_form.is_valid() and author_formset.is_valid():
            # TODO FIX 
            # if self.check_paper_exists(paper_form, self.get_workshop()):
            #     print("Paper with this title already exists in the workshop.")
            #     return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))
            paper_instance = paper_form.save(commit=False) 
            paper_instance.workshop = self.get_workshop()

            # check to see if any files are uploaded. If not, they are already attached to the paper_instance from openreview.
            if request.FILES:
                paper_instance.uploaded_file = request.FILES['uploaded_file']
            
            paper_instance.save()  
            if request.POST['session'] != '':
                session_instance = Session.objects.get(pk=request.POST['session'])
                paper_instance.session = session_instance

            # author_instances = author_formset.save()
            # paper_instance.authors.add(*author_instances)  

            self.get_workshop().accepted_papers.add(paper_instance)
            
            paper_form = PaperForm(file_uploaded=True, 
                                   workshop=self.get_workshop(), 
                                   instance=paper_instance, 
                                   pages=paper_form.cleaned_data['pages'])

            name, agreement_html_content = self.generate_agreement(request, paper_instance.id, author_upload_secret_token, author_formset)

            paper_instance.agreement_file.save(name, ContentFile(agreement_html_content.encode('utf-8')))
            paper_instance.save()           

            # request.session['author_formset_data'] = request.POST

            download_url = paper_instance.agreement_file
            context = {
                'author_formset' : author_formset, 
                'paper_form' : paper_form,
                'paper_instance' : paper_instance,
                'download_url' : download_url,
                }

            return render(request, self.edit_path, context)
        else:
            print(paper_form.errors)
            return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))

    def get(self, request, author_upload_secret_token):
        # if 'author_formset_data' in request.session:
        #     author_formset = get_author_formset()(data=request.session['author_formset_data'], prefix="author")
        # else:
        author_formset = get_author_formset()(queryset=Author.objects.none(), prefix="author")
        paper_form = PaperForm(file_uploaded=False, 
                               workshop=self.get_workshop(), 
                               hide_pages = True, 
                               hide_agreement = True,
                               hide_has_third_party_material = False)

        context = self.get_context(author_formset, paper_form)

        if self.get_workshop().openreview_url:
            context['paper_list'] = [paper for paper in self.get_workshop().accepted_papers.all()]

        return render(request, self.upload_path, context)

    def post(self, request, author_upload_secret_token):

        # if statement to check if a paperID is included in the post data, which means a paper was selected from the openreview dropdown. This is checked because then the file has already been uploaded.
        if request.POST.get('paper_id'):
            paper_instance = Paper.objects.get(id=request.POST['paper_id'])

            author_formset = get_author_formset()(queryset=paper_instance.authors.all(),
                                                data=request.POST, 
                                                prefix="author"
                                                )


            paper_form = PaperForm(request.POST,  
                                   file_uploaded=True, 
                                   instance = paper_instance,
                                   workshop=self.get_workshop(), 
                                   agreement_file = True, 
                                   clean_enabled = True)
            
            # print(paper_form.uploaded_file)

        # if statement to check if request.FILES has any new files attached. 
        elif bool(request.FILES.get('uploaded_file', False)) == True:
            author_formset = get_author_formset()(queryset=Author.objects.none(), 
                                                  data = request.POST, 
                                                  prefix="author")
            paper_form = PaperForm(request.POST, 
                                   request.FILES, 
                                   file_uploaded=True, 
                                   workshop=self.get_workshop(), 
                                   agreement_file = True, 
                                   clean_enabled = True)

        # if no files are attached we extract the files uploaded 
        else:
            print('fina round')
            author_formset = get_author_formset()(request.POST, prefix="author")

            paper_instance = Paper.objects.filter(secret_token=request.POST.get('secret_token'), workshop = self.get_workshop()).first()

            paper_form = PaperForm(request.POST, 
                                   file_uploaded=True, 
                                   workshop=self.get_workshop(), 
                                   instance = paper_instance, 
                                   agreement_file = True, 
                                   clean_enabled = True)

        if 'confirm_button' in request.POST:
            return self.submit_paper(request, author_formset, paper_form)
        else:
            return self.create_paper(request, author_formset, paper_form, author_upload_secret_token)