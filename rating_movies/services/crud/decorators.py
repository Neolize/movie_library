import logging
from typing import Optional

from django.db.models import QuerySet


LOGGER = logging.getLogger("json_main_logger")


def base_movie_filter(func: callable) -> callable:
    """Set base filter for "Movie" model queries"""
    def base_movie_filter_wrapper(*args, **kwargs) -> Optional[QuerySet]:
        try:
            query_set = func(*args, **kwargs).filter(draft=False)
        except AttributeError as attr_exc:
            LOGGER.error(attr_exc)
            query_set = None

        return query_set
    return base_movie_filter_wrapper


def base_movie_ordering(func: callable) -> callable:
    """Set base ordering for "Movie" model queries"""
    def base_movie_ordering_wrapper(*args, **kwargs) -> Optional[QuerySet]:
        try:
            query_set = func(*args, **kwargs).order_by("-world_premiere")
        except AttributeError as attr_exc:
            LOGGER.error(attr_exc)
            query_set = None

        return query_set
    return base_movie_ordering_wrapper


def base_actor_director_ordering(func: callable) -> callable:
    """Set base ordering for "Actor" model queries"""
    def base_actor_director_ordering_wrapper(*args, **kwargs) -> Optional[QuerySet]:
        try:
            query_set = func(*args, **kwargs).order_by("name")
        except AttributeError as attr_exc:
            LOGGER.error(attr_exc)
            query_set = None

        return query_set
    return base_actor_director_ordering_wrapper
