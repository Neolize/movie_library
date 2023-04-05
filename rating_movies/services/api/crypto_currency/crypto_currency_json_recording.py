import json
import os
import logging

from site_engine.settings import BASE_DIR
from rating_movies.services.api.api_utils import do_need_update, create_dir_for_json_files, is_dir_for_json_files,\
    get_folder_name_for_json_files
from rating_movies.services.api.crypto_currency.crypto_currency_api import get_coin_market_cap_data, CryptoCurrencyData
from rating_movies.exceptions import ReadFileError, WriteToFileError, ConversionStringError


LOGGER = logging.getLogger("json_api_logger")


def _get_data_for_recording() -> dict:
    """Возвращает словарь с данными для записи в файл.
    При наличии сообщения об ошибке запишет в 'crypto_currencies_list' старые данные."""
    data_for_recording = get_coin_market_cap_data()

    if not data_for_recording.error_message:
        crypto_currencies_list = data_for_recording.crypto_currencies_list
    else:
        crypto_currencies_list = _get_old_crypto_currencies_list()

    return {
        "error_message": data_for_recording.error_message,
        "last_updated": data_for_recording.last_updated,
        "crypto_currencies_list": crypto_currencies_list
    }


def _get_old_crypto_currencies_list() -> list:
    """Возвращает старые данные из файла."""
    try:
        old_data = _read_crypto_currency_data()
        crypto_currencies_list = old_data.get("crypto_currencies_list")
    except (ReadFileError, FileNotFoundError) as exc:
        LOGGER.error(exc)
        crypto_currencies_list = []

    return crypto_currencies_list


def _form_full_path(file_name: str = None) -> str:
    """Формирует полный путь до передаваемого файла.
    Если имя файла не было передано, оно устанавливается в базовое значение"""
    if file_name is None:
        file_name = "coin_market_cap_data.json"

    return BASE_DIR / "rating_movies" / get_folder_name_for_json_files() / file_name


def _write_crypto_currency_data() -> None:
    """Записывает данные в файл с расширением .json"""
    full_path = _form_full_path()
    crypto_currency_data = _get_data_for_recording()
    try:
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(crypto_currency_data, file, ensure_ascii=False, indent=2)
    except Exception:
        raise WriteToFileError(full_path)


def _read_crypto_currency_data() -> dict:
    """Возвращает считанные данные из файла с расширением .json"""
    full_path = _form_full_path()
    try:
        with open(full_path, "r") as file:
            json_data = json.load(file)
    except Exception:
        raise ReadFileError(full_path)

    return json_data


def _convert_to_crypto_currency_object(read_data: dict, rows: int) -> CryptoCurrencyData:
    """Конвертирует словарь с данными в объект класса CryptoCurrencyData"""
    return CryptoCurrencyData(
        error_message=read_data.get("error_message"),
        last_updated=read_data.get("last_updated"),
        crypto_currencies_list=read_data.get("crypto_currencies_list")[:rows],
    )


def get_read_data(rows) -> CryptoCurrencyData:
    """Возвращает объект класса CryptoCurrencyData с актуальными данными"""
    if not is_dir_for_json_files():
        create_dir_for_json_files()

    try:
        if not os.path.isfile(_form_full_path()):
            _write_crypto_currency_data()
        else:
            crypto_currency_data = _read_crypto_currency_data()
            last_updated = crypto_currency_data.get("last_updated", "")
            interval = 1 if crypto_currency_data.get("error_message", "") else 10
            # Если есть ошибка - обновлять каждую минуту, иначе каждые 10 минут
            if do_need_update(last_updated=last_updated, interval=interval):
                # если данные не актуальны, то информация обновляется
                _write_crypto_currency_data()

        crypto_currency_data = _read_crypto_currency_data()

    except (ReadFileError, WriteToFileError, ConversionStringError) as exc:
        LOGGER.error(exc)
        crypto_currency_data = _get_data_for_recording()

    return _convert_to_crypto_currency_object(crypto_currency_data, int(rows))
