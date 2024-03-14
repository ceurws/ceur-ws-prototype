from django.urls import path

from . import views
from .views import create_workshop, workshop_overview, author_upload

app_name = "workshops"

urlpatterns = [
    path('', views.index, name='index'),
    path('create_workshop/', create_workshop, name='create_workshop'),
    path('author_upload/<uuid:secret_token>/', author_upload, name='author_upload'),
    path('create_workshop/<int:workshop_id>/', create_workshop, name='create_workshop'),
    path('workshop_overview/<uuid:secret_token>/', workshop_overview, name='workshop_overview'),
    path('author_upload_success/', views.author_upload_check, name='author_upload_success'),
    path('workshop_edit_success/<int:workshop_id>/', views.workshop_edit_success, name='workshop_edit_success'),
    path('author_upload_check/<uuid:secret_token>/', views.author_upload_check, name='author_upload_check'),
    path('submit_workshop/<uuid:secret_token>/', views.submit_workshop, name='submit_workshop'),
]
