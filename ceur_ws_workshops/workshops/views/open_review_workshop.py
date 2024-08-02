from django.views import View
from . import CreateWorkshop
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import WorkshopForm, EditorFormSet, SessionFormSet, PaperForm, get_author_formset, PrefaceFormset
from ..models import Editor, Session, Workshop, Paper, Author, Preface
from urllib.parse import urlparse, parse_qs
from django.http import HttpResponse
from openreview import OpenReviewException  # Ensure this is imported at the beginning

class OpenReviewClient:
    def __init__(self):
        import openreview        
        try: 
            self.openreview_object = openreview.api.OpenReviewClient(
                baseurl='https://api2.openreview.net',
                username='filipmorris@duck.com', 
                password='MxFNF93fXpGZ*3.'
            )
        except Exception as e:
            print('error creating openreview object',e)
            self.error = e
            self.openreview_object = None
    
class OpenReviewClass(View):
    def __init__(self):
        super().__init__()
        self.query = None

    def find_ws_id(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        venue_id = query_params.get('id', [None])[0]
        return venue_id

    def post(self, request):
        if request.POST.get('paper_title', None):
            for i, paper_title in enumerate(request.POST.getlist('paper_title')):

                data = {
                    'paper_title' : paper_title,
                    'pages' : request.POST.getlist('pages')[i]
                    }
                
                workshop = get_object_or_404(Workshop, id = request.POST.get('workshop_id'))
                paper = get_object_or_404(Paper, id = request.POST.getlist('paper_id')[i])
                
                paper_form = PaperForm(data = data, workshop = workshop, instance = paper, agreement_not_required = True)
    
                if paper_form.is_valid():
                    paper_instance = paper_form.save(commit=False)
                    paper_instance.workshop = workshop

                    if request.POST.getlist('session')[i] != "":
                        session = get_object_or_404(Session, pk=request.POST.getlist('session')[i])
                        paper_instance.session = session

                    if request.POST.get('author0-TOTAL_FORMS', None):
                        author_formset = get_author_formset(extra=request.POST[f'author{i}-TOTAL_FORMS'])(queryset=Author.objects.none(), data = request.POST, prefix=f'author{i}')
                        if author_formset.is_valid():
                            author_instances = author_formset.save()
                            paper_instance.authors.add(*author_instances)
                    instance = paper_form.save()
                    workshop.accepted_papers.add(instance)
                else:
                    print(paper_form.errors, "ERRORS")
            return redirect('workshops:workshop_overview', secret_token=workshop.secret_token)

        else:
            create_workshop_view = CreateWorkshop.as_view(openreview_url = self.query)
            return create_workshop_view(request)

    def get(self, request):        
        # search function
        query = request.GET.get('query')
        if query:
            self.query = query
            self.venue_id = self.find_ws_id(query)

            if self.venue_id:
                try:
                    ORC = OpenReviewClient().openreview_object
                    venue_group = ORC.get_group(id=self.venue_id)
                    # results = venue_group.members
                    submission_name = venue_group.content['submission_name']['value']
                    all_submissions = ORC.get_all_notes(invitation=f'{self.venue_id}/-/{submission_name}')

                except Exception as e:
                    
                    print('excepted', str(e))
                    print(type(str(e)))
                    print(dict(e))
                    print(repr(e))
                    context = {'query' : None, 'error' : e}
                    return render(request, "workshops/open_review_workshop.html", context)

                data = {
                    'workshop_city': venue_group.content.get('location', {}).get('value', '').split(',')[0] if 'location' in venue_group.content else None,
                    'workshop_country': venue_group.content.get('location', {}).get('value', '').split(',')[-1] if 'location' in venue_group.content else None,
                    'workshop_full_title': venue_group.content.get('title', {}).get('value'),
                    'workshop_acronym': venue_group.content.get('subtitle', {}).get('value'),
                    'workshop_begin_date': venue_group.content.get('start_date', {}).get('value'),
                    'total_submitted_papers': len(all_submissions) if all_submissions else None,
                }

                # Remove None values from data
                data = {k: v for k, v in data.items() if v is not None}

                workshop_form = WorkshopForm(data=data)
                editor_form = EditorFormSet(queryset=Editor.objects.none(), prefix='editor')
                session_form = SessionFormSet(queryset=Session.objects.none(), prefix='session')
                preface_formset = PrefaceFormset(queryset=Preface.objects.none(), prefix = "preface")
                context = {
                    'form': workshop_form,
                    'editor_form': editor_form,
                    'session_form': session_form,
                    'preface_formset': preface_formset,
                    'openreview_url': query
                }
                return render(request, "workshops/create_workshop.html", context)

        context = {
            'query' : query
        }
        print('rendering')
        return render(request, "workshops/open_review_workshop.html", context)