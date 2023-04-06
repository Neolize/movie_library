from django.core.cache import cache

from rating_movies.models import Movie, Actor
from rating_movies.services import cache_variables
from rating_movies.services.crud import repositories


def delete_movie(movie: Movie) -> bool:
    """Удаление фильма"""
    repository = repositories.MovieRepository()
    return repository.delete_obj(obj=movie)


def delete_actor_director(actor_director: Actor) -> bool:
    """Удаление актёра/режиссёра"""
    repository = repositories.ActorDirectorRepository()
    return repository.delete_obj(obj=actor_director)


def reset_cache(key: str) -> None:
    cache_keys = {
        "movie": cache_variables.CACHE_FOR_NEW_MOVIES,
        "user_movie": cache_variables.CACHE_FOR_USER_ADDED_MOVIES,
        "genre": cache_variables.CACHE_FOR_GENRES,
        "year": cache_variables.CACHE_FOR_YEARS,
    }
    if key.lower() == "movie":
        # if a new movie was created or an old movie was updated, then two keys should be deleted: movie and year
        cache.delete_many([cache_keys.get(cache_keys.get("movie")), cache_keys.get("year")])
        return None
    cache.delete(cache_keys.get(key.lower(), cache_variables.CACHE_FOR_NEW_MOVIES))
