import datetime

from rating_movies.models import Actor
from rating_movies.forms import MovieForm, ActorDirectorForm
from rating_movies.services.crud import repositories, crud_utils
from rating_movies.services.crud.create import create_other_sources_rating
from rating_movies.services.crud.read import get_movie_by_parameters, get_other_sources_rating


def update_movie(form: MovieForm) -> bool:
    """Movie update"""
    if form.is_valid():
        repository = repositories.MovieRepository()
        response = repository.update_obj(obj=form)
        if response:
            update_other_sources_rating(movie_cleaned_data=form.cleaned_data)
            return response
    return False


def update_actor_director(form: ActorDirectorForm) -> bool:
    """Actor/director update"""
    if form.is_valid():
        repository = repositories.ActorDirectorRepository()
        return repository.update_obj(obj=form)
    return False


def update_other_sources_rating(movie_cleaned_data: dict) -> None:
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
