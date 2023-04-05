import json
import os
import logging
from datetime import date
from typing import Optional

from site_engine.settings import BASE_DIR
from rating_movies.exceptions import WriteToFileError, ReadFileError, ConversionStringError
from rating_movies.services.api.api_utils import do_need_update, create_dir_for_json_files, is_dir_for_json_files,\
    get_folder_name_for_json_files
from rating_movies.services.api.currency.currency_api import get_cbr_data, CurrencyData


LOGGER = logging.getLogger("json_api_logger")


def _get_data_for_recording(specific_date: date = None) -> dict:
    """Возвращает словарь с данными для записи в файл.
    При наличии сообщения об ошибке запишет в 'currencies_list' старые данные."""
    data_for_recording = get_cbr_data(specific_date)

    if not data_for_recording.error_message:
        currencies_list = data_for_recording.currencies_list
    else:
        currencies_list = _get_old_currencies_list()

    return {
        "error_message": data_for_recording.error_message,
        "last_updated": data_for_recording.last_updated,
        "currencies_list": currencies_list
    }


def _get_old_currencies_list() -> list:
    """Возвращает старые данные из файла."""
    try:
        old_data = _read_currency_data()
        currencies_list = old_data.get("currencies_list")
    except (ReadFileError, FileNotFoundError) as exc:
        LOGGER.error(exc)
        currencies_list = []

    return currencies_list


def _form_full_path(file_name: str = None) -> str:
    """Формирует полный путь до передаваемого файла.
    Если имя файла не было передано, оно устанавливается в базовое значение"""
    if file_name is None:
        file_name = "cbr_data.json"

    return BASE_DIR / "rating_movies" / get_folder_name_for_json_files() / file_name


def _write_currency_data(specific_date: Optional[date]) -> None:
    """Записывает данные в файл с расширением .json"""
    full_path = _form_full_path()
    currency_data = _get_data_for_recording(specific_date)
    try:
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(currency_data, file, ensure_ascii=False, indent=2)
    except Exception:
        raise WriteToFileError(full_path)


def _read_currency_data() -> dict:
    """"Возвращает считанные данные из файла с расширением .json"""
    full_path = _form_full_path()
    try:
        with open(full_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)
    except Exception:
        raise ReadFileError(full_path)

    return json_data


def _convert_to_currency_data(read_data: dict) -> CurrencyData:
    """Конвертирует словарь с данными в объект класса CryptoCurrencyData"""
    return CurrencyData(
        error_message=read_data.get("error_message", ""),
        last_updated=read_data.get("last_updated", ""),
        currencies_list=read_data.get("currencies_list", [])
    )


def get_read_data(specific_date: Optional[date]) -> CurrencyData:
    """Возвращает объект класса CryptoCurrencyData с актуальными данными"""
    if not is_dir_for_json_files():
        create_dir_for_json_files()

    try:
        if not os.path.isfile(_form_full_path()):
            _write_currency_data(specific_date)
        else:
            currency_data = _read_currency_data()
            last_updated = currency_data.get("last_updated", "")
            interval = 1 if currency_data.get("error_message", "") else 60
            # Если есть ошибка - обновлять каждую минуту, иначе каждые 60 минут
            if specific_date or do_need_update(last_updated=last_updated, interval=interval):
                # если данные не актуальны или нужно получить новые данные на конкретную дату,
                # информация обновляется
                _write_currency_data(specific_date)

        currency_data = _read_currency_data()

    except (ReadFileError, WriteToFileError, ConversionStringError) as exc:
        LOGGER.error(exc)
        currency_data = _get_data_for_recording(specific_date)

    return _convert_to_currency_data(currency_data)
