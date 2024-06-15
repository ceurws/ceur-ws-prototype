from django.urls import path

# from . import views
from .views import index, CreateWorkshop, AuthorUpload, WorkshopOverview, edit_author_post_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import include

app_name = "workshops"

urlpatterns = [
    path('', index, name='index'),
    path('create_workshop/', CreateWorkshop.as_view(), name='create_workshop'),
    path('author_upload/<uuid:author_upload_secret_token>/', AuthorUpload.as_view(), name='author_upload'),
    path('workshop_overview/<uuid:secret_token>/', WorkshopOverview.as_view(), name='workshop_overview'),
    path('author_upload/<uuid:paper_id>/<uuid:author_upload_secret_token>/', edit_author_post_view, name='edit_author_post')
]

urlpatterns += staticfiles_urlpatterns()

