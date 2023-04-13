import logging
from typing import Union

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest

from rating_movies import forms
from rating_movies.models import Actor, Movie, UserProfile, MovieShots
from rating_movies.services.crud import repositories
from rating_movies.services.utils import get_client_ip
from rating_movies.services.crud.delete import reset_cache
from rating_movies.services.api.movies import movies_api
from rating_movies.services.crud import custom_validators


LOGGER = logging.getLogger("json_main_logger")

BASE_ERROR_MESSAGE = "An error occurred while adding a new record on the server"


def create_actor_director(form: forms.ActorDirectorForm) -> Union[Actor, bool]:
    """Actor/director creation"""
    repository = repositories.ActorDirectorRepository()
    actor_director_validator = custom_validators.ActorDirectorValidator(form=form, repository=repository, creation=True)

    if actor_director_validator.can_be_saved():
        new_actor_director = repository.create_new_object(obj=form.cleaned_data)
        if new_actor_director:
            return new_actor_director
        form.add_error(None, BASE_ERROR_MESSAGE)
    return False


def create_category(form: forms.CategoryForm) -> bool:
    """Category creation"""
    repository = repositories.CategoryRepository()
    category_validator = custom_validators.CategoryValidator(form=form, repository=repository)

    if category_validator.can_be_saved():
        if repository.create_new_object(obj=form.cleaned_data):
            return True
        form.add_error(None, BASE_ERROR_MESSAGE)
    return False


def create_genre(form: forms.GenreForm) -> bool:
    repository = repositories.GenreRepository()
    genre_validator = custom_validators.GenreValidator(form=form, repository=repository)

    if genre_validator.can_be_saved():
        if repository.create_new_object(obj=form.cleaned_data):
            return True
        form.add_error(None, BASE_ERROR_MESSAGE)
    return False


def create_movie(form: forms.MovieForm) -> Union[Movie, bool]:
    repository = repositories.MovieRepository()
    movie_validator = custom_validators.MovieValidator(form=form, repository=repository, creation=True)

    if movie_validator.can_be_saved():
        new_movie = repository.create_new_object(obj=form.cleaned_data)
        if new_movie:
            title = new_movie.title_en or new_movie.title
            # if attribute "title_en" exists its value will be written to the variable
            # otherwise will be written value from attribute "title"
            create_other_sources_rating(title=title, movie=new_movie)
            # creating new record with movie rating
            return new_movie
        form.add_error(None, BASE_ERROR_MESSAGE)
    return False


def create_movie_shot(form: forms.MovieShotForm) -> Union[MovieShots, bool]:
    repository = repositories.MovieShotRepository()
    movie_shot_validator = custom_validators.MovieShotValidator(form=form, repository=repository)

    if movie_shot_validator.can_be_saved():
        new_movie_shot = repository.create_new_object(obj=form.cleaned_data)
        if new_movie_shot:
            return new_movie_shot
        form.add_error(None, BASE_ERROR_MESSAGE)
    return False


def create_review(form: forms.ReviewForm, request: WSGIRequest, movie: Movie) -> bool:
    """Добавление отзыва"""
    if form.is_valid():
        form = form.save(commit=False)  # приостанавливаем сохранение формы
        parent = request.POST.get("parent")  # parent - имя поля в форме
        if parent:
            form.parent_id = int(parent)
        form.movie = movie
        form.save()
        return True
    form.add_error(None, "The review form was filled out incorrectly")
    return False


def create_rating_star(form: forms.RatingStarForm) -> bool:
    """Добавление звезды рейтинга"""
    if form.is_valid():
        value = form.cleaned_data.get("value")
        if 0 <= value <= 5:
            form.save()
            return True
        form.add_error("value", f"Rating star must be between 0 and 5 but you passed {value}")
    else:
        form.add_error(None, "The rating star form was filled out incorrectly")
    return False


def update_or_create_rating(form: forms.RatingForm, request: WSGIRequest) -> bool:
    """Create or update data in model "Rating" """
    if form.is_valid():
        repository = repositories.RatingRepository()

        movie_id = int(request.POST.get("movie"))
        user_ip = get_client_ip(request=request)
        star_id = int(request.POST.get("star"))

        if repository.update_or_create_rating(ip=user_ip, movie_id=movie_id, star_id=star_id):
            return True
    form.add_error(None, "Rating was marked incorrect")
    return False


def create_other_sources_rating(title: str, movie: Movie) -> None:
    """Get movie rating from IMDb API and create new record in model "OtherSourcesRating" """
    rating_repository = repositories.OtherSourcesRatingRepository()
    movie_rating = movies_api.get_movie_rating(movie_title=title)
    if movie_rating:
        rating_repository.create_new_object(obj={"rating": movie_rating, "movie": movie})


@receiver(post_save, sender=User)
def user_creation(sender, instance, created, **kwargs):
    """Create new record in model "UserProfile" right after new user was created"""
    if created:
        UserProfile.objects.create(user=instance)


def create_user_profile(user_instance: User) -> None:
    """Create new record in model "UserProfile" """
    UserProfile.objects.create(user=user_instance)


def add_movie_to_user_movie_list(user: User, movie: Movie) -> None:
    """Add new movie to user's watchlist"""
    try:
        user.user_profile.movies.add(movie)
        reset_cache("user_movie")
    except User.user_profile.RelatedObjectDoesNotExist as exc:
        LOGGER.error(exc)
        create_user_profile(user_instance=user)
        add_movie_to_user_movie_list(user, movie)
