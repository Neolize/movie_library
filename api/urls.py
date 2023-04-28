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
    path("movie_list/", views.MovieAPIViewSet.as_view({"get": "list"})),
    path("movie/<int:pk>/", views.MovieAPIViewSet.as_view({"get": "retrieve"})),
    path("category_list/", views.CategoryAPIViewSet.as_view({"get": "list"})),
    path("category/<int:pk>/", views.CategoryAPIViewSet.as_view({"get": "retrieve"})),
    path("create/review/", views.ReviewAPICreateView.as_view()),
    path("update/review/<int:pk>/", views.ReviewAPIUpdateView.as_view()),
    path("update_or_create/rating/", views.RatingAPIUpdateOrCreateView.as_view()),
    path("destroy/rating/<int:movie_id>/", views.RatingAPIDestroyView.as_view()),
    path("destroy/review/<int:pk>/", views.ReviewAPIDestroyView.as_view()),
]
