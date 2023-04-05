from datetime import date as datetime_date

from rating_movies.services.api.currency.currency_json_recording import get_read_data
from rating_movies.services.api.currency.currency_api import CurrencyData


def get_currency_data(date: str = None) -> CurrencyData:
    if date is not None:
        date = _convert_date(date)
    return get_read_data(date)


def _convert_date(date: str) -> datetime_date:
    """Принимает дату в формате: 'YYYY-MM-DD' и возвращает объект datetime.date с этой датой"""
    date_split = list(map(int, date.split("-")))
    return datetime_date(year=date_split[0], month=date_split[1], day=date_split[-1])
