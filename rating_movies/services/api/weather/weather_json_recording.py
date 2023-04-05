import json
import os
import logging
from typing import Optional

from site_engine.settings import BASE_DIR
from rating_movies.exceptions import WriteToFileError, ReadFileError, ConversionStringError
from rating_movies.services.api.api_utils import create_dir_for_json_files, do_need_update, is_dir_for_json_files
from rating_movies.services.api.weather.weather_api import get_yandex_weather_data, WeatherData


LOGGER = logging.getLogger("json_api_logger")


def _get_data_for_recording() -> dict:
    """Возвращает словарь с данными для записи в файл.
    При наличии сообщения об ошибке запишет в 'weather_dict' старые данные."""
    data_for_recording = get_yandex_weather_data()

    if not data_for_recording.error_message:
        current_weather = data_for_recording.current_weather
        weather_forecast = data_for_recording.weather_forecast
    else:
        old_data = _get_old_data()
        current_weather = _get_old_current_weather(old_data)
        weather_forecast = _get_old_weather_forecast(old_data)

    return {
        "error_message": data_for_recording.error_message,
        "last_updated": data_for_recording.last_updated,
        "current_weather": current_weather,
        "weather_forecast": weather_forecast
    }


def _get_old_data() -> Optional[dict]:
    """Возвращает старые данные из файла"""
    try:
        old_data = _read_weather_data(_form_full_path())
    except (ReadFileError, FileNotFoundError) as exc:
        LOGGER.error(exc)
        old_data = None

    return old_data


def _get_old_current_weather(old_data: Optional[dict]) -> dict:
    """Возвращает старые данные о текущей погоде"""
    if old_data:
        current_weather = old_data.get("current_weather", {})
    else:
        current_weather = {}

    return current_weather


def _get_old_weather_forecast(old_data: Optional[dict]) -> list:
    """Возвращает старые данные о прогнозе погоды"""
    if old_data:
        weather_forecast = old_data.get("weather_forecast", [])
    else:
        weather_forecast = []

    return weather_forecast


def _form_full_path(file_name: str = None) -> str:
    """Формирует полный путь до передаваемого файла.
        Если имя файла не было передано, оно устанавливается в базовое значение"""
    if file_name is None:
        file_name = "yandex_weather_data.json"

    return os.path.join(BASE_DIR, "rating_movies", "json_files", file_name)


def _write_weather_data(full_path: str) -> None:
    """Записывает данные в файл с расширением .json"""
    weather_data = _get_data_for_recording()
    try:
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(weather_data, file, ensure_ascii=False, indent=2)
    except Exception:
        raise WriteToFileError(full_path)


def _read_weather_data(full_path: str) -> dict:
    """Возвращает считанные данные из файла с расширением .json"""
    try:
        with open(full_path, "r", encoding="utf-8") as file:
            weather_json_data = json.load(file)
    except Exception:
        raise ReadFileError(full_path)

    return weather_json_data


def _convert_to_weather_object(read_data: dict) -> WeatherData:
    """Конвертирует словарь с данными в объект класса WeatherData"""
    return WeatherData(
        error_message=read_data.get("error_message", ""),
        last_updated=read_data.get("last_updated", ""),
        current_weather=read_data.get("current_weather", {}),
        weather_forecast=read_data.get("weather_forecast", [])
    )


def get_read_data() -> WeatherData:
    """Возвращает объект класса WeatherData с актуальными данными"""
    if not is_dir_for_json_files():
        create_dir_for_json_files()

    try:
        path = _form_full_path()
        if not os.path.isfile(path):
            _write_weather_data(path)
        else:
            weather_data = _read_weather_data(path)
            last_updated = weather_data.get("last_updated", "")
            interval = 1 if weather_data.get("error_message", "") else 30
            # Если есть ошибка - обновлять каждую минуту, иначе каждые 30 минут
            if do_need_update(last_updated=last_updated, interval=interval):
                _write_weather_data(path)

        weather_data = _read_weather_data(path)

    except (WriteToFileError, ReadFileError, ConversionStringError) as exc:
        LOGGER.error(exc)
        weather_data = _get_data_for_recording()

    return _convert_to_weather_object(weather_data)
