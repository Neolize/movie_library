import logging
from typing import Optional, Union
from random import choice, shuffle

from django import forms
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User
from django.db.models import F, QuerySet, Prefetch, ObjectDoesNotExist

from rating_movies import models
from rating_movies.services.crud import repositories, specifications
from rating_movies.services.utils import get_client_ip, convert_years_for_random_movies,\
    convert_country_for_random_movies


LOGGER = logging.getLogger("json_main_logger")


def get_all_categories_ordered_by_parameter(parameter: str) -> QuerySet[models.Category]:
    """Return all categories ordered by given parameter"""
    repository = repositories.CategoryRepository()
    return repository.get_objects_ordered_by_params(
        specification=specifications.ObjectsOrderBySpecification(parameter)
    )


def get_all_movies_ordered_by_parameter(parameter: str) -> QuerySet[models.Movie]:
    """Return all movies ordered by given parameter"""
    repository = repositories.MovieRepository()
    return repository.get_all_objects_ordered_by_parameter(
        specification=specifications.ObjectsOrderBySpecification(parameter)
    )


def get_non_empty_categories() -> QuerySet[models.Category]:
    """Возвращает все категории, на которые ссылается хотя бы одна запись из таблицы Movie"""
    repository = repositories.CategoryRepository()
    return repository.get_non_empty_objects()


def get_movie_by_parameters(**kwargs) -> models.Movie:
    repository = repositories.MovieRepository()
    return repository.get_object_by_parameter(
        specification=specifications.ObjectByParameterSpecification(**kwargs)
    )


def get_all_actors_directors_ordered_by_parameter(parameter: str) -> QuerySet[models.Actor]:
    """Return all actors and directors ordered by given parameter"""
    repository = repositories.ActorDirectorRepository()
    return repository.get_objects_ordered_by_params(
        specification=specifications.ObjectsOrderBySpecification(parameter)
    )


def get_all_genres_ordered_by_parameter(parameter: str) -> QuerySet[models.Genre]:
    """Return all genres ordered by given parameter"""
    repository = repositories.GenreRepository()
    return repository.get_objects_ordered_by_params(
        specification=specifications.ObjectsOrderBySpecification(parameter)
    )


def get_actor_director_by_parameters(**kwargs) -> models.Actor:
    """Возвращает актёра/режиссёра по переданному слагу"""
    repository = repositories.ActorDirectorRepository()
    return repository.get_object_by_parameter(
        specification=specifications.ObjectByParameterSpecification(**kwargs)
    )


def get_related_objects_to_category(category_url: str) -> QuerySet[models.Movie]:
    """Получает url категории и возвращает связанные с этим url'ом фильмы"""
    return models.Movie.objects.filter(category__url=category_url, draft=False)


def get_most_recently_added_movies(number: int = 5) -> QuerySet[models.Movie]:
    """Возвращает пять последних добавленных фильмов"""
    repository = repositories.MovieRepository()
    movies = cache.get("most_recently_added_movies")

    if not movies:
        movies = repository.get_most_recently_added_objects(number)
        cache.set("most_recently_added_movies", movies, 60)

    return movies


def get_filtered_movies(years: list, genres: list) -> QuerySet[dict]:
    """Возвращает список фильмов отфильтрованных по году выхода и/или по жанру"""
    repository = repositories.MovieRepository()

    if years and genres:  # в обоих полях установленно значение
        if years[0] == "0" and genres[0] == "0":  # оба поля формы пусты => показать все фильмы
            return repository.get_all_filtered_objects()
        return repository.get_objects_filtered_by_combined_fields(years=years, genres=genres)

    return repository.get_objects_filtered_by_years_genres(years=years, genres=genres)


def get_sorted_movies(sorting_order="descending", **kwargs) -> Union[QuerySet[dict], list[dict]]:
    sorting = kwargs.get("sorting")
    if sorting == "1":
        return get_movies_sorted_by_rating(sorting_order)
    elif sorting == "4":
        return get_movies_sorted_by_random()

    pattern_sorting = {
        "2": "world_premiere" if sorting_order == "ascending" else "-world_premiere",
        "3": "title" if sorting_order == "ascending" else "-title",
        "5": "id" if sorting_order == "ascending" else "-id",
    }
    sorting_parameter = pattern_sorting.get(sorting)
    repository = repositories.MovieRepository()
    return repository.get_sorted_objects_by_parameter(sorting_parameter)


def get_movies_sorted_by_random() -> list[dict]:
    movies = list(models.Movie.objects.filter(draft=False).values("url", "title", "poster", "tagline"))
    shuffle(movies)
    return movies


def get_movies_sorted_by_rating(sorting_order) -> QuerySet[dict]:
    sorting_order_statement = "rating__imDb" if sorting_order == "ascending" else "-rating__imDb"
    repository = repositories.OtherSourcesRatingRepository()
    sorted_movies = repository.get_all_objects().order_by(sorting_order_statement).values(
        url=F("movie__url"),
        title=F("movie__title"),
        poster=F("movie__poster"),
        tagline=F("movie__tagline")
    )
    return sorted_movies


def get_all_rating_stars() -> QuerySet[models.RatingStar]:
    """Возвращает все звёзды рейтинга"""
    repository = repositories.RatingStarRepository()
    return repository.get_all_objects()


def get_movie_rating(request: WSGIRequest, movie_id: int) -> Optional[int]:
    """Возвращает рейтинг, который установил пользователь для данного фильма"""
    repository = repositories.RatingRepository()
    user_ip = get_client_ip(request=request)
    return repository.get_rating(ip=user_ip, movie_id=movie_id)


def fetch_average_movie_rating(movie_id: int) -> Optional[float]:
    """Возвращает средний рейтинг для переданного фильма"""
    repository = repositories.RatingRepository()
    return repository.fetch_average_movie_rating(movie_id=movie_id)


def fetch_sought_elements(search_element: str, parameter: str) -> Union[QuerySet[models.Movie], QuerySet[models.Actor]]:
    search_elements = {
        "movies": search_movies,
        "actors/directors": search_actors_directors,
    }
    return search_elements.get(search_element.lower(), search_movies)(parameter)


def search_actors_directors(parameter: str) -> QuerySet[models.Actor]:
    """Return actor/director list by given parameter"""
    repository = repositories.ActorDirectorRepository()
    actors_directors = repository.search_objects_by_name(name=parameter)
    if not actors_directors:
        actors_directors = repository.search_objects_by_description(description=parameter)

    return actors_directors


def search_movies(parameter: str) -> QuerySet[models.Movie]:
    """Return movie list by given parameter"""
    repository = repositories.MovieRepository()
    movies = repository.search_objects_by_title(title=parameter)
    if not movies:
        movies = repository.search_objects_by_description(description=parameter)

    return movies


def get_unique_countries() -> list[tuple[str, str]]:
    """Возвращает список кортежей, сформированный из MultilingualQuerySet, которые состоят из названий стран"""
    repository = repositories.MovieRepository()
    return [(country.get("country"), country.get("country")) for country in repository.get_unique_params_dicts(
        specification=specifications.UniqueValuesSpecification("country")
    )]


def get_random_movies_from_form(form: forms.Form) -> Union[bool, QuerySet]:
    """Возвращает список псевдослучайных фильмов на основе переданных через форму данных"""
    if not form.is_valid():
        return False

    movies_number = form.cleaned_data.get("movies_number")  # количество фильмов всегда будет больше нуля
    genres = form.cleaned_data.get("genres")
    countries = convert_country_for_random_movies(form.cleaned_data.get("countries"))
    years = convert_years_for_random_movies(form.cleaned_data.get("years"))

    if not countries:
        countries = models.Movie.objects.values("country").distinct()

    if not genres:
        genres = models.Genre.objects.all().distinct()

    if not years:
        years = list(models.Movie.objects.values_list("year").distinct().order_by("year"))
        years = [years[0][0], years[-1][0]]  # список, содержащий минимальный и максимальный годы выхода фильмов

    filtered_movies_pk = models.Movie.objects.filter(
        genres__in=genres, country__in=countries, year__range=years, draft=False
    ).values("pk").distinct().order_by("pk")

    random_movies = get_random_movies(movies_pk=list(filtered_movies_pk), movies_number=movies_number)
    return random_movies


def get_random_movies(movies_pk: list[dict] = None, movies_number: int = 3) -> QuerySet:
    """Возвращает список псевдослучайных фильмов"""
    random_pk_list = []

    if not movies_pk:
        repository = repositories.MovieRepository()
        movies_pk = list(repository.get_all_available_pk())

    for _ in range(movies_number):
        if not movies_pk:
            break
        chosen_pk = choice(movies_pk)
        random_pk_list.append(chosen_pk.get("pk"))
        movies_pk.remove(chosen_pk)

    random_movies = models.Movie.objects.filter(pk__in=random_pk_list)
    return random_movies


def get_count_movies():
    """Возвращает количество фильмов"""
    repository = repositories.MovieRepository()
    return repository.get_count_movies()


def get_genre_movies(genre_slug: str) -> list[models.Movie]:
    """Возвращает фильмы по заданному жанру"""
    try:
        movies = models.Genre.objects.prefetch_related(
            Prefetch(
                "movie_genre",
                models.Movie.objects.filter(draft=False),
                "movies"
            )
        ).get(url__iexact=genre_slug).movies
    except ObjectDoesNotExist as exc:
        LOGGER.error(exc)
        movies = []

    return movies


def get_other_sources_rating(movie: models.Movie) -> Optional[dict]:
    """Get movie rating from model "OtherSourcesRating" and return it as dict"""
    repository = repositories.OtherSourcesRatingRepository()
    rating_object: models.OtherSourcesRating = repository.get_object_by_parameter(
        specification=specifications.ObjectByParameterSpecification(movie=movie)
    )
    if rating_object:
        return rating_object.rating
    return None


def get_movie_reviews(movie: models.Movie) -> QuerySet[models.Review]:
    """Get movie object and return all reviews which are related to this movie"""
    reviews = models.Review.objects.prefetch_related(
        Prefetch(
            "review_parent",
            models.Review.objects.filter(movie_id=movie.pk, parent_id__isnull=False),
            "child_reviews"
        )
    ).filter(movie_id=movie.pk, parent_id__isnull=True)

    return reviews


def get_all_user_movies(user: User) -> QuerySet[models.Movie]:
    """Return all movies that were added by user earlier"""
    try:
        user_movies = user.user_profile.movies.order_by("-world_premiere")

    except User.user_profile.RelatedObjectDoesNotExist as exc:
        from rating_movies.services.crud.create import create_user_profile
        LOGGER.error(exc)
        create_user_profile(user_instance=user)
        user_movies = get_all_user_movies(user)

    return user_movies


def get_most_recently_added_user_movies(user: User, number: int = 5) -> list:
    """Return last movies added by user. Amount of items is given as a parameter in the definition of the function"""
    movies = cache.get("last_added_user_movies")

    if not movies:
        movies = []
        try:
            user_profile_items = user.user_profile.user_profile_movie. \
                select_related("movie").order_by("-added")[:number]

            for item in user_profile_items:
                movies.append(item.movie)

        except User.user_profile.RelatedObjectDoesNotExist as exc:
            LOGGER.error(exc)

        else:
            cache.set("last_added_user_movies", movies, 60)

    return movies


def is_movie_in_user_watchlist(movie: models.Movie, user: User) -> bool:
    """Check existence the given movie in user's watchlist"""
    if user.is_anonymous:
        return False

    try:
        is_movie = user.user_profile.movies.all().contains(movie)

    except (User.user_profile.RelatedObjectDoesNotExist, AttributeError) as exc:
        from rating_movies.services.crud.create import create_user_profile
        LOGGER.error(exc)
        create_user_profile(user_instance=user)
        is_movie = is_movie_in_user_watchlist(movie, user)

    return is_movie


def get_all_reviews() -> QuerySet[models.Review]:
    repository = repositories.ReviewRepository()
    return repository.get_all_objects()
