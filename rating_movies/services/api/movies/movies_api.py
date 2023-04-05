import logging
from os import environ
from typing import final, Optional

import backoff
from requests import get as requests_get

from site_engine.settings import load_env
from rating_movies.services.api import api_utils


@final
class IMDbAPI:
    __slots__ = ("__api_key", "__lang", "__logger", "__movie_title")

    def __init__(self, api_key, movie_title, lang=None):
        self.__api_key = api_key
        self.__movie_title = movie_title
        self.__lang = "en" if not lang else lang
        self.__logger = logging.getLogger("json_api_logger")

    @backoff.on_exception(backoff.expo,
                          api_utils.return_base_requests_exceptions(),
                          max_tries=3)
    def __get_movie_json_data(self, movie_title: str) -> Optional[dict]:
        """В случае успешного запроса возвращает ответ от сервера в виде словаря с данными о фильме,
         иначе возвращает None"""
        url = "https://imdb-api.com/%s/API/SearchMovie/%s/%s" % (self.__lang, self.__api_key, movie_title)
        try:
            response = requests_get(url=url)
            data = response.json()
        except api_utils.return_base_requests_exceptions() as exc:
            self.__logger.error(exc)
            data = None

        return data

    @backoff.on_exception(backoff.expo,
                          api_utils.return_base_requests_exceptions(),
                          max_tries=3)
    def __get_movie_json_rating(self) -> Optional[dict]:
        """В случае успешного запроса возвращает ответ от сервера в виде словаря с рейтингом фильма,
        иначе возвращает None"""
        movie_id = self.__fetch_movie_id_from_json()

        if movie_id is None:
            return None

        url = "https://imdb-api.com/%s/API/Ratings/%s/%s" % (self.__lang, self.__api_key, movie_id)
        try:
            response = requests_get(url=url)
            data = response.json()
        except api_utils.return_base_requests_exceptions() as exc:
            self.__logger.error(exc)
            data = None

        return data

    def __fetch_movie_id_from_json(self) -> Optional[str]:
        """Достаёт из данных, полученных от сервера, id фильма"""
        json_data = self.__get_movie_json_data(movie_title=self.__movie_title)

        if json_data is None:
            return None

        try:
            movie_id = json_data.get("results")[0]["id"]
        except (KeyError, TypeError) as exc:
            self.__logger.error(exc)
            movie_id = None

        return movie_id

    def run(self) -> Optional[dict]:
        return self.__get_movie_json_rating()


def get_movie_rating(movie_title: str) -> Optional[dict]:
    """Возвращает словарь с рейтингом переданного фильма"""
    load_env()
    try:
        api_key = environ["IMDb_API_KEY"]
    except KeyError:
        api_key = "default"

    movies_instance = IMDbAPI(api_key=api_key, movie_title=movie_title)
    movie_rating = movies_instance.run()

    try:
        cleaned_movie_rating = _clean_movie_rating(movie_rating)
    except (KeyError, TypeError) as exc:
        print(exc)
        cleaned_movie_rating = None

    return cleaned_movie_rating


def _clean_movie_rating(movie_rating: Optional[dict]) -> Optional[dict]:
    """Return movie ratings dictionary only with needed data"""
    if movie_rating is None:
        return movie_rating

    return {
        "imDb": movie_rating.get("imDb", 0),
        "metacritic": movie_rating.get("metacritic", 0),
        "rottenTomatoes": movie_rating.get("rottenTomatoes", 0),
    }
