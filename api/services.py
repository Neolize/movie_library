from django_filters import rest_framework

from rating_movies.models import Movie


class GenresInFilter(rest_framework.BaseInFilter, rest_framework.CharFilter):
    pass


class MovieFilter(rest_framework.FilterSet):
    genres = GenresInFilter(field_name="genres__name", lookup_expr="in")
    year = rest_framework.RangeFilter()

    class Meta:
        model = Movie
        fields = ("genres", "year")
