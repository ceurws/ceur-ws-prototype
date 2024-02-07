from django.urls import path

from . import views
from .views import add_editor, editor_added_success, create_workshop, workshop_created_success, edit_workshop, workshop_overview

app_name = "workshops"

urlpatterns = [
    path('', views.index, name='index'),
    path('add_editor/', add_editor, name='add_editor'),
    path('editor_added_success/', editor_added_success, name='editor_added_success'),
    path('create_workshop/', create_workshop, name='create_workshop'),
    path('workshop_created_success/', workshop_created_success, name='workshop_created_success'),
    path('add_author/', views.add_author, name='add_author'),
    path('author_added_success/', views.author_added_success, name='author_added_success'),
    path ('add_paper/', views.add_paper, name='add_paper'),
    path ('paper_added_success/', views.paper_added_success, name='paper_added_success'),
    path('edit_workshop/<int:workshop_id>/', edit_workshop, name='edit_workshop'),
    path('create_workshop/<int:workshop_id>/', create_workshop, name='create_workshop'),
    path('workshop_overview/<int:workshop_id>/', workshop_overview, name='workshop_overview')

]
