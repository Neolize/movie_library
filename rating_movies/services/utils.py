import string
from typing import Optional
from random import choice

from django.core.handlers.wsgi import WSGIRequest
from django.utils.http import url_has_allowed_host_and_scheme
from django.http.request import QueryDict

from rating_movies.models import Movie, get_current_year


def format_budget(budget: int) -> str:
    """Возвращает бюджет в отформатированном виде: 1 000 000"""
    budget = str(budget)
    length = len(budget)
    sections = length % 3

    if sections == 0:
        first_index = 3
    else:
        first_index = sections

    result = budget[:first_index]
    for item in range(first_index, length, 3):
        result += f" {budget[item: item + 3]}"

    return result


def change_movie_fields(instance: Movie) -> None:
    """Изменяет поля (budget, fees_in_usa, fees_in_world) экземпляра модели Movie
       для корректного отображения на странице"""
    instance.budget = format_budget(instance.budget)
    instance.fees_in_usa = format_budget(instance.fees_in_usa)
    instance.fees_in_world = format_budget(instance.fees_in_world)


def get_previous_url(request: WSGIRequest):
    """Возвращает url с которого пришёл пользователь"""
    previous_url = request.META.get("HTTP_REFERER")
    if not url_has_allowed_host_and_scheme(url=previous_url, allowed_hosts=request.get_host()):
        previous_url = "home"
    return previous_url


def get_client_ip(request: WSGIRequest):
    """Возвращает ip пользователя"""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded_for:
        user_ip = forwarded_for.split(",")[0]
    else:
        user_ip = request.META.get("REMOTE_ADDR")
    return user_ip


def convert_years_for_random_movies(years: str) -> Optional[list]:
    """Формирует диапазон годов для запроса к БД"""
    if years == "All years":
        return None
    if years == "After 2020":
        return [2020, get_current_year()]
    return years.split(" - ")


def convert_country_for_random_movies(country):
    if not country:
        return None
    return country[0]


def format_currency_date(currency_date: str) -> str:
    """Принимает дату в формате: 'YYYY-MM-DD' и возвращает её в отформатированном виде: 'DD.MM.YYYY' """
    date_split = currency_date.split("-")
    return f"{date_split[-1]}.{date_split[1]}.{date_split[0]}"


def generate_random_password(request_dict: QueryDict) -> str:
    """Генерирует псевдослучайный пароль на основе переданных параметров"""
    password_length = int(request_dict.get("password_length", 12))

    uppercase = string.ascii_uppercase if request_dict.get("uppercase") else ""
    numbers = string.digits if request_dict.get("numbers") else ""
    special_characters = "!@#$%^&*()-_+=;:,./?\|`~[]{}" if request_dict.get("special characters") else ""

    characters = string.ascii_lowercase + uppercase + numbers + special_characters
    password = ""

    for _ in range(password_length):
        password += choice(characters)

    return password


def _assign_color(rating_number: float) -> str:
    """Assign a color to the passed value"""
    if rating_number >= 75:
        color = "green"
    elif 50 <= rating_number <= 74:
        color = "orange"
    elif 0 < rating_number < 50:
        color = "red"
    else:
        color = "grey"

    return color


def add_class_color_to_movie_rating(movie_rating: Optional[dict]) -> Optional[dict]:
    """Add items for identifying rating color"""
    if movie_rating is None:
        return movie_rating

    imdb_rating = float(movie_rating.get("imDb", 0)) * 10
    metacritic_rating = float(movie_rating.get("metacritic", 0))
    rotten_tomatoes_rating = float(movie_rating.get("rottenTomatoes", 0))

    movie_rating["imDb_color"] = _assign_color(imdb_rating)
    movie_rating["metacritic_color"] = _assign_color(metacritic_rating)
    movie_rating["rottenTomatoes_color"] = _assign_color(rotten_tomatoes_rating)

    return movie_rating
