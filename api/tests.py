import json
from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from django.contrib.auth.models import User

from api import serializers, views
from rating_movies import models


class ActorAPITestCase(APITestCase):
    def setUp(self):
        self.first_actor = models.Actor.objects.create(name="First actor", birth_date=date(year=1971, month=4, day=12))
        self.second_actor = models.Actor.objects.create(name="Second actor", birth_date=date.today())
        self.third_actor = models.Actor.objects.create(name="Third actor", birth_date=date(year=1993, month=11, day=2))

    def test_actor_detail(self):
        url = reverse("actor-detail", kwargs={"pk": 1})
        response = self.client.get(url)
        serializer_data = serializers.ActorDetailSerializer(self.first_actor).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_actor_search(self):
        url = reverse("actor-list")
        response = self.client.get(url, data={"search": self.third_actor.id})

        response_data = dict(response.data)
        response_data_results = dict(response_data.get("results")[0])
        serializer_data = serializers.ActorListSerializer(self.third_actor).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response_data.get("count"))
        self.assertEqual(serializer_data, response_data_results)

    def test_actor_filter(self):
        url = reverse("actor-list")
        response = self.client.get(url, data={"name": "Second actor"})

        response_data = dict(response.data)
        response_data_results = dict(response_data.get("results")[0])
        serializer_data = serializers.ActorListSerializer(self.second_actor).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response_data.get("count"))
        self.assertEqual(serializer_data, response_data_results)

    def test_actor_ordering(self):
        url = reverse("actor-list")
        response = self.client.get(url, data={"ordering": "-name"})

        response_data = dict(response.data)
        response_data_results = response_data.get("results")
        serializer_data = serializers.ActorListSerializer(
            [self.third_actor, self.second_actor, self.first_actor],
            many=True
        ).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, response_data.get("count"))
        self.assertEqual(serializer_data, response_data_results)


class GenreAPITestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.first_genre = models.Genre.objects.create(name="First genre", description="First test genre",
                                                       url="first-genre")
        self.second_genre = models.Genre.objects.create(name="Second genre", description="Second test genre",
                                                        url="second-genre")
        self.third_genre = models.Genre.objects.create(name="Third genre", description="Third test genre",
                                                       url="third-genre")

        self.superuser = User.objects.create_superuser("superuser")

    def test_genre_detail(self):
        url = reverse("genre-detail", kwargs={"pk": self.third_genre.pk})
        response = self.client.get(url)

        response_data = response.data
        serializer_data = serializers.GenreDetailSerializer(self.third_genre).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response_data)

    def test_genre_list(self):
        view = views.GenreAPIViewSet.as_view({"get": "list"})
        serializer_data = serializers.GenreListSerializer(
            [self.first_genre, self.second_genre, self.third_genre],
            many=True
        ).data

        url = reverse("genre-list")
        request = self.factory.get(url)
        force_authenticate(request, user=self.superuser)

        response = view(request)
        response_data = dict(response.data)
        results = response_data.get("results")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, response_data.get("count"))
        self.assertEqual(serializer_data, results)

    def test_create_genre(self):
        view = views.GenreAPIViewSet.as_view({"post": "create"})
        url = reverse("genre-list")
        new_genre = {"id": 4, "name": "fourth genre", "description": "", "url": "fourth-genre"}

        request = self.factory.post(url, data=new_genre, format="json")
        force_authenticate(request, user=self.superuser)
        response = view(request)
        response.data.pop("movie_genre")
        genres_number = models.Genre.objects.all().count()

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, genres_number)
        self.assertEqual(new_genre, response.data)

    def test_update_genre(self):
        url = reverse("genre-detail", args=(self.second_genre.id, ))
        data = {
            "id": 2,
            "name": "New name",
            "description": "Second test genre",
            "url": "second-genre",
        }
        json_data = json.dumps(data)

        self.client.force_login(self.superuser)
        response = self.client.put(url, data=json_data, content_type="application/json")
        self.second_genre.refresh_from_db()

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("New name", self.second_genre.name)

    def test_delete_genre(self):
        url = reverse("genre-detail", args=(self.third_genre.id, ))
        self.client.force_login(user=self.superuser)
        response = self.client.delete(url)
        genres_number = models.Genre.objects.all().count()

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, genres_number)


class RatingAPITestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser("superuser")
        self.user = User.objects.create_user("user")

        self.first_rating_star = models.RatingStar.objects.create(value=3)
        self.second_rating_star = models.RatingStar.objects.create(value=5)

        self.first_movie = models.Movie.objects.create(title="First movie")
        self.second_movie = models.Movie.objects.create(title="Second movie")

        self.first_rating = models.Rating.objects.create(
            ip="127.0.0.1",
            star=self.first_rating_star,
            movie=self.first_movie,
        )
        self.second_rating = models.Rating.objects.create(
            ip="127.0.0.1",
            star=self.second_rating_star,
            movie=self.second_movie,
        )

    def test_not_update_rating(self):
        url = reverse("update_or_create_rating")
        data = {"star": 1, "movie": 1}
        unauthorized_response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, unauthorized_response.status_code)

        self.client.force_login(user=self.user)
        forbidden_response = self.client.put(url, data=data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, forbidden_response.status_code)

        self.client.force_login(user=self.superuser)
        not_allowed_response = self.client.put(url, data=data)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, not_allowed_response.status_code)

        response = self.client.post(url, data=data)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_update_or_create_rating(self):
        url = reverse("update_or_create_rating")
        data = {"star": self.second_rating_star.id, "movie": self.first_movie.id}

        self.client.force_login(user=self.superuser)
        response = self.client.post(url, data=data)

        self.first_rating.refresh_from_db()
        serializer_data = serializers.RatingUpdateOrCreateSerializer(self.first_rating).data

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_delete_rating(self):
        url = reverse("destroy_rating", args=(self.second_movie.id, ))
        self.client.force_login(user=self.superuser)
        response = self.client.delete(url)
        ratings_number = models.Rating.objects.all().count()

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(1, ratings_number)
