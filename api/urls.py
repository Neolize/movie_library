from django.urls import path, include

from api import views


urlpatterns = [
    path("auth/", include("djoser.urls")),
    path("session_auth/", include("rest_framework.urls")),

    path("movie_list/", views.MovieAPIListView.as_view()),
    path("movie/<int:pk>/", views.MovieAPIDetailView.as_view()),
    path("actor_list/", views.ActorAPIListView.as_view()),
    path("actor/<int:pk>/", views.ActorAPIDetailView.as_view()),

    path("add/rating/", views.RatingAPICreateOrUpdateView.as_view()),
    path("add/review/", views.ReviewAPICreateView.as_view()),
]
