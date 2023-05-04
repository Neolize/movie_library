from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView

from api import views


router = DefaultRouter()
router.register(r"actor", views.ActorAPIViewSet)
router.register(r"genre", views.GenreAPIViewSet)


urlpatterns = [
    path("auth/", include("rest_framework_social_oauth2.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/token/login/", TokenCreateView.as_view(), name="authtoken_login"),
    path("auth/token/logout/", TokenDestroyView.as_view(), name="authtoken_logout"),
    path("session_auth/", include("rest_framework.urls")),

    path("", include(router.urls)),
    path("movies/", views.MovieAPIViewSet.as_view({"get": "list"})),
    path("movies/<int:pk>/", views.MovieAPIViewSet.as_view({"get": "retrieve"})),
    path("categories/", views.CategoryAPIViewSet.as_view({"get": "list"})),
    path("categories/<int:pk>/", views.CategoryAPIViewSet.as_view({"get": "retrieve"})),
    path("review/", views.ReviewAPICreateView.as_view()),
    path("review/<int:pk>/", views.ReviewAPIUpdateView.as_view()),
    path("destroy/review/<int:pk>/", views.ReviewAPIDestroyView.as_view()),
    path("rating/", views.RatingAPIUpdateOrCreateView.as_view(), name="update_or_create_rating"),
    path("rating/<int:movie_id>/", views.RatingAPIDestroyView.as_view(), name="destroy_rating"),
]
