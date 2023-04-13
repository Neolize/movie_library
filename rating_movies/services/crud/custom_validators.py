import logging

from rating_movies import exceptions
from rating_movies import forms
from rating_movies.services.crud import repositories, specifications, crud_utils


LOGGER = logging.getLogger("json_main_logger")


class BaseValidator:
    """Base validator methods"""

    __slots__ = ()

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


class ActorDirectorValidator(BaseValidator):

    __slots__ = ("__form", "__repository", "__creation")

    def __init__(self, form: forms.ActorDirectorForm, repository: repositories.ActorDirectorRepository,
                 creation: bool = False):
        self.__form = form
        self.__repository = repository
        self.__creation = creation

    def can_be_saved(self) -> bool:
        if self.__form.is_valid():
            if self.__check_all_validators_for_actor_director():
                return True
        return False

    @staticmethod
    def __is_age_valid(age: int) -> bool:
        return 0 <= age <= 130

    def __check_all_validators_for_actor_director(self) -> bool:
        fields = ("name", "birth_date", "death_date", "description", "image")
        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.__form.cleaned_data):
            self.__form.add_error(None, "Mismatch filled fields")
            return False

        age = crud_utils.calculate_age(self.__form.cleaned_data["birth_date"], self.__form.cleaned_data["death_date"])
        if not self.__is_age_valid(age):
            self.__form.add_error("birth_date", f"Age must be between 0 and 130, but got: {age}")
            return False

        if self.__creation:
            name_field = self.__form.cleaned_data["name"]
            if self.is_instance_with_same_params(repository=self.__repository, name=name_field):
                self.__form.add_error("name", f"Name \"{name_field}\" already exists")
                return False
        return True


class CategoryValidator(BaseValidator):

    __slots__ = ("__form", "__repository")

    def __init__(self, form: forms.CategoryForm, repository: repositories.CategoryRepository):
        self.__form = form
        self.__repository = repository

    def can_be_saved(self) -> bool:
        if self.__form.is_valid():
            if self.__check_all_validators_for_category():
                return True
        return False

    def __check_all_validators_for_category(self) -> bool:
        fields = ("name", "description", "url")

        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.__form.cleaned_data):
            self.__form.add_error(None, "Mismatch filled fields")
            return False

        if self.is_instance_with_same_params(repository=self.__repository, name=self.__form.cleaned_data["name"]):
            self.__form.add_error("name", f"Name \"{self.__form.cleaned_data['name']}\" already exists")
            return False

        if self.is_instance_with_same_params(repository=self.__repository, url=self.__form.cleaned_data["url"]):
            self.__form.add_error("url", f"Url \"{self.__form.cleaned_data['url']}\" already exists")
            return False
        return True


class GenreValidator(BaseValidator):

    __slots__ = ("__form", "__repository")

    def __init__(self, form: forms.GenreForm, repository: repositories.GenreRepository):
        self.__form = form
        self.__repository = repository

    def can_be_saved(self) -> bool:
        if self.__form.is_valid():
            if self.__check_all_validators_for_genre():
                return True
        return False

    def __check_all_validators_for_genre(self) -> bool:
        fields = ("name", "description", "url")

        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.__form.cleaned_data):
            self.__form.add_error(None, "Mismatch filled fields")
            return False

        if self.is_instance_with_same_params(repository=self.__repository, name=self.__form.cleaned_data["name"]):
            self.__form.add_error("name", f"Name \"{self.__form.cleaned_data['name']}\" already exists")
            return False

        if self.is_instance_with_same_params(repository=self.__repository, url=self.__form.cleaned_data["url"]):
            self.__form.add_error("url", f"Url \"{self.__form.cleaned_data['url']}\" already exists")
            return False
        return True


class MovieValidator(BaseValidator):

    __slots__ = ("__form", "__repository", "__creation")

    def __init__(self, form: forms.MovieForm, repository: repositories.MovieRepository, creation: bool = False):
        self.__form = form
        self.__repository = repository
        self.__creation = creation

    def can_be_saved(self) -> bool:
        if self.__form.is_valid():
            if self.__check_all_validators_for_movie():
                return True
        return False

    def __add_year(self) -> None:
        """Добавляем поле year на основе поля world_premiere в словарь cleaned_data.
        Данная функция должна вызываться перед are_all_fields_movie_in_form"""
        year: int = self.__form.cleaned_data["world_premiere"].year
        self.__form.cleaned_data["year"] = year

    def __check_all_validators_for_movie(self) -> bool:
        fields = ("title", "tagline", "description", "poster", "country",
                  "directors", "actors", "genres", "world_premiere", "budget",
                  "fees_in_usa", "fees_in_world", "category", "draft")

        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.__form.cleaned_data):
            self.__form.add_error(None, "Mismatch filled fields")
            return False
        self.__add_year()   # если присутствует поле "world_premiere", то можно добавить поле "year"

        if self.__creation:
            title_field = self.__form.cleaned_data["title"]
            year_field = self.__form.cleaned_data["year"]
            if self.is_instance_with_same_params(repository=self.__repository,
                                                 title=title_field,
                                                 year=year_field):
                self.__form.add_error("title",
                                      f"Movie with title: \"{title_field}\" and year: \"{year_field}\" already exists")
                return False
        return True


class MovieShotValidator(BaseValidator):

    __slots__ = ("__form", "__repository")

    def __init__(self, form: forms.MovieShotForm, repository: repositories.MovieShotRepository):
        self.__form = form
        self.__repository = repository

    def can_be_saved(self) -> bool:
        if self.__form.is_valid():
            if self.__check_all_validators_for_movie_shots():
                return True
        return False

    def __check_all_validators_for_movie_shots(self) -> bool:
        fields = ("title", "description", "image", "movie")
        if not self.are_all_fields_in_form(fields=fields, form_cleaned_data=self.__form.cleaned_data):
            self.__form.add_error(None, "Mismatch filled fields")
            return False
        return True
