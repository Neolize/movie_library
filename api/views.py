from django.http import Http404
from rest_framework import generics, permissions, viewsets
from rest_framework.request import Request
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from api import serializers, paginations, services as api_services
from rating_movies.services.crud import read
from rating_movies.services.utils import get_client_ip


class ActorAPIViewSet(viewsets.ModelViewSet, api_services.PermissionMixin):
    queryset = read.get_all_actors_directors_ordered_by_parameter("id")
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    pagination_class = paginations.BasePagination
    filterset_fields = ["name"]
    search_fields = ["id", "age"]
    ordering_fields = ["id", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ActorListSerializer
        else:
            return serializers.ActorDetailSerializer

    def check_permissions(self, request: Request):
        self.check_user_permissions()


class MovieAPIViewSet(viewsets.ReadOnlyModelViewSet, api_services.PermissionMixin):
    filter_backends = (DjangoFilterBackend, )
    filterset_class = api_services.MovieFilter
    pagination_class = paginations.MovieAPIListPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.MovieListSerializer
        elif self.action == "retrieve":
            return serializers.MovieDetailSerializer

    def get_queryset(self):
        if self.action == "list":
            return read.get_all_movies_annotated_by_rating(request=self.request)
        elif self.action == "retrieve":
            api_services.update_movie_other_sources_rating_api(pk=self.kwargs.get("pk"))
            return read.get_movie_by_pk_annotated_by_rating(self.kwargs.get("pk"))


class GenreAPIViewSet(viewsets.ModelViewSet, api_services.PermissionMixin):
    queryset = read.get_all_genres_ordered_by_parameter("id")
    pagination_class = paginations.BasePagination

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.GenreListSerializer
        else:
            return serializers.GenreDetailSerializer

    def check_permissions(self, request: Request):
        self.check_user_permissions()


class CategoryAPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = read.get_all_categories_ordered_by_parameter("id")
    permission_classes = (permissions.IsAuthenticated, )
    pagination_class = paginations.BasePagination

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.CategoryListSerializer
        elif self.action == "retrieve":
            return serializers.CategoryDetailSerializer


class ReviewAPICreateView(generics.CreateAPIView):
    serializer_class = serializers.ReviewCreateSerializer
    permission_classes = (permissions.IsAdminUser, )


class ReviewAPIUpdateView(generics.UpdateAPIView):
    serializer_class = serializers.ReviewUpdateSerializer
    permission_classes = (permissions.IsAdminUser, )

    def get_queryset(self):
        queryset = read.get_review_set_by_parameters(pk=self.kwargs.get("pk"))
        if not queryset:
            raise Http404
        return queryset


class ReviewAPIDestroyView(generics.DestroyAPIView):
    serializer_class = serializers.ReviewDestroySerializer
    permission_classes = (permissions.IsAdminUser, )

    def get_queryset(self):
        queryset = read.get_review_set_by_parameters(pk=self.kwargs.get("pk"))
        if not queryset:
            raise Http404
        return queryset


class RatingAPIUpdateOrCreateView(generics.CreateAPIView):
    serializer_class = serializers.RatingUpdateOrCreateSerializer
    permission_classes = (permissions.IsAdminUser, )

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


class RatingAPIDestroyView(generics.DestroyAPIView):
    serializer_class = serializers.RatingDestroySerializer
    permission_classes = (permissions.IsAdminUser, )
    lookup_field = "movie_id"

    def get_queryset(self):
        queryset = read.get_rating_set_by_parameters(
            ip=get_client_ip(self.request),
            movie=self.kwargs.get("movie_id")
        )
        if not queryset:
            raise Http404
        return queryset
