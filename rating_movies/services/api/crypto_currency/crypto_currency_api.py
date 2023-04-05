import logging
from os import environ
from dataclasses import dataclass
from datetime import datetime
from typing import final, Optional

import backoff
from requests import Session

from site_engine.settings import load_env
from rating_movies.services.api import api_utils


@dataclass
class CryptoCurrencyData:
    error_message: str
    last_updated: str
    crypto_currencies_list: list[dict]


@final
class CoinMarketCapAPI:
    __slots__ = ("__api_key", "__url", "__convert", "__headers", "__parameters", "__logger")

    def __init__(self, api_key: str, start: str, limit: str, convert: str):
        self.__api_key = api_key
        self.__url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        self.__convert = convert
        self.__set_headers()
        self.__set_parameters(start=start, limit=limit, convert=convert)
        self.__logger = logging.getLogger("json_api_logger")

    def __set_headers(self) -> None:
        self.__headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.__api_key
        }

    def __set_parameters(self, start, limit, convert) -> None:
        self.__parameters = {
            "start": start,
            "limit": limit,
            "convert": convert
        }

    @backoff.on_exception(backoff.expo,
                          api_utils.return_base_requests_exceptions(),
                          max_tries=3)
    def __make_api_call(self) -> Optional[dict]:
        """В случае успешного запроса возвращает ответ от сервера в виде словаря с данными о криптовалюте,
         иначе возвращает None"""
        session = Session()
        session.headers.update(self.__headers)
        try:
            response = session.get(url=self.__url, params=self.__parameters)
            data = response.json()
        except api_utils.return_base_requests_exceptions() as exc:
            self.__logger.error(exc)
            data = None

        return data

    def __get_response_data(self) -> CryptoCurrencyData:
        """Возвращает объект CryptoCurrencyData, содержащий ответ от сервера в разобранном на атрибуты виде"""
        response = self.__make_api_call()
        data_object = CryptoCurrencyData(
            error_message="",
            last_updated=str(datetime.now()),
            crypto_currencies_list=[]
        )

        if _is_error(response):
            self.__logger.error(response)
            data_object.error_message = api_utils.return_error_message()
            return data_object

        data_response = response.get("data")
        try:
            number = 1
            for current_currency in data_response:
                crypto_currency_dict = {
                    "number": number,
                    "name": _fetch_name(current_currency),
                    "symbol": _fetch_symbol(current_currency),
                    "price": api_utils.format_crypto_currency_value(_fetch_price(current_currency, self.__convert)),
                    "percent_change_24h": api_utils.format_crypto_currency_value(
                        _fetch_percent_change_24h(current_currency, self.__convert)
                    ),
                    "percent_change_7d": api_utils.format_crypto_currency_value(
                        _fetch_percent_change_7d(current_currency, self.__convert)
                    ),
                    "percent_change_30d": api_utils.format_crypto_currency_value(
                        _fetch_percent_change_30d(current_currency, self.__convert))
                }
                data_object.crypto_currencies_list.append(crypto_currency_dict)
                number += 1
        except (AttributeError, KeyError, ValueError, TypeError) as exc:
            self.__logger.error(exc)
            data_object.error_message = api_utils.return_error_message()

        return data_object

    def run(self) -> CryptoCurrencyData:
        return self.__get_response_data()


def _fetch_name(currency_data: dict) -> str:
    """Возвращает название криптовалюты"""
    return currency_data["name"]


def _fetch_symbol(currency_data: dict) -> str:
    """Возвращает символ криптовалюты"""
    return currency_data["symbol"]


def _fetch_price(currency_data: dict, convert: str) -> float:
    """Возвращает цену криптовалюты"""
    return currency_data.get("quote").get(convert)["price"]


def _fetch_percent_change_24h(currency_data: dict, convert: str) -> float:
    """Возвращает 24-х часовое изменение цены криптовалюты в процентах"""
    return currency_data.get("quote").get(convert)["percent_change_24h"]


def _fetch_percent_change_7d(currency_data: dict, convert: str) -> float:
    """Возвращает 7-ми дневное изменение цены криптовалюты в процентах"""
    return currency_data.get("quote").get(convert)["percent_change_7d"]


def _fetch_percent_change_30d(currency_data: dict, convert: str) -> float:
    """Возвращает 30-ти дневное изменение цены криптовалюты в процентах"""
    return currency_data.get("quote").get(convert)["percent_change_30d"]


def _is_error(response: dict) -> bool:
    """Проверяет ответ на наличие статуса ошибки"""
    if response.get("statusCode") == 404 or response is None:
        return True

    status = response.get("status")
    if status.get("error_code") == 0:
        return False
    return True


def get_coin_market_cap_data(start: str = "1", limit: str = "100", convert: str = "USD") -> CryptoCurrencyData:
    """Возвращает объект класса CryptoCurrencyData с данными полученными от CoinMarketCap API"""
    load_env()
    try:
        api_key = environ["CoinMarketCap_API_KEY"]
    except KeyError:
        api_key = "default"

    api_instance = CoinMarketCapAPI(api_key=api_key, start=start, limit=limit, convert=convert)
    return api_instance.run()
