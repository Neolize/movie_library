import logging
from typing import Union, Optional

import psycopg2
from django.db.models import Q, QuerySet, Count

from site_engine.settings import environ
from rating_movies.models import Category, Actor, Genre, Movie, MovieShots, RatingStar, Rating, OtherSourcesRating
from rating_movies.services.crud import specifications
from rating_movies.services.crud.crud_utils import BaseObject
from rating_movies.services.crud.decorators import base_movie_filter, base_movie_ordering, base_actor_director_ordering


LOGGER = logging.getLogger("json_main_logger")


class CategoryRepository(BaseObject):
    model = Category

    @staticmethod
    def get_related_objects(category: Category) -> QuerySet[Movie]:
        """Получает экземпляр класса Category
         и возвращает связанные с этим экземпляром фильмы"""
        return category.movie_category.filter(draft=False).order_by("-world_premiere")

    def get_non_empty_objects(self):
        return self.model.objects.annotate(total=Count("movie_category")).filter(total__gt=0)


class ActorDirectorRepository(BaseObject):
    model = Actor

    @base_actor_director_ordering
    def search_objects_by_name(self, name: str) -> QuerySet[Actor]:
        """Search all actors/directors by given name"""
        return self.model.objects.filter(name__icontains=name)

    @base_actor_director_ordering
    def search_objects_by_description(self, description: str) -> QuerySet[Actor]:
        """Search all actors/directors by given description"""
        return self.model.objects.filter(description__icontains=description)


class GenreRepository(BaseObject):
    model = Genre


class MovieRepository(BaseObject):
    model = Movie

    @base_movie_filter
    def get_all_objects_ordered_by_parameter(
            self, specification: specifications.ObjectsOrderBySpecification
    ) -> QuerySet[Movie]:
        """Return all published movies ordered by world premiere in reverse order"""
        return self.get_objects_ordered_by_params(specification)

    def create_new_object(self, obj: dict) -> Union[bool, Movie]:
        try:
            # удаляем из словаря поля типа Many to many
            directors = obj.pop("directors")
            actors = obj.pop("actors")
            genres = obj.pop("genres")

            new_movie = self.model.objects.create(**obj)

            # отдельно добавляем поля Many to many
            for director in directors:
                new_movie.directors.add(director)

            for actor in actors:
                new_movie.actors.add(actor)

            for genre in genres:
                new_movie.genres.add(genre)

            new_movie.save()
            return new_movie

        except Exception as exc:
            LOGGER.error(exc)
            return False

    def get_most_recently_added_objects(self, number: int) -> QuerySet[Movie]:
        """Return most recently added movies"""
        return self.model.objects.filter(draft=False).order_by("-id")[:number]

    @base_movie_ordering
    def get_objects_filtered_by_years_genres(self, years: list[str], genres: list[str]) -> QuerySet[dict]:
        """Return movies filtered by years or genres"""
        return self.model.objects.filter(
            Q(draft=False) & (Q(year__in=years) | Q(genres__in=genres))
        ).distinct().values("title", "tagline", "poster", "url")

    @base_movie_ordering
    def get_objects_filtered_by_combined_fields(self, years: list[str], genres: list[str]) -> QuerySet[dict]:
        """Return movies filtered by years and by genres"""
        return self.model.objects.filter(
            draft=False, year__in=years, genres__in=genres
        ).distinct().values("title", "tagline", "poster", "url")

    @base_movie_ordering
    @base_movie_filter
    def get_all_filtered_objects(self) -> QuerySet[dict]:
        """Return dictionaries list with all active movies(draft=False)"""
        return self.model.objects.values("title", "tagline", "poster", "url")

    def get_sorted_objects_by_parameter(self, parameter) -> QuerySet[dict]:
        query = self.get_all_objects_ordered_by_parameter(
            specification=specifications.ObjectsOrderBySpecification(parameter)
        )
        return query.values("url", "title", "poster", "tagline")

    @base_movie_ordering
    @base_movie_filter
    def search_objects_by_title(self, title: str) -> QuerySet[Movie]:
        """Search all active movies by given title"""
        return self.model.objects.filter(title__icontains=title)

    @base_movie_ordering
    @base_movie_filter
    def search_objects_by_description(self, description: str) -> QuerySet[Movie]:
        """Search all active movies by given description"""
        return self.model.objects.filter(description__icontains=description)

    @base_movie_filter
    def get_all_available_pk(self) -> QuerySet[dict[str: int]]:
        return self.model.objects.values("pk")

    def get_unique_params_dicts(self,
                                specification: specifications.UniqueValuesSpecification) -> QuerySet[dict[str: str]]:
        return self.model.objects.values(*specification.is_satisfied()).distinct()

    def get_count_movies(self) -> int:
        return self.model.objects.all().count()


class MovieShotRepository(BaseObject):
    model = MovieShots


class RatingStarRepository(BaseObject):
    model = RatingStar


class RatingRepository(BaseObject):
    model = Rating

    def get_rating(self, ip: int, movie_id: int) -> Optional[int]:
        """Возвращает рейтинг конкретного фильма для переданного ip адреса"""
        try:
            obj: Rating = self.model.objects.get(ip=ip, movie_id=movie_id)
            star = obj.star.value
        except self.model.DoesNotExist as exc:
            print(exc)
            star = None
        return star

    def update_or_create_rating(self, ip, movie_id, star_id) -> bool:
        """Создаёт новую запись в таблице Rating или обновляет уже имеющуюся"""
        try:
            self.model.objects.update_or_create(
                ip=ip, movie_id=movie_id, defaults={"star_id": star_id}
            )
            return True
        except Exception as exc:
            LOGGER.error(exc)
            return False

    @staticmethod
    def fetch_average_movie_rating(movie_id: int) -> Optional[float]:
        """Возвращает средний рейтинг переданного фильма"""
        connection = None

        try:
            connection = psycopg2.connect(
                host=environ["DATABASE_HOST"],
                port=environ["DATABASE_PORT"],
                user=environ["DATABASE_USER"],
                password=environ["DATABASE_PASSWORD"],
                database=environ["DATABASE_NAME"]
            )
            with connection.cursor() as cursor:
                print("[INFO] Connection with PostgreSQL was opened")

                sql_query = """SELECT ROUND(AVG(rs.value), 1)
                FROM "RatingStar" rs
                INNER JOIN "Rating" r ON r.star_id = rs.id
                WHERE r.movie_id = %s;""" % movie_id
                cursor.execute(sql_query)
                record: tuple = cursor.fetchone()
                return record[0]

        except psycopg2.OperationalError as connection_exception:
            message = f"[INFO] Error while working with PostgreSQL. {connection_exception}"
            LOGGER.error(message)
        finally:
            if connection:
                connection.close()
                print("[INFO] Connection with PostgreSQL was closed")


class OtherSourcesRatingRepository(BaseObject):
    model = OtherSourcesRating
