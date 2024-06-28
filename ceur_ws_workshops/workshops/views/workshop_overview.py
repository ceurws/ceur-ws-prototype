from django.shortcuts import render, get_object_or_404
from ..models import Workshop, Paper, Session, Editor
from django.urls import reverse
from django.views import View
from django.contrib import messages
from ..forms import *
from .util import *
class WorkshopOverview(View):
    def get_workshop(self):
        workshop = get_object_or_404(Workshop, secret_token=self.kwargs['secret_token'])
        return workshop
    
    def render_workshop(self, request, edit_mode = False):
        workshop = self.get_workshop()
        return render(request, 'workshops/workshop_overview.html', context = {
            'papers' : [paper for paper in workshop.accepted_papers.all()],
            'workshop' : workshop,
            'workshop_form': WorkshopForm(instance=workshop),
            # 'paper_forms' : [PaperForm(instance=paper_instance, workshop=workshop) for paper_instance in workshop.accepted_papers.all()],
            'paper_forms': PaperFormset(queryset = workshop.accepted_papers.all(), prefix = "paper", agreement_not_required=True),
            'paper_forms_no_session' : [paper for paper in workshop.accepted_papers.all() if paper.session == None],
            'session_title_list' : [session_object.session_title for session_object in workshop.sessions.all()],
            'editor_forms': EditorFormSet(queryset=workshop.editors.all(), prefix="editor"),
            'edit_mode': edit_mode,
            'secret_token': self.kwargs['secret_token'],
            'organizer_url': reverse('workshops:workshop_overview', args=[workshop.secret_token]),
            'author_url': reverse('workshops:author_upload', args=[workshop.author_upload_secret_token])
        })

    def get(self, request, secret_token):
        return self.render_workshop(request)        
    
    def submit_workshop(self, request, secret_token):
        submit_path = 'workshops/submit_workshop.html'

        workshop = get_object_or_404(Workshop, secret_token=secret_token)
        workshop_data = get_workshop_data(workshop)

        add_editors_data(workshop, workshop_data)
        add_papers_data(workshop, workshop_data)   
        save_workshop_data(workshop_data, workshop)
        request.session['json_saved'] = True
        zip_agreement_files(workshop)
        messages.success(request, 'Workshop submitted successfully.')
        return render(request, submit_path)
    
    def post(self, request, secret_token, open_review = False):
        workshop = get_object_or_404(Workshop, secret_token=secret_token)
        
        # not sure if following if statement is necessary
        if request.POST["submit_button"] == "Edit":
            return self.render_workshop(request, edit_mode = True)
        
        elif request.POST["submit_button"] == "Confirm":
            workshop_form = WorkshopForm(instance=self.get_workshop(), data=request.POST, files = request.FILES)
            editor_formset = EditorFormSet(request.POST, request.FILES, queryset=workshop.editors.all(), prefix="editor", form_kwargs={'agreement_not_required': True})
            paper_form = PaperFormset(request.POST, request.FILES, queryset = workshop.accepted_papers.all(), prefix="paper")
            print(paper_form)
            print("request.POST", request.POST)
            print("before if !!!!")
            if all([workshop_form.is_valid(), editor_formset.is_valid(), paper_form.is_valid()]):
                print("in if ")
                workshop_form.save()
                editor_formset.save()
                saved_paper_instance = paper_form.save()
                if request.POST['session'] != '':
                    saved_session_instance = Session.objects.get(pk=request.POST['session'])
                    saved_paper_instance.session = saved_session_instance
                else:
                    saved_paper_instance.session = None

                workshop.accepted_papers.add(saved_paper_instance)
            else: 
                print("paper formset", paper_form.errors)
                print("NOOOOO")
                return self.render_workshop(request, edit_mode=True) 
            
            # existing_paper_ids = request.POST.getlist('paper_id')  
            papers_to_delete = request.POST.getlist('papers_to_delete') 
            for paper_id in papers_to_delete:
                Paper.objects.filter(id=paper_id).delete()


            # for paper_id in existing_paper_ids:
            #     if paper_id in papers_to_delete:
            #         continue  

            #     # paper_instance = Paper.objects.filter(id=paper_id, workshop = workshop).first()
            #     # paper_form = PaperForm(data = request.POST, files = request.FILES, instance=paper_instance, workshop = workshop)
                
            #     print(paper_form)
               
            #         order_key = f'order_{paper_id}'
            #         if order_key in request.POST:
            #             saved_paper_instance.order = int(request.POST[order_key])
            #             print(saved_paper_instance.order)
            #             saved_paper_instance.save()
            #         print("SUCESSSS")
            

            return self.render_workshop(request, edit_mode=False)
        elif request.POST["submit_button"] == "Submit Workshop":
            return self.submit_workshop(request, secret_token)
        
        