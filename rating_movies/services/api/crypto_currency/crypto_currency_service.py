from rating_movies.services.api.crypto_currency.crypto_currency_json_recording import get_read_data
from rating_movies.services.api.crypto_currency.crypto_currency_api import CryptoCurrencyData


def get_crypto_currency_data(rows: str = "10") -> CryptoCurrencyData:
    return get_read_data(rows)
