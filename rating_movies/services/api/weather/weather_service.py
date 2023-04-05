from rating_movies.services.api.weather.weather_json_recording import get_read_data
from rating_movies.services.api.weather.weather_api import WeatherData


def get_weather_data() -> WeatherData:
    return get_read_data()
