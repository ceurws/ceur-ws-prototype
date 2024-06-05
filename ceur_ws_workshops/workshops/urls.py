from django.urls import path

# from . import views
from .views import index, CreateWorkshop, AuthorUpload, WorkshopOverview, edit_author_post_view, OpenReview
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "workshops"

urlpatterns = [
    path('', index, name='index'),
    path('open_review_workshop/', OpenReview.as_view(), name='open_review_workshop'),
    path('create_workshop/', CreateWorkshop.as_view(), name='create_workshop'),
    path('author_upload/<uuid:secret_token>/', AuthorUpload.as_view(), name='author_upload'),
    path('workshop_overview/<uuid:secret_token>/', WorkshopOverview.as_view(), name='workshop_overview'),
    path('author_upload/<uuid:paper_id>/<uuid:secret_token>/', edit_author_post_view, name='edit_author_post')
]

urlpatterns += staticfiles_urlpatterns()

