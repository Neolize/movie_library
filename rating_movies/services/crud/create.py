import logging
from typing import Union

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest

from rating_movies import exceptions
from rating_movies import forms
from rating_movies.models import Actor, Movie, UserProfile
from rating_movies.services.crud import repositories, specifications
from rating_movies.services.utils import get_client_ip
from rating_movies.services.crud.delete import reset_cache
from rating_movies.services.api.movies import movies_api


LOGGER = logging.getLogger("json_main_logger")


class BaseCreation:
    """Базовые методы обработки форм добавления объектов"""
    @staticmethod
    def is_instance_with_same_params(repository, **kwargs) -> bool:
        try:
            result = repository.is_object_with_same_params(
                specification=specifications.SameObjectSpecification(**kwargs))
        except (exceptions.AbsentParameterError, exceptions.UnavailableParameterError) as exc:
            LOGGER.error(exc)
            result = False

        return result

    @staticmethod
    def are_all_fields_in_form(fields, form_cleaned_data):
        if len(form_cleaned_data) != len(fields):
            return False

        for field in fields:
            if field not in form_cleaned_data:
                return False
        return True


class ActorDirectorCreation(BaseCreation):
    """Добавление актёра/режиссёра"""

    def __init__(self, form: forms.ActorDirectorForm):
        self.form = form
        self.__repository = repositories.ActorDirectorRepository()

    def create_actor_director(self) -> Union[bool, Actor]:
        if self.form.is_valid():
            if self.check_all_validators_for_actor_director():
                new_actor_director = self.__repository.create_new_object(obj=self.form.cleaned_data)
                if new_actor_director:
                    return new_actor_director
                self.form.add_error(None, "An error occurred while adding a new record on the server")
        return False

    @staticmethod
    def is_age_valid(age: int) -> bool:
        if 0 <= age < 130:
            return True
        return False

    def check_all_validators_for_actor_director(self) -> bool:
        fields = ("name", "age", "description", "image")
        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.form.cleaned_data):
            self.form.add_error(None, "Mismatch filled fields")
            return False

        age_field = self.form.cleaned_data["age"]
        if not self.is_age_valid(age_field):
            self.form.add_error("age", f"Age must be between 0 and 130, but got: {age_field}")
            return False

        name_field = self.form.cleaned_data["name"]
        if self.is_instance_with_same_params(repository=self.__repository, name=name_field):
            self.form.add_error("name", f"Name \"{name_field}\" already exists")
            return False
        return True


class CategoryCreation(BaseCreation):
    """Добавление категории"""

    def __init__(self, form: forms.CategoryForm):
        self.form = form
        self.__repository = repositories.CategoryRepository()

    def create_category(self) -> bool:
        if self.form.is_valid():
            if self.check_all_validators_for_category():
                if self.__repository.create_new_object(obj=self.form.cleaned_data):
                    return True
                self.form.add_error(None, "An error occurred while adding a new record on the server")
        return False

    def check_all_validators_for_category(self) -> bool:
        fields = ("name", "description", "url")

        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.form.cleaned_data):
            self.form.add_error(None, "Mismatch filled fields")
            return False

        if self.is_instance_with_same_params(repository=self.__repository, name=self.form.cleaned_data["name"]):
            self.form.add_error("name", f"Name \"{self.form.cleaned_data['name']}\" already exists")
            return False

        if self.is_instance_with_same_params(repository=self.__repository, url=self.form.cleaned_data["url"]):
            self.form.add_error("url", f"Url \"{self.form.cleaned_data['url']}\" already exists")
            return False
        return True


class GenreCreation(BaseCreation):
    """Добавление жанра"""

    def __init__(self, form: forms.GenreForm):
        self.form = form
        self.__repository = repositories.GenreRepository()

    def create_genre(self) -> bool:
        if self.form.is_valid():
            if self.check_all_validators_for_genre():
                if self.__repository.create_new_object(obj=self.form.cleaned_data):
                    return True
                self.form.add_error(None, "An error occurred while adding a new record on the server")
        return False

    def check_all_validators_for_genre(self) -> bool:
        fields = ("name", "description", "url")

        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.form.cleaned_data):
            self.form.add_error(None, "Mismatch filled fields")
            return False

        if self.is_instance_with_same_params(repository=self.__repository, name=self.form.cleaned_data["name"]):
            self.form.add_error("name", f"Name \"{self.form.cleaned_data['name']}\" already exists")
            return False

        if self.is_instance_with_same_params(repository=self.__repository, url=self.form.cleaned_data["url"]):
            self.form.add_error("url", f"Url \"{self.form.cleaned_data['url']}\" already exists")
            return False
        return True


class MovieCreation(BaseCreation):
    """Добавление фильма"""

    def __init__(self, form: forms.MovieForm):
        self.form = form
        self.__movie_repository = repositories.MovieRepository()

    def create_movie(self) -> Union[bool, Movie]:
        if self.form.is_valid():
            if self.check_all_validators_for_movie():
                new_movie = self.__movie_repository.create_new_object(obj=self.form.cleaned_data)
                if new_movie:
                    title = new_movie.title_en or new_movie.title
                    # if attribute "title_en" exists its value will be written to the variable
                    # otherwise will be written value from attribute "title"
                    create_other_sources_rating(title=title, movie=new_movie)
                    # creating new record with movie rating
                    return new_movie
                self.form.add_error(None, "An error occurred while adding a new record on the server")
        return False

    def add_year(self) -> None:
        """Добавляем поле year на основе поля world_premiere в словарь cleaned_data.
        Данная функция должна вызываться перед are_all_fields_movie_in_form"""
        year: int = self.form.cleaned_data["world_premiere"].year
        self.form.cleaned_data["year"] = year

    def check_all_validators_for_movie(self) -> bool:
        fields = ("title", "tagline", "description", "poster", "country",
                  "directors", "actors", "genres", "world_premiere", "budget",
                  "fees_in_usa", "fees_in_world", "category", "draft")

        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.form.cleaned_data):
            self.form.add_error(None, "Mismatch filled fields")
            return False
        self.add_year()   # если присутствует поле "world_premiere", то можно добавить поле "year"

        title_field = self.form.cleaned_data["title"]
        year_field = self.form.cleaned_data["year"]
        if self.is_instance_with_same_params(repository=self.__movie_repository,
                                             title=title_field,
                                             year=year_field):
            self.form.add_error("title",
                                f"Movie with title: \"{title_field}\" and year: \"{year_field}\" already exists")
            return False
        return True


class MovieShotCreation(BaseCreation):
    """Добавление кадров из фильма"""

    def __init__(self, form: forms.MovieShotForm):
        self.form = form
        self.__repository = repositories.MovieShotRepository()

    def create_movie_shot(self) -> bool:
        if self.form.is_valid():
            if self.check_all_validators_for_movie_shots():
                new_movie_shot = self.__repository.create_new_object(obj=self.form.cleaned_data)
                if new_movie_shot:
                    return new_movie_shot
                self.form.add_error(None, "An error occurred while adding a new record on the server")
        return False

    def check_all_validators_for_movie_shots(self) -> bool:
        fields = ("title", "description", "image", "movie")
        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.form.cleaned_data):
            self.form.add_error(None, "Mismatch filled fields")
            return False
        return True


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
