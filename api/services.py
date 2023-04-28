from django_filters import rest_framework
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from rating_movies.models import Movie
from rating_movies.services.crud import update, read


class GenresInFilter(rest_framework.BaseInFilter, rest_framework.CharFilter):
    pass


class PermissionMixin:
    def check_user_permissions(self, request):
        authenticated_user_actions = ("list", "retrieve")
        admin_actions = ("create", "update", "partial_update", "destroy")

        if self.action in authenticated_user_actions and not bool(request.user and request.user.is_authenticated):
            raise NotAuthenticated

        elif self.action in admin_actions and not bool(request.user and request.user.is_staff):
            raise PermissionDenied


class MovieFilter(rest_framework.FilterSet):
    genres = GenresInFilter(field_name="genres__name", lookup_expr="in")
    year = rest_framework.RangeFilter()

    class Meta:
        model = Movie
        fields = ("genres", "year")


def update_movie_other_sources_rating_api(pk: int, data: dict = None) -> None:
    if data is None or not ("title" in data and "world_premiere" in data):
        movie = read.get_movie_by_parameters(pk=pk)
        data = {"title": movie.title, "world_premiere": movie.world_premiere}

    update.update_movie_other_sources_rating(movie_cleaned_data=data)
