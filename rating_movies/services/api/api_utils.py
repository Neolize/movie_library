import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from requests import get as requests_get
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects, MissingSchema
from geopy.geocoders import Nominatim
from geopy.location import Location

from site_engine.settings import BASE_DIR
from rating_movies.exceptions import ConversionStringError


def format_crypto_currency_value(price: float) -> str:
    """Возвращает цену/процент колебания криптовалюты в отформатированном виде"""
    price = str(price).replace(",", ".")
    formatted_price = str(round(float(price), 2))
    price_to_the_point = formatted_price.split(".")[0]
    price_after_the_point = formatted_price.split(".")[1]

    if len(price_after_the_point) == 1:
        formatted_price = f"{formatted_price}0"

    length_to_the_point = len(price_to_the_point)
    if length_to_the_point < 4:
        return formatted_price

    sections = length_to_the_point % 3
    if sections == 0:
        first_index = 3
    else:
        first_index = sections

    formatted_price = price_to_the_point[:first_index]
    for number in range(first_index, length_to_the_point, 3):
        formatted_price += f",{price_to_the_point[number: number + 3]}"

    return f"{formatted_price}.{price_after_the_point}"


def return_error_message() -> str:
    return "An error occurred while receiving new data. Try refreshing the page in a minute."


def do_need_update(last_updated: str, interval: int) -> bool:
    """Проверяет актуальность переданной даты в виде строки.
    Дата считается актуальной, если с момента её последнего обновления прошло менее interval минут"""
    try:
        datetime_last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        raise ConversionStringError(last_updated)

    now = datetime.now()
    time_difference = now - datetime_last_updated

    if time_difference.days > 0 or time_difference.seconds >= interval * 60:
        return True
    return False


def is_dir_for_json_files(dir_name: str = None) -> bool:
    if dir_name is None:
        dir_name = "json_files"

    dir_path = os.path.join(BASE_DIR, "rating_movies", dir_name)
    return os.path.isdir(dir_path)


def create_dir_for_json_files(dir_name: str = None) -> None:
    if dir_name is None:
        dir_name = "json_files"

    dir_path = os.path.join(BASE_DIR, "rating_movies", dir_name)
    if not os.path.isdir(dir_path):
        os.mkdir(path=dir_path)


@dataclass
class Coordinates:
    latitude: float
    longitude: float
    city: str


def _get_geolocation(user_agent: str, place: str) -> Optional[Location]:
    try:
        location = Nominatim(user_agent=user_agent).geocode(place)
    except Exception as exc:
        print(exc)
        location = None

    return location


def get_coordinates(place: str = None) -> Coordinates:
    """Возвращает координаты моего местонахождения"""
    user_agent = "user"
    base_latitude = 55.7833
    base_longitude = 42.0833
    city = "Penza"
    # Координаты Пензы

    if place is None:
        place = _get_my_geolocation()

    geolocation = _get_geolocation(user_agent=user_agent, place=place)

    if geolocation is None:
        user_coordinates = Coordinates(latitude=base_latitude, longitude=base_longitude, city=city)
    else:
        user_coordinates = Coordinates(latitude=geolocation.latitude, longitude=geolocation.longitude,
                                       city=place.split()[0])

    return user_coordinates


def _get_my_geolocation() -> str:
    """Возвращает город, в котором я нахожусь"""
    url = "http://ipinfo.io/json"
    try:
        response = requests_get(url)
        data = response.json()
    except Exception as exc:
        print(exc)
        data = {}

    return data.get("region", "Penza")


def return_base_requests_exceptions() -> tuple:
    return ConnectionError, Timeout, TooManyRedirects, MissingSchema
