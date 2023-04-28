import datetime

from rating_movies.models import Actor
from rating_movies.forms import MovieForm, ActorDirectorForm
from rating_movies.services.crud import repositories, crud_utils, custom_validators
from rating_movies.services.crud.create import create_other_sources_rating
from rating_movies.services.crud.read import get_movie_by_parameters, get_other_sources_rating


def update_movie(form: MovieForm) -> bool:
    """Movie update"""
    repository = repositories.MovieRepository()
    movie_validator = custom_validators.MovieValidator(form=form, repository=repository)

    if movie_validator.can_be_saved():
        is_updated: bool = repository.update_obj(obj=form)
        if is_updated:
            update_movie_other_sources_rating(movie_cleaned_data=form.cleaned_data)
            return True
    return False


def update_actor_director(form: ActorDirectorForm) -> bool:
    """Actor/director update"""
    repository = repositories.ActorDirectorRepository()
    actor_director_validator = custom_validators.ActorDirectorValidator(form=form, repository=repository)

    if actor_director_validator.can_be_saved():
        return repository.update_obj(obj=form)
    return False


def update_movie_other_sources_rating(movie_cleaned_data: dict) -> None:
    """Other sources rating update"""
    title = movie_cleaned_data.get("title", "")
    world_premiere = movie_cleaned_data.get("world_premiere", datetime.date.today())
    movie_object = get_movie_by_parameters(title=title, world_premiere=world_premiere)

    if movie_object:
        if not get_other_sources_rating(movie=movie_object):
            create_other_sources_rating(title=title, movie=movie_object)


def update_actor_director_age(actor_director: Actor) -> None:
    """Update actor/directors age"""
    repository = repositories.ActorDirectorRepository()
    current_age = crud_utils.calculate_age(birth_date=actor_director.birth_date, death_date=actor_director.death_date)
    actor_director.age = current_age
    repository.update_obj(actor_director)
