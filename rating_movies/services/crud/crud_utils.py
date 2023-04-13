import operator
import logging
import datetime
from random import shuffle
from typing import Union, Optional

from django.core.cache import cache
from django.db.models import QuerySet, Count, Prefetch
from django.core.exceptions import FieldError, FieldDoesNotExist

from rating_movies import exceptions
from rating_movies.models import Genre, Movie
from rating_movies.services.crud import specifications


LOGGER = logging.getLogger("json_main_logger")


class BaseObject:
    """Базовые операции с моделями"""
    model = None

    def is_object_with_same_params(self, specification: specifications.SameObjectSpecification) -> bool:
        return self.model.objects.filter(**specification.is_satisfied()).exists()

    def get_object_by_parameter(self, specification: specifications.ObjectByParameterSpecification) -> Optional[model]:
        try:
            obj = self.model.objects.get(**specification.is_satisfied())
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned, exceptions.AbsentParameterError,
                exceptions.UnavailableParameterError) as exc:
            print(exc)
            obj = None
        return obj

    def get_objects_ordered_by_params(self,
                                      specification: specifications.ObjectsOrderBySpecification) -> Optional[QuerySet]:
        try:
            objects = self.model.objects.order_by(*specification.is_satisfied())
            # берём первый элемент, так как метод возвращает кортеж
        except (FieldError, FieldDoesNotExist, exceptions.AbsentParameterError,
                exceptions.UnavailableParameterError) as exc:
            LOGGER.error(exc)
            objects = None
        return objects

    def get_all_objects(self) -> QuerySet:
        return self.model.objects.all()

    def create_new_object(self, obj: dict) -> Union[bool, model]:
        try:
            new_obj = self.model.objects.create(**obj)
            return new_obj
        except Exception as exc:
            LOGGER.error(exc)
            return False

    @staticmethod
    def delete_obj(obj) -> bool:
        try:
            obj.delete()
            return True
        except Exception as exc:
            LOGGER.error(exc)
            return False

    @staticmethod
    def update_obj(obj) -> bool:
        try:
            obj.save()
            return True
        except Exception as exc:
            LOGGER.error(exc)
            return False


class GenreYear:
    """Genres and years for active movies"""
    @staticmethod
    def get_genres() -> list[Genre]:
        """Return several random chosen genres"""
        genres = cache.get("genres")  # try to fetch genres from cache
        if not genres:
            genres = Genre.objects.prefetch_related(
                Prefetch(
                    "movie_genre",
                    Movie.objects.filter(draft=False).only("pk"),
                    "movies",
                )
            ).annotate(total=Count("movie_genre")).filter(total__gt=0)
            # Transforming QuerySet to list, shuffling it and take first seven items
            genres = list(genres)
            shuffle(genres)
            genres = genres[:7]

            cache.set("genres", genres, 60)

        return genres

    @staticmethod
    def get_years() -> list[dict]:
        """Return several random chosen years"""
        years = cache.get("years")  # try to fetch years from cache
        if not years:
            years = Movie.objects.filter(draft=False).values("year").distinct().order_by("year")
            # Transforming QuerySet to list, shuffling it and take first seven items, then sorting by ascending
            years = list(years)
            shuffle(years)
            years = years[:7]
            years = sorted(years, key=operator.itemgetter("year"))

            cache.set("years", years, 60)

        return years


def calculate_age(birth_date: datetime.date, death_date: datetime.date = None) -> int:
    """Return calculated age by using given birthdate and/or death date."""
    if death_date:
        time_delta = death_date - birth_date
    else:
        time_delta = datetime.date.today() - birth_date

    years = int(time_delta.days / 365)
    return years
