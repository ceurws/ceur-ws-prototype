from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import json
import os
from ..models import Workshop
from django.conf import settings
from django.views import View

class GenerateHtml(View):
    def get(self, request, workshop_id):

        json_file_path = os.path.join(settings.BASE_DIR, 'workshop_metadata', f'workshop_{workshop_id}_metadata.json')

        with open(json_file_path, 'r') as json_file:
            workshop_data = json.load(json_file)

        html_content = self.generate_html(workshop_data)

        return HttpResponse(html_content, content_type='text/html')

    def generate_html(self, request, workshop_data):
        return render(request, 'workshops/generated_html_template.html', {'data': workshop_data})
