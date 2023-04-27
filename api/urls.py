from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView

from api import views


router = DefaultRouter()
router.register(r"actor", views.ActorAPIViewSet)


urlpatterns = [
    path("auth/", include("rest_framework_social_oauth2.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/token/login/", TokenCreateView.as_view(), name="authtoken_login"),
    path("auth/token/logout/", TokenDestroyView.as_view(), name="authtoken_logout"),
    path("session_auth/", include("rest_framework.urls")),

    path("", include(router.urls)),
    path("movie_list/", views.MovieAPIViewSet.as_view({"get": "list"})),
    path("movie/<int:pk>/", views.MovieAPIViewSet.as_view({"get": "retrieve"})),
    path("genre_list/", views.GenreAPIViewSet.as_view({"get": "list"})),
    path("genre/<int:pk>/", views.GenreAPIViewSet.as_view({"get": "retrieve"})),
    path("category_list/", views.CategoryAPIViewSet.as_view({"get": "list"})),
    path("category/<int:pk>/", views.CategoryAPIViewSet.as_view({"get": "retrieve"})),

    path("add/rating/", views.RatingAPICreateOrUpdateView.as_view()),
    path("add/review/", views.ReviewAPICreateView.as_view()),
]
