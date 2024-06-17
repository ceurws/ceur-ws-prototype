from django.shortcuts import render, get_object_or_404, redirect
from ..models import Workshop, Paper, Author, Session
from django.views import View
from ..forms import AuthorFormSet, PaperForm, get_author_formset
import os, PyPDF2
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.core.files.base import ContentFile
import uuid


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
                   'author_formset': author_formset}
        html_content = render_to_string(template_name, context)
        return html_content, paper.has_third_party_material

    def generate_agreement(self, request, paper_id, author_upload_secret_token, author_formset):
        paper = get_object_or_404(Paper, id=paper_id)
        html_content, has_third_party_material = self.generate_agreement_html(paper, author_upload_secret_token, author_formset)
        response = HttpResponse(html_content, content_type='text/html')
        name = 'ntp_agreement.html' if not has_third_party_material else'tp_agreement.html'
        response['Content-Disposition'] = f'attachment; filename="{name}"'
        return response, name, html_content
    
    def submit_paper(self, request, author_formset, paper_form):

        author_instances = None

        if paper_form.is_valid() and author_formset.is_valid():

            paper_instance = paper_form.save(commit=False)
            paper_instance.workshop = self.get_workshop()
            
            if request.FILES.get('uploaded_file', False):
                paper_instance.uploaded_file = request.FILES['uploaded_file']
                pdfReader = PyPDF2.PdfReader(paper_instance.uploaded_file)
                paper_instance.pages = len(pdfReader.pages)
        
            if request.FILES.get('agreement_file', False):
                paper_instance.agreement_file = request.FILES['agreement_file']
                paper_instance.agreement_file.name = self._get_agreement_filename(paper_instance, paper_instance.agreement_file.name)
            paper_instance.save()

            author_instances = author_formset.save()

            if request.POST['session'] != '':
                session_instance = Session.objects.get(pk=request.POST['session'])
                paper_instance.session = session_instance
            
            paper_instance.authors.add(*author_instances)
            self.get_workshop().accepted_papers.add(paper_instance)

            return redirect('workshops:edit_author_post', paper_id = paper_instance.secret_token, author_upload_secret_token = self.kwargs['author_upload_secret_token'])
        else:
            return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))
    
    def create_paper(self, request, author_formset, paper_form, author_upload_secret_token):

        if paper_form.is_valid() and author_formset.is_valid():
            
            paper_instance = paper_form.save(commit=False) 
            paper_instance.workshop = self.get_workshop()

            paper_instance.uploaded_file = request.FILES['uploaded_file']
            
            paper_instance.save()  
            if request.POST['session'] != '':
                session_instance = Session.objects.get(pk=request.POST['session'])
                paper_instance.session = session_instance

            # paper_instance.authors.add(*author_instances)  
            self.get_workshop().accepted_papers.add(paper_instance)  
            
            paper_form = PaperForm(file_uploaded=True, workshop=self.get_workshop(), instance=paper_instance, pages=paper_form.cleaned_data['pages'])

            # Build path 
            _, name, agreement_html_content = self.generate_agreement(request, paper_instance.id, author_upload_secret_token, author_formset)
            print(name)

            paper_instance.agreement_file.save(name, ContentFile(agreement_html_content.encode('utf-8')))
            paper_instance.save()            

            # if not agreement_file_path.endswith('.html'):
            #     agreement_file_path += '.html'
    
            # os.makedirs(os.path.dirname(agreement_file_path), exist_ok=True)
            
            # # Write the HTML content to the file
            # with open(agreement_file_path, 'w', encoding='utf-8') as agreement_file:
            #     agreement_file.write(agreement_html_content)
            
            
            context = {
                'author_formset' : author_formset, 
                'paper_form' : paper_form,
                'paper_instance' : paper_instance,
                }

            return render(request, self.edit_path, context)
        else:
            return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))


    def get(self, request, author_upload_secret_token):
        author_formset = AuthorFormSet(queryset=Author.objects.none(), prefix="author")
        paper_form = PaperForm(file_uploaded=False, 
                               workshop=self.get_workshop(), 
                               hide_pages = True, 
                               hide_agreement = True,
                               hide_has_third_party_material = False)

        context = self.get_context(author_formset, paper_form)
        return render(request, self.upload_path, context)

    def post(self, request, author_upload_secret_token):
        
        # if statement to check if request.FILES has any new files attached. 

        if bool(request.FILES.get('uploaded_file', False)) == True:
        # if bool(request.FILES.get('agreement_file', False)) == True and bool(request.FILES.get('uploaded_file', False)) == True:
            author_formset = AuthorFormSet(queryset=Author.objects.none(), data = request.POST, prefix="author")
            paper_form = PaperForm(request.POST, request.FILES, file_uploaded=True, workshop=self.get_workshop(), agreement_file = True)

       
        # if no files are attached we extract the files uploaded 
        else:
            author_formset = get_author_formset()(request.POST, prefix="author")

            paper_instance = Paper.objects.filter(secret_token=request.POST.get('secret_token'), workshop = self.get_workshop()).first()

            paper_form = PaperForm(request.POST, file_uploaded=True, workshop=self.get_workshop(), instance = paper_instance, agreement_file = True)

        if 'confirm_button' in request.POST:
            return self.submit_paper(request, author_formset, paper_form)
        else:
            
            return self.create_paper(request, author_formset, paper_form, author_upload_secret_token)