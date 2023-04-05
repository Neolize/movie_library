from django import template
from django.contrib.auth.models import User

from rating_movies.services.crud import read

register = template.Library()


@register.simple_tag()
def get_categories():
    """Вывод всех непустых категорий в header"""
    return read.get_non_empty_categories()


@register.inclusion_tag("rating_movies/tags/last_movies.html")
def get_last_movies():
    """Вывод последних добавленных фильмов"""
    movies = read.get_most_recently_added_movies()
    return {"last_movies": movies}


@register.inclusion_tag("rating_movies/tags/last_movies.html")
def get_last_added_user_movies(user: User):
    """Return last movies added by user. If user doesn't have any movies, then return common last added movies"""
    movies = read.get_most_recently_added_user_movies(user)
    my_movies = True

    if not movies:
        movies = read.get_most_recently_added_movies()
        my_movies = False

    return {"last_movies": movies, "my_movies": my_movies}
