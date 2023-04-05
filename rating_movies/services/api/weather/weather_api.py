import logging
from os import environ
from datetime import datetime
from dataclasses import dataclass
from typing import final, Optional

import backoff
from requests import get as requests_get

from site_engine.settings import load_env
from rating_movies.services.api import api_utils


@dataclass
class WeatherData:
    error_message: str
    last_updated: str
    current_weather: dict
    weather_forecast: list


def _get_weather_data_object() -> WeatherData:
    return WeatherData(
        error_message="",
        last_updated=str(datetime.now()),
        current_weather={},
        weather_forecast=[],
    )


@final
class YandexWeatherAPI:
    __slots__ = ("__api_key", "__geo_coordinates", "__headers", "__weather_data_object", "__logger")

    def __init__(self, api_key):
        self.__api_key = api_key
        self.__geo_coordinates = api_utils.get_coordinates()
        self.__set_headers()
        self.__weather_data_object = _get_weather_data_object()
        self.__logger = logging.getLogger("json_api_logger")

    def __set_headers(self) -> None:
        self.__headers = {
            "X-Yandex-API-Key": self.__api_key
        }

    @backoff.on_exception(backoff.expo,
                          api_utils.return_base_requests_exceptions(),
                          max_tries=3)
    def __make_api_call(self) -> Optional[dict]:
        """В случае успешного запроса возвращает ответ от сервера в виде словаря с данными о погоде,
         иначе возвращает None"""
        url = "https://api.weather.yandex.ru/v2/informers?lat=%s&lon=%s" % (self.__geo_coordinates.latitude,
                                                                            self.__geo_coordinates.longitude)
        try:
            response = requests_get(url=url, headers=self.__headers)
            data = response.json()
        except api_utils.return_base_requests_exceptions() as exc:
            self.__logger.error(exc)
            data = None

        return data

    def __fill_weather_data_object(self) -> None:
        """Заполняет объект WeatherData данными, полученными от API Yandex weather"""
        response_data = self.__make_api_call()
        _write_current_weather_data_to_object(response_data, self.__weather_data_object, self.__logger,
                                              self.__geo_coordinates.city)
        _write_weather_forecast_data_to_object(response_data, self.__weather_data_object, self.__logger)

    def run(self) -> WeatherData:
        self.__fill_weather_data_object()
        return self.__weather_data_object


def _write_current_weather_data_to_object(data_dict: Optional[dict], weather_data_instance: WeatherData,
                                          logger: logging.Logger, user_city: str) -> None:
    """Записывает в объект WeatherData данные о погоде из полученного словаря"""
    if data_dict is None:
        weather_data_instance.error_message = api_utils.return_error_message()
        return None

    try:
        fact = data_dict.get("fact")
        formed_weather_data = {
            "city": user_city,
            "temp": fact["temp"],
            "feels_like": fact["feels_like"],
            "condition": fact["condition"],
            "pressure": fact["pressure_mm"],
            "humidity": fact["humidity"],
            "wind_speed": fact["wind_speed"],
            "wind_gust": fact["wind_gust"],
            "sunrise": data_dict.get("forecast")["sunrise"],
            "sunset": data_dict.get("forecast")["sunset"],
        }
        weather_data_instance.current_weather = formed_weather_data
    except (AttributeError, KeyError, TypeError) as exc:
        logger.error(exc)
        weather_data_instance.error_message = api_utils.return_error_message()


def _write_weather_forecast_data_to_object(data_dict: Optional[dict], weather_data_instance: WeatherData,
                                           logger: logging.Logger) -> None:
    """Записывает в объект WeatherData данные о прогнозе погоды из полученного словаря"""
    if data_dict is None:
        weather_data_instance.error_message = api_utils.return_error_message()
        return None

    try:
        forecast_parts = data_dict.get("forecast")["parts"]
        formed_forecast_data_list = []

        for data in forecast_parts:
            temp_dict = {
                "part_name": data.get("part_name"),
                "temp": data.get("temp_avg"),
                "feels_like": data.get("feels_like"),
                "condition": data.get("condition"),
            }
            formed_forecast_data_list.append(temp_dict)

        weather_data_instance.weather_forecast = formed_forecast_data_list
    except (AttributeError, KeyError, TypeError) as exc:
        logger.error(exc)
        weather_data_instance.error_message = api_utils.return_error_message()


def get_yandex_weather_data() -> WeatherData:
    """Возвращает объект класса WeatherDAta с данными, полученными от API Yandex weather"""
    load_env()
    try:
        api_key = environ["YandexWeather_API_KEY"]
    except KeyError:
        api_key = "default"

    weather_instance = YandexWeatherAPI(api_key)
    return weather_instance.run()
