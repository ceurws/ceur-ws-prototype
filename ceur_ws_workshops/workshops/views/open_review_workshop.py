from django.views import View
from . import CreateWorkshop
from django.shortcuts import render, redirect
from ..forms import WorkshopForm, EditorFormSet, SessionFormSet
from ..models import Editor, Session
from urllib.parse import urlparse, parse_qs
from django.http import HttpResponse



class OpenReviewClient:
    def __init__(self, baseurl, username, password):
        import openreview
        self.client = openreview.api.OpenReviewClient(baseurl=baseurl, username=username, password=password)

    def check_workshop(self, venue_id):
        submissions = self.client.get_all_notes(content={'venueid': venue_id})
        return list(submissions)
    
    def find_ws_id(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        venue_id = query_params.get('id', [None])[0]
        return venue_id

    def get_workshop_metadata(self, submission):
        metadata = {
            'title': submission.content['title']['value'],
            'pdf_url': 'https://openreview.net/' + submission.content['pdf']['value'],
            'openreview_page': 'https://openreview.net/forum?id=' + submission.id,
            'abstract': submission.content['abstract']['value'],
            'keywords': '; '.join(submission.content['keywords']['value']),
            'tldr': submission.content['TLDR']['value'] if 'TLDR' in submission.content else 'none'
        }
        return metadata


class OpenReviewClass(View):
    def __init__(self):
        super().__init__()
        self.query = None
        try:
            self.openreview_object = OpenReviewClient(
                baseurl='https://api2.openreview.net',
                username='filipmorris@duck.com', 
                password='MxFNF93fXpGZ*3.'
            )
        except Exception as e:
            # Log the error or handle it as needed
            print("Error initializing OpenReviewClient:", e)


    def post(self, request):
        print('now')
        create_workshop_view = CreateWorkshop.as_view(openreview_url = self.query)
        return create_workshop_view(request)

    def get(self, request):        
        # search function
        results = []
        query = request.GET.get('query')
        if query:
            self.query = query
            self.venue_id = self.openreview_object.find_ws_id(query)

            if self.venue_id:
                try:
                    venue_group = self.openreview_object.client.get_group(id=self.venue_id)
                    results = venue_group.members
                    submission_name = venue_group.content['submission_name']['value']
                    all_submissions = self.openreview_object.client.get_all_notes(invitation=f'{self.venue_id}/-/{submission_name}')

                except:
                    pass 
                # accepted_submissions = self.openreview_object.client.get_all_notes(content={'venueid':self.venue_id} )
  
                data = {
                'workshop_city' : venue_group.content['location']['value'].split(',')[0],
                'workshop_country' : venue_group.content['location']['value'].split(',')[-1],
                'workshop_full_title' : venue_group.content['title']['value'],
                'workshop_acronym' : venue_group.content['subtitle']['value'],
                'workshop_begin_date' : venue_group.content['start_date']['value'],
                'total_submitted_papers' : len(all_submissions),
                }
                # perhaps more data can be extracted? 
                
                workshop_form = WorkshopForm(data = data)
                editor_form = EditorFormSet(queryset=Editor.objects.none(), 
                                    prefix='editor')
                session_form = SessionFormSet(queryset=Session.objects.none(), 
                                      prefix='session')
                context = {'form':workshop_form,
                           'editor_form':editor_form,
                           'session_form':session_form,
                           'openreview_url':query}

                return render(request, "workshops/create_workshop.html", context)

        context = {
            'query' : query
        }
        return render(request, "workshops/open_review_workshop.html", context)
