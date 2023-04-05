from rating_movies.services.api.crypto_currency.crypto_currency_api import CryptoCurrencyData


def sort_crypto_currency(sorting: str, crypto_currency_data: CryptoCurrencyData) -> CryptoCurrencyData:
    """Сортирует переданные данные на основе параметра 'sorting'."""
    sorting_type, sorting_column = sorting.split(":")
    sorting_function = _get_sorting_function(sorting_column)
    return sorting_function(sorting_type=sorting_type, data=crypto_currency_data)


def _get_sorting_function(sorting_column):
    sorting_functions = {
        "0": _sort_by_number,
        "1": _sort_by_name,
        "2": _sort_by_price,
        "3": _sort_by_percent_change_24h,
        "4": _sort_by_percent_change_7d,
        "5": _sort_by_percent_change_30d
    }
    return sorting_functions[sorting_column]


def _sort_by_number(sorting_type: str, data: CryptoCurrencyData) -> CryptoCurrencyData:
    """Сортировка списка криптовалют на основе порядкового номера."""
    if sorting_type == "descending":
        data.crypto_currencies_list = data.crypto_currencies_list[::-1]
    return data


def _sort_by_name(sorting_type: str, data: CryptoCurrencyData) -> CryptoCurrencyData:
    """Сортировка списка криптовалют на основе названия."""
    names_list = [crypto_coin.get("name") for crypto_coin in data.crypto_currencies_list]
    sorted_list = []
    if sorting_type == "ascending":
        names_list = sorted(names_list)
    else:
        names_list = sorted(names_list, reverse=True)

    for name in names_list:
        for crypto_currency in data.crypto_currencies_list:
            if crypto_currency.get("name") == name:
                sorted_list.append(crypto_currency)
                break
    data.crypto_currencies_list = sorted_list
    return data


def _sort_by_price(sorting_type: str, data: CryptoCurrencyData) -> CryptoCurrencyData:
    """Сортировка списка криптовалют на основе цены."""
    prices_list = [crypto_coin.get("price") for crypto_coin in data.crypto_currencies_list]
    sorted_list = []
    if sorting_type == "ascending":
        prices_list = sorted(prices_list, key=lambda elem: float(elem.replace(",", "")))
        # Запятая убирается, чтобы строку можно было привести к типу float
    else:
        prices_list = sorted(prices_list, key=lambda elem: float(elem.replace(",", "")), reverse=True)

    for price in prices_list:
        for crypto_currency in data.crypto_currencies_list:
            if crypto_currency.get("price") == price and crypto_currency not in sorted_list:
                sorted_list.append(crypto_currency)
                break
    data.crypto_currencies_list = sorted_list
    return data


def _sort_by_percent_change_24h(sorting_type: str, data: CryptoCurrencyData) -> CryptoCurrencyData:
    """Сортировка списка криптовалют на основе колебания цены в процентах за последние 24 часа"""
    percent_changes_list = [crypto_coin.get("percent_change_24h") for crypto_coin in data.crypto_currencies_list]
    sorted_list = []
    if sorting_type == "ascending":
        percent_changes_list = sorted(percent_changes_list, key=lambda elem: float(elem.replace(",", "")))
    else:
        percent_changes_list = sorted(percent_changes_list, key=lambda elem: float(elem.replace(",", "")), reverse=True)

    for percent_change in percent_changes_list:
        for crypto_currency in data.crypto_currencies_list:
            if crypto_currency.get("percent_change_24h") == percent_change and crypto_currency not in sorted_list:
                sorted_list.append(crypto_currency)
                break
    data.crypto_currencies_list = sorted_list
    return data


def _sort_by_percent_change_7d(sorting_type: str, data: CryptoCurrencyData) -> CryptoCurrencyData:
    """Сортировка списка криптовалют на основе колебания цены в процентах за последние 7 дней."""
    percent_changes_list = [crypto_coin.get("percent_change_7d") for crypto_coin in data.crypto_currencies_list]
    sorted_list = []
    if sorting_type == "ascending":
        percent_changes_list = sorted(percent_changes_list, key=lambda elem: float(elem.replace(",", "")))
    else:
        percent_changes_list = sorted(percent_changes_list, key=lambda elem: float(elem.replace(",", "")), reverse=True)

    for percent_change in percent_changes_list:
        for crypto_currency in data.crypto_currencies_list:
            if crypto_currency.get("percent_change_7d") == percent_change and crypto_currency not in sorted_list:
                sorted_list.append(crypto_currency)
                break
    data.crypto_currencies_list = sorted_list
    return data


def _sort_by_percent_change_30d(sorting_type: str, data: CryptoCurrencyData) -> CryptoCurrencyData:
    """Сортировка списка криптовалют на основе колебания цены в процентах за последние 30 дней."""
    percent_changes_list = [crypto_coin.get("percent_change_30d") for crypto_coin in data.crypto_currencies_list]
    sorted_list = []
    if sorting_type == "ascending":
        percent_changes_list = sorted(percent_changes_list, key=lambda elem: float(elem.replace(",", "")))
    else:
        percent_changes_list = sorted(percent_changes_list, key=lambda elem: float(elem.replace(",", "")), reverse=True)

    for percent_change in percent_changes_list:
        for crypto_currency in data.crypto_currencies_list:
            if crypto_currency.get("percent_change_30d") == percent_change and crypto_currency not in sorted_list:
                sorted_list.append(crypto_currency)
                break
    data.crypto_currencies_list = sorted_list
    return data
