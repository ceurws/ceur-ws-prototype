from django.shortcuts import render, get_object_or_404, redirect
from ..models import Workshop, Paper, Author, Session
from django.views import View
from ..forms import AuthorFormSet, PaperForm
import os

class AuthorUpload(View):
    upload_path = "workshops/author_upload.html"
    edit_path  = "workshops/edit_author.html"
    success_path = "workshops/author_upload_success.html"
    
    def get_workshop(self):
        workshop = get_object_or_404(Workshop, secret_token=self.kwargs['secret_token'])
        return workshop
    
    def get_context(self, author_formset, paper_form, condition='default', edit_paper_url=None):
        if condition == 'author':
            return {'author_formset': author_formset, 'paper_form': paper_form}
        elif condition == "confirm":
            return {'workshop': self.get_workshop(), 'paper': paper_form, 'authors': author_formset, 'edit_paper_url': edit_paper_url}
        return {'workshop': self.get_workshop(), 'author_formset': author_formset, 'paper_form': paper_form}
    
    def _get_agreement_filename(self, paper_instance, original_filename):
        paper_title = paper_instance.paper_title.replace(' ', '')
        extension = os.path.splitext(original_filename)[1]
        new_filename = f'AUTHOR-AGREEMENT-{paper_title}{extension}'
        return new_filename
    
    def submit_paper(self, request, author_formset, paper_form):

        author_instances = None

        if paper_form.is_valid() and author_formset.is_valid():
            paper_instance = paper_form.save(commit=False)
            paper_instance.workshop = self.get_workshop()
            paper_instance.save()

            author_instances = author_formset.save()

            if request.POST['session'] != '':
                session_instance = Session.objects.get(pk=request.POST['session'])
                paper_instance.session = session_instance
            
            paper_instance.authors.add(*author_instances)
            self.get_workshop().accepted_papers.add(paper_instance)

            return redirect('workshops:edit_author_post', paper_id = paper_instance.secret_token, secret_token = self.kwargs['secret_token'])
        else:
            return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))
        
    def create_paper(self, request, author_formset, paper_form):

        if paper_form.is_valid() and author_formset.is_valid():
            paper_instance = paper_form.save(commit=False) 
            paper_instance.workshop = self.get_workshop()
            paper_instance.uploaded_file = request.FILES['uploaded_file']
            paper_instance.agreement_file = request.FILES['agreement_file']
            paper_instance.agreement_file.name = self._get_agreement_filename(paper_instance, paper_instance.agreement_file.name)
            
            paper_instance.save()  

            if request.POST['session'] != '':
                session_instance = Session.objects.get(pk=request.POST['session'])
                paper_instance.session = session_instance

            # paper_instance.authors.add(*author_instances)  
            self.get_workshop().accepted_papers.add(paper_instance)  
            
            context = {
                'author_formset' : author_formset, 
                'paper_form' : paper_form,
                'paper_instance' : paper_instance
                }

            return render(request, self.edit_path, context)
        else:
            return render(request, self.edit_path, self.get_context(author_formset, paper_form, 'author'))

    def get(self, request, secret_token):
        author_formset = AuthorFormSet(queryset=Author.objects.none(), prefix="author")
        paper_form = PaperForm(file_uploaded=False, workshop=self.get_workshop())
        context = self.get_context(author_formset, paper_form)
        return render(request, self.upload_path, context)

    def post(self, request, secret_token):
        
        # if statement to check if request.FILES has any new files attached. 
        if bool(request.FILES.get('agreement_file', False)) == True and bool(request.FILES.get('uploaded_file', False)) == True:
            author_formset = AuthorFormSet(queryset=Author.objects.none(), data = request.POST, prefix="author")
            paper_form = PaperForm(request.POST, request.FILES, file_uploaded=True, workshop=self.get_workshop())
       
        # if no files are attached we extract the files uploaded 
        else:
            author_formset = AuthorFormSet(request.POST, prefix="author")

            paper_instance = Paper.objects.filter(secret_token=request.POST.get('secret_token'), workshop = self.get_workshop()).first()

            paper_form = PaperForm(request.POST, file_uploaded=True, workshop=self.get_workshop(), instance = paper_instance)

        if 'confirm_button' in request.POST:
            return self.submit_paper(request, author_formset, paper_form)
        else:
            return self.create_paper(request, author_formset, paper_form)