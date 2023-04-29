from typing import Union

from django_filters import rest_framework
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rating_movies.models import Movie
from rating_movies.services.crud import update, read


class GenresInFilter(rest_framework.BaseInFilter, rest_framework.CharFilter):
    pass


class PermissionMixin:
    authenticated_user_actions = ("list", "retrieve")
    admin_actions = ("create", "update", "partial_update", "destroy")

    def check_user_permissions(self) -> list[Union[IsAuthenticated, IsAdminUser]]:
        """Check user's permissions for different actions"""

        if self.action in self.authenticated_user_actions:
            permission_classes = [IsAuthenticated]
        elif self.action in self.admin_actions:
            permission_classes = [IsAdminUser]
        else:
            raise PermissionDenied

        return [permission() for permission in permission_classes]


class MovieFilter(rest_framework.FilterSet):
    """Filtering movies by years and genres"""
    genres = GenresInFilter(field_name="genres__name", lookup_expr="in")
    year = rest_framework.RangeFilter()

    class Meta:
        model = Movie
        fields = ("genres", "year")


def update_movie_other_sources_rating_api(pk: int, data: dict = None) -> None:
    """Update OtherSourcesRating instance using gotten params: pk and data.
    If data wasn't given then get movie by pk and add needed information"""
    if data is None or not ("title" in data and "world_premiere" in data):
        movie = read.get_movie_by_parameters(pk=pk)
        data = {"title": movie.title, "world_premiere": movie.world_premiere}

    update.update_movie_other_sources_rating(movie_cleaned_data=data)
