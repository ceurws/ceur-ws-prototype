from django.views import View
import openreview
from django.shortcuts import render
from ..forms import WorkshopForm, EditorFormSet, SessionFormSet
from ..models import Editor, Session


class OpenReviewClient:
    def __init__(self, baseurl, username, password):
        self.client = openreview.Client(baseurl=baseurl, username=username, password=password)

    def check_workshop(self, venue_id):
        submissions = self.client.get_all_notes(content={'venueid': venue_id})
        return list(submissions)

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

    # client = openreview.api.OpenReviewClient(
    # baseurl='https://api2.openreview.net',
    # username='filipmorris@duck.com', 
    # password='MxFNF93fXpGZ*3.'
    # )
    # venues = client.get_group(id='venues').members

    # # Find the id for your venue. For ICLR 2024 it's 'ICLR.cc/2024/Conference'
    # for v in venues:
    #     # if 'ICLR.cc/2024' in v:
    #         print(v)

class WorkshopView:
    def __init__(self):
        self.openreview_client = OpenReviewClient(
            baseurl='https://api2.openreview.net',
            username='filipmorris@duck.com', 
            password='MxFNF93fXpGZ*3.'
        )

    def post(self, request):
        # Handle form submission
        pass

    def get(self, request):
        form = WorkshopForm()
        editor_form = EditorFormSet(queryset=Editor.objects.none(), prefix='editor')
        session_form = SessionFormSet(queryset=Session.objects.none(), prefix='session')

        # This is not correct, we need to check whether the workshop is present based on some filled in value like the workshop short title or something similar
        venue_id = request.GET.get('venue_id')
        if venue_id:
            submissions = self.openreview_client.check_workshop(venue_id)
            if submissions:
                metadata = self.openreview_client.get_workshop_metadata(submissions[0])
                form = WorkshopForm(initial={
                    'workshop_full_title': metadata['title'],
                    'workshop_description': metadata['abstract']
                })

        context = {
            'form': form,
            'editor_form': editor_form,
            'session_form': session_form
        }
        return render(request, "workshops/create_workshop.html", context)
