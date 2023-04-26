from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend

from api import serializers, paginations
from api.services import MovieFilter
from rating_movies.services.crud import read
from rating_movies.services.utils import get_client_ip


class ActorAPIListView(generics.ListAPIView):
    queryset = read.get_all_actors_directors_ordered_by_parameter("id")
    serializer_class = serializers.ActorListSerializer
    pagination_class = paginations.BasePagination
    permission_classes = (permissions.IsAuthenticated, )


class MovieAPIListView(generics.ListAPIView):
    serializer_class = serializers.MovieListSerializer
    pagination_class = paginations.MovieAPIListPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = MovieFilter
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return read.get_all_movies_annotated_by_rating(request=self.request)


class ActorAPIDetailView(generics.RetrieveAPIView):
    queryset = read.get_all_actors_directors_ordered_by_parameter("id")
    serializer_class = serializers.ActorDetailSerializer


class MovieAPIDetailView(generics.RetrieveAPIView):
    # queryset = read.get_all_movies_ordered_by_parameter("id")
    serializer_class = serializers.MovieDetailSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        return read.get_movie_by_pk_annotated_by_rating(self.kwargs.get("pk", 1))


class ReviewAPICreateView(generics.CreateAPIView):
    serializer_class = serializers.ReviewCreateSerializer
    permission_classes = (permissions.IsAdminUser, )


class RatingAPICreateOrUpdateView(generics.CreateAPIView):
    serializer_class = serializers.CreateRatingSerializer
    permission_classes = (permissions.IsAdminUser, )

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip(self.request))


# class ActorAPICreateView(generics.CreateAPIView):
#     queryset = read.get_all_actors_directors_ordered_by_parameter("id")
#     serializer_class = serializers.ActorDetailSerializer
#     permission_classes = (IsAdminUser, )
#
#
# class ActorAPIUpdateView(generics.UpdateAPIView):
#     queryset = read.get_all_actors_directors_ordered_by_parameter("id")
#     serializer_class = serializers.ActorDetailSerializer
#     permission_classes = (IsAdminUser, )
#
#
# class ActorAPIDeleteView(generics.DestroyAPIView):
#     queryset = read.get_all_actors_directors_ordered_by_parameter("id")
#     serializer_class = serializers.ActorDetailSerializer
#     permission_classes = (IsAdminUser, )


# class ActorAPIDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = read.get_all_actors_directors_ordered_by_parameter("id")
#     serializer_class = serializers.ActorSerializer
