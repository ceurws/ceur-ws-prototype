from django.urls import path

from . import views
from .views import create_workshop, edit_workshop, workshop_overview

app_name = "workshops"

urlpatterns = [
    path('', views.index, name='index'),
    path('create_workshop/', create_workshop, name='create_workshop'),
    path('author_upload/<int:workshop_id>/', views.author_upload, name='author_upload'),
    path('edit_workshop/<int:workshop_id>/', edit_workshop, name='edit_workshop'),
    path('edit_workshop/', edit_workshop, name='edit_workshop'),
    path('create_workshop/<int:workshop_id>/', create_workshop, name='create_workshop'),
    path('workshop_overview/<int:workshop_id>/', workshop_overview, name='workshop_overview'),
    path('author_upload_success/', views.metadata_added_success, name='author_upload_success'),
    path('workshop_edit_success/<int:workshop_id>/', views.workshop_edit_success, name='workshop_edit_success'),
    path('metadata_added_success/<int:paper_id>', views.metadata_added_success, name='metadata_added_success'),
    path('author_overview/<int:paper_id>/', views.author_overview, name='author_overview'),
]
