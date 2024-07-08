from django.shortcuts import render, get_object_or_404
from ..models import *
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
            'papers' : workshop.accepted_papers.all().order_by('order'),#[paper for paper in workshop.accepted_papers.all()],
            'workshop' : workshop,
            'workshop_form': WorkshopForm(instance=workshop, fields_not_required =True),
            # 'paper_forms' : [PaperForm(instance=paper_instance, workshop=workshop) for paper_instance in workshop.accepted_papers.all()],
            'paper_forms': PaperFormset(queryset = workshop.accepted_papers.all(), prefix = "paper",  agreement_not_required = True),
            'prefaces': workshop.prefaces.all(),
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
            workshop_form = WorkshopForm(instance=self.get_workshop(), data=request.POST, files = request.FILES, fields_not_required = True)
            editor_formset = EditorFormSet(request.POST, request.FILES, queryset=workshop.editors.all(), prefix="editor")
            paper_form = PaperFormset(data = request.POST, files = request.FILES, queryset = workshop.accepted_papers.all(), prefix="paper", agreement_not_required = True)
            if all([workshop_form.is_valid(), editor_formset.is_valid()]):
                workshop_form.save()
                editor_formset.save()
            elif paper_form.is_valid():
                print("HERERE")
                paper_form.save()

                if request.POST.get(paper_form, None):
                    for i, paper_form in enumerate(paper_form):
                        saved_paper_instance = paper_form.save(commit = False)
                        if request.POST.getlist('session')[i] != "":
                            session = get_object_or_404(Session, pk=request.POST.getlist('session')[i])
                            saved_paper_instance.session = session
                        else:
                            saved_paper_instance.session = None
                        saved_paper_instance.save()
                    
                    # session_id = request.POST.get(f'id_paper-{i}-session')
                    # print(session_id)
                    # if 'session' in request.POST:
                    #     session_id = request.POST.get('session')
                    #     session = get_object_or_404(Session, pk=session_id)
                    #     saved_paper_instance.session = session
                    # else:
                    #     saved_paper_instance.session = None
                    # saved_paper_instance.save()

                papers_to_delete = request.POST.getlist('papers_to_delete') 
                for paper_id in papers_to_delete:
                    Paper.objects.filter(id=paper_id).delete()

                if 'paper_order' in request.POST:
                    paper_order = json.loads(request.POST['paper_order'])
                    if not isinstance(paper_order, int):
                        for idx, paper_id in enumerate(paper_order):
                            Paper.objects.filter(id=paper_id).update(order=idx + 1)

                
                # if 'session' in request.POST:
                #     session_id = request.POST.get('session')
                #     if session_id:
                #         saved_session_instance = Session.objects.get(pk=session_id)
                #         saved_paper_instance.session = saved_session_instance
                #         saved_paper_instance.save()
                #     else:
                #         saved_paper_instance.session = None
                #         saved_paper_instance.save()
                
            if not workshop_form.is_valid():
                print("Workshop form errors:", workshop_form.errors)

            if not editor_formset.is_valid():
                print("Editor formset errors:", editor_formset.errors)

            if not paper_form.is_valid():
                print("Paper formset errors:", paper_form.errors)
            return self.render_workshop(request, edit_mode=False)
        elif request.POST["submit_button"] == "Submit Workshop":
            return self.submit_workshop(request, secret_token)
        
        