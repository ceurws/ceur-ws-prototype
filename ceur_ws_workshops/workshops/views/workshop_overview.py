from django.shortcuts import render, get_object_or_404
from ..models import Workshop, Paper
from django.conf import settings
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
import json, os, zipfile
from datetime import date
from django.conf import settings
from ..forms import WorkshopForm, PaperForm

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
            'paper_forms' : [PaperForm(instance=paper_instance) for paper_instance in workshop.accepted_papers.all()],
            'session_title_list' : [session_object.session_title for session_object in workshop.sessions.all()],
            'edit_mode': edit_mode,
            
            'secret_token': self.kwargs['secret_token']
        })

    def get(self, request, secret_token):
        return self.render_workshop(request)        
    
    def _get_workshop_data(self, workshop):
        return {
            "JJJJ":	workshop.year_final_papers,
            "YYYY": workshop.workshop_begin_date.year, 
            "NNNN": workshop.workshop_acronym,
            # "DD": date.today().day,
            # "MM": date.today.month,
            "XXX": workshop.volume_number,
            "CEURLANG": workshop.workshop_language_iso,
            "CEURVOLNR": workshop.pk,
            "CEURPUBYEAR":str(workshop.workshop_begin_date.year), #workshop_begin_date
            "CEURURN": workshop.urn,
            "CEURVOLACRONYM": workshop.workshop_acronym,
            "CEURVOLTITLE": workshop.workshop_short_title,
            "CEURFULLTITLE": workshop.workshop_full_title,
            "CEURDESCRIPTION": workshop.workshop_description,
            "CEURCOLOCATED": workshop.workshop_colocated,
            "CEURLOCTIME":{
                "CEURCITY": workshop.workshop_city,
                "CEURCOUNTRY": workshop.workshop_country,
                "CEURBEGINDATE": workshop.workshop_begin_date,
                "CEURENDDATE": workshop.workshop_end_date,
            },
            "CEUREDITORS": [],
            "email_address": workshop.volume_owner_email,
            
            "CEURSESSIONS": [],
            "CEURPAPERS": [],
            "CEURPUBDATE": date.today(),
            "CEURSUBMITTEDPAPERS": workshop.total_submitted_papers,
            "CEURACCEPTEDPAPERS": workshop.total_accepted_papers,
            "CEURACCEPTEDSHORTPAPERS": workshop.total_reg_acc_papers,
            "CEURACCEPTEDSHORTPAPERS": workshop.total_short_acc_papers,
            "CEURLIC": workshop.license,
            "secret_token": str(workshop.secret_token),
        }
    
    def add_editors_data(self, workshop, workshop_data):
        editors_data = [
        {
            "CEURVOLEDITOR": editor.editor_name,
            "CEUREDITOREMAIL": editor.editor_url,
            "CEURINSTITUTION": editor.institution,
            "CEURCOUNTRY": editor.institution_country,
            "CEURINSTITUTIONURL": editor.institution_url,
            "CEURRESEARCHGROUP": editor.research_group 
        }
        for editor in workshop.editors.all()
        ]
        workshop_data['CEUREDITORS'] = editors_data

    def add_papers_data(self, workshop, workshop_data):
        if workshop.sessions.exists():
            sessions_data = []
            for session in workshop.sessions.all():
                session_data = {
                    "session_title": session.session_title,
                    "papers": [
                        {
                            "CEURTITLE": paper.paper_title,
                            "CEURPAGES": paper.pages,
                            "CEURAUTHOR": [str(author) for author in paper.authors.all()],
                            "uploaded_file_url": paper.uploaded_file.url if paper.uploaded_file else None,
                            "agreement_file_url": paper.agreement_file.url if paper.agreement_file else None,
                        }
                        for paper in session.paper_set.all()
                    ]
                }
                sessions_data.append(session_data)
            workshop_data['CEURSESSIONS'] = sessions_data
            del(workshop_data['CEURPAPERS'])
        else:
            papers_data = [
                {
                    "CEURTITLE": paper.paper_title,
                    "CEURPAGES": paper.pages,
                    "CEURAUTHOR": [str(author) for author in paper.authors.all()],
                    "uploaded_file_url": paper.uploaded_file.url if paper.uploaded_file else None,
                    "agreement_file_url": paper.agreement_file.url if paper.agreement_file else None,
                }
                for paper in workshop.accepted_papers.all()
            ]
            del(workshop_data['CEURSESSIONS'])
            workshop_data['CEURPAPERS'] = papers_data

    def _save_workshop_data(self, workshop_data, workshop):
        directory_path = os.path.join(settings.BASE_DIR, 'workshop_metadata')
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path, f'workshop_{workshop.id}_metadata.json')

        with open(file_path, 'w') as file:
            json.dump(workshop_data, file, cls=DjangoJSONEncoder, indent=4)

    def _zip_agreement_files(self, workshop):
        agreement_path = os.path.join(settings.MEDIA_ROOT, 'agreement', f'Vol-{workshop.id}', )
        os.makedirs('zipped_agreements', exist_ok=True)
        zip_filename = os.path.join(settings.BASE_DIR, 'zipped_agreements', f'AGREEMENTS-Vol-{workshop.id}.zip')
    
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, _, files in os.walk(agreement_path):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), agreement_path))
    
    def submit_workshop(self, request, secret_token):
        submit_path = 'workshops/submit_workshop.html'

        workshop = get_object_or_404(Workshop, secret_token=secret_token)
        workshop_data = self._get_workshop_data(workshop)

        self.add_editors_data(workshop, workshop_data)
        self.add_papers_data(workshop, workshop_data)   
        self._save_workshop_data(workshop_data, workshop)
        request.session['json_saved'] = True

        self._zip_agreement_files(workshop)
        messages.success(request, 'Workshop submitted successfully.')

        return render(request, submit_path)
    
    def post(self, request, secret_token):
        workshop = get_object_or_404(Workshop, secret_token=secret_token)
        
        if request.POST["submit_button"] == "Edit":
            return self.render_workshop(request, edit_mode = True)
        elif request.POST["submit_button"] == "Confirm":
            workshop_form = WorkshopForm(instance=self.get_workshop(), data=request.POST, files = request.FILES)

            if workshop_form.is_valid():
                workshop_form.save()

            else:
                print(workshop_form.errors)

            existing_paper_ids = request.POST.getlist('paper_id')  
            papers_to_delete = request.POST.getlist('papers_to_delete') 

            for paper_id in papers_to_delete:
                Paper.objects.filter(id=paper_id).delete()

            for paper_id in existing_paper_ids:
                if paper_id in papers_to_delete:
                    continue  
                paper_instance = Paper.objects.filter(id=paper_id, workshop = workshop).first()
                
                paper_form = PaperForm(data = request.POST, files = request.FILES, instance=paper_instance, workshop = workshop)
                if paper_form.is_valid():
                    paper_form.save()

                workshop.accepted_papers.add(paper_instance)

            return self.render_workshop(request, edit_mode=False)
        elif request.POST["submit_button"] == "Submit Workshop":
            return self.submit_workshop(request, secret_token)