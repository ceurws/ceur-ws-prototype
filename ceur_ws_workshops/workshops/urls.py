from django.urls import path

from . import views
app_name = "workshops"
urlpatterns = [
    path('', views.index, name='index'),
    path('create_workshop/', views.create_workshop, name='create_workshop'),
    path('submit_paper/', views.submit_paper, name='submit_paper'),
    # path("", views.IndexView.as_view(), name="index"),
    # path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    # path("<int:question_id>/vote/", views.vote, name="vote"),
]
