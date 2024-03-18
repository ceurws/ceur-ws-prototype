from django.urls import path

from . import views
from .views import CreateWorkshop, author_upload_class, WorkshopOverview

app_name = "workshops"

urlpatterns = [
    path('', views.index, name='index'),
    path('create_workshop/', CreateWorkshop.as_view(), name='create_workshop'),
    path('author_upload/<uuid:secret_token>/', author_upload_class.as_view(), name='author_upload'),
    path('workshop_overview/<uuid:secret_token>/', WorkshopOverview.as_view(), name='workshop_overview'),
    path('author_upload_success/', views.author_upload_check, name='author_upload_success'),
    path('workshop_edit_success/<int:workshop_id>/', views.workshop_edit_success, name='workshop_edit_success'),
    path('author_upload_check/<uuid:secret_token>/', views.author_upload_check, name='author_upload_check'),
    path('submit_workshop/<uuid:secret_token>/', views.submit_workshop, name='submit_workshop'),
]
