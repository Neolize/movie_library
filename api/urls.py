from django.urls import path

from api import views


urlpatterns = [
    path("movie_list/", views.MovieAPIListView.as_view()),
    path("movie/<int:pk>/", views.MovieAPIDetailView.as_view()),
]
