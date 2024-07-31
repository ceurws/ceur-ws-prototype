from django.urls import path

# from . import views
from .views import index, CreateWorkshop, AuthorUpload, WorkshopOverview, edit_author_post_view, GenerateHtml, OpenReviewClass
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import include
from django.urls import re_path
from django.views.static import serve
from django.conf import settings
app_name = "workshops"

urlpatterns = [
    path('', index, name='index'),
    path('create_workshop/', CreateWorkshop.as_view(), name='create_workshop'),
    path('author_upload/<uuid:author_upload_secret_token>/', AuthorUpload.as_view(), name='author_upload'),
    path('workshop_overview/<uuid:secret_token>/', WorkshopOverview.as_view(), name='workshop_overview'),
    path('open_review_workshop/', OpenReviewClass.as_view(), name='open_review_workshop'),
    path('open_review_edit', OpenReviewClass.as_view(), name='open_review_edit'),
    path('author_upload/<uuid:paper_id>/<uuid:author_upload_secret_token>/', edit_author_post_view, name='edit_author_post'),
]

urlpatterns += staticfiles_urlpatterns()

