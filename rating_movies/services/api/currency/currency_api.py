import json
import logging
from json.decoder import JSONDecodeError
from datetime import date, datetime
from dataclasses import dataclass
from typing import final, Optional

import backoff
from requests import get as requests_get
from requests.models import Response

from rating_movies.services.api import api_utils


@dataclass
class CurrencyData:
    error_message: str
    last_updated: str
    currencies_list: list[dict]


@final
class CurrencyAPI:
    __slots__ = ("__date", "__logger")

    def __init__(self, specific_date: Optional[date]):
        self.__date = specific_date
        self.__logger = logging.getLogger("json_api_logger")

    def __form_url(self) -> str:
        """Формирует url для запроса на основе атрибута __date"""
        if self.__date is None or not _check_date(self.__date):
            url = "https://www.cbr-xml-daily.ru/daily_json.js"
        else:
            desired_date = _form_date(self.__date)
            url = "https://www.cbr-xml-daily.ru/archive/%s/daily_json.js" % desired_date

        return url

    @backoff.on_exception(backoff.expo,
                          api_utils.return_base_requests_exceptions(),
                          max_tries=3)
    def __make_call(self) -> Optional[Response]:
        """Возвращает ответ от сервера в виде объекта Response"""
        try:
            response = requests_get(url=self.__form_url())
        except api_utils.return_base_requests_exceptions() as exc:
            self.__logger.error(exc)
            response = None
        return response

    def __get_response_data(self) -> CurrencyData:
        """Возвращает объект CryptoCurrencyData, содержащий ответ от сервера с данными о валюте,
        который разобран на атрибуты"""
        currency_instance = CurrencyData(
            error_message="",
            last_updated=str(datetime.now()),
            currencies_list=[]
        )
        response = self.__make_call()
        if _is_error(response):
            if response.status_code == 404:
                self.__logger.error(response.text)

            currency_instance.error_message = api_utils.return_error_message()
            return currency_instance

        try:
            json_response: dict = json.loads(response.text)
        except JSONDecodeError as exc:
            self.__logger.error(exc)
            currency_instance.error_message = api_utils.return_error_message()
            return currency_instance

        try:
            currencies_dict: dict = json_response.get("Valute")
            for currency in currencies_dict.values():
                currency_instance.currencies_list.append(_generate_currency_dict(currency))
        except (AttributeError, KeyError) as exc:
            self.__logger.error(exc)
            currency_instance.error_message = api_utils.return_error_message()

        return currency_instance

    def run(self):
        return self.__get_response_data()


def _generate_currency_dict(currency: dict) -> dict:
    """Формирует новый словарь на основе переданного."""
    return {
        "NumCode": currency["NumCode"],
        "CharCode": currency["CharCode"],
        "Nominal": currency["Nominal"],
        "Name": currency["Name"],
        "Value": currency["Value"],
        "Previous": currency["Previous"]
    }


def _form_date(date_obj: date) -> str:
    """Приводит объект datetime к виду, необходимому для GET запроса"""
    return str(date_obj).replace("-", "/")


def _check_date(date_obj: date) -> bool:
    """Проверяет, является ли переданная дата объектом datetime.date"""
    return isinstance(date_obj, date)


def _is_error(response: Response) -> bool:
    """Проверяет объект response на наличие статуса ошибки"""
    if response is None or not response.ok:
        return True
    return False


def get_cbr_data(specific_date: Optional[date]) -> CurrencyData:
    """Возвращает объект класса CurrencyData с данными полученными в результате запроса"""
    currency_instance = CurrencyAPI(specific_date)
    return currency_instance.run()
