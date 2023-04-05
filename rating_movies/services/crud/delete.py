from rating_movies.models import Movie, Actor
from rating_movies.services.crud import repositories


def delete_movie(movie: Movie) -> bool:
    """Удаление фильма"""
    repository = repositories.MovieRepository()
    return repository.delete_obj(obj=movie)


def delete_actor_director(actor_director: Actor) -> bool:
    """Удаление актёра/режиссёра"""
    repository = repositories.ActorDirectorRepository()
    return repository.delete_obj(obj=actor_director)
