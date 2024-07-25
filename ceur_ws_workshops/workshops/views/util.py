from datetime import date
from django.conf import settings
import os, json, zipfile, hashlib
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from ..models import *

def get_workshop_data(workshop):
    '''
    Function that returns part of the metadata for the final JSON 
    '''
    workshop_data = {
        "JJJJ": workshop.year_final_papers,
        "YYYY": workshop.workshop_begin_date.year, 
        "NNNN": workshop.workshop_acronym,
        "DD": workshop.workshop_begin_date.day,
        "MM": workshop.workshop_begin_date.month,
        "XXX": workshop.volume_number,
        "CEURLANG": workshop.workshop_language_iso,
        "CEURVOLNR": str(workshop.id),
        "CEURPUBYEAR": str(workshop.workshop_begin_date.year),
        "CEURWORKSHOP_ID":  str(workshop.id),
        "CEURURN": workshop.urn,
        "CEURVOLACRONYM": workshop.workshop_acronym,
        "CEURVOLTITLE": workshop.workshop_short_title,
        "CEURFULLTITLE": workshop.workshop_full_title,
        "CEURDESCRIPTION": workshop.workshop_description,
        "CEURCOLOCATED": workshop.workshop_colocated,
        "CEURLOCTIME": {
            "CEURCITY": workshop.workshop_city,
            "CEURCOUNTRY": workshop.workshop_country,
            "CEURBEGINDATE": str(workshop.workshop_begin_date),
            "CEURENDDATE": str(workshop.workshop_end_date),
        },
        "CEUREDITORS": [],
        "email_address": workshop.volume_owner_email,
        "CEURSESSIONS": [],
        "CEURPAPERS": [],
        "CEURPUBDATE": str(date.today()),
        "CEURSUBMITTEDPAPERS": workshop.total_submitted_papers,
        "CEURACCEPTEDPAPERS": workshop.total_accepted_papers,
        "CEURACCEPTEDREGULARPAPERS": workshop.total_reg_acc_papers,
        "CEURACCEPTEDSHORTPAPERS": workshop.total_short_acc_papers,
        "CEURLIC": workshop.license,
        "secret_token": str(workshop.secret_token),
    }

    data_string = json.dumps(workshop_data, sort_keys=True)
    
    checksum = hashlib.md5(data_string.encode('utf-8')).hexdigest()
    
    # Add the checksum to the data
    workshop_data["CEURCHECKSUM"] = checksum
    
    return workshop_data

def add_editors_data(workshop, workshop_data):
    editors_data = [
    {
        "CEURVOLEDITOR": editor.editor_name,
        "CEUREDITOREMAIL": editor.editor_url,
        "CEURINSTITUTION": editor.institution,
        "CEUREDITORURL": editor.editor_url,
        "CEURCOUNTRY": editor.institution_country,
        "CEURINSTITUTIONURL": editor.institution_url,
        "CEURRESEARCHGROUP": editor.research_group 
    }
    for editor in workshop.editors.all()
    ]
    workshop_data['CEUREDITORS'] = editors_data

def add_papers_data(workshop, workshop_data):
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
            for paper in workshop.accepted_papers.all().order_by('order')
        ]
        del(workshop_data['CEURSESSIONS'])
        workshop_data['CEURPAPERS'] = papers_data

def save_workshop_data(workshop_data, workshop):
        directory_path = os.path.join(settings.BASE_DIR, 'workshop_metadata')
        os.makedirs(directory_path, exist_ok=True)
        file_path = os.path.join(directory_path, f'workshop_{workshop.id}_metadata.json')

        with open(file_path, 'w') as file:
            json.dump(workshop_data, file, cls=DjangoJSONEncoder, indent=4)

def zip_agreement_files(workshop):
        agreement_path = os.path.join(settings.MEDIA_ROOT, 'agreement', f'Vol-{workshop.id}', )
        os.makedirs('zipped_agreements', exist_ok=True)
        zip_filename = os.path.join(settings.BASE_DIR, 'zipped_agreements', f'AGREEMENTS-Vol-{workshop.id}.zip')
    
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, _, files in os.walk(agreement_path):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), agreement_path))

def zip_paper_files(workshop):
        file_path = os.path.join(settings.MEDIA_ROOT, 'papers', f'Vol-{workshop.id}', )
        os.makedirs('zipped_papers', exist_ok=True)
        zip_filename = os.path.join(settings.BASE_DIR, 'zipped_papers', f'PAPERS-Vol-{workshop.id}.zip')
    
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, _, files in os.walk(file_path):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), file_path))

def get_agreement_filename(paper_instance, original_filename):
    paper_title = paper_instance.paper_title.replace(' ', '')
    extension = os.path.splitext(original_filename)[1]
    new_filename = f'AUTHOR-AGREEMENT-{paper_title}{extension}'
    return new_filename





