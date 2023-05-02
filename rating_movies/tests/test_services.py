from datetime import date

from django.test import TestCase
from django.test.client import RequestFactory
from django.http.request import QueryDict

from rating_movies import models
from rating_movies.services import utils
from rating_movies.services.crud import crud_utils
from rating_movies.services.api.currency import currency_api
from rating_movies.services.api.crypto_currency import crypto_currency_api
from rating_movies.services.api.weather import weather_api
from rating_movies.services.api.movies import movies_api


class UtilsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_format_budget(self):
        first_budget = utils.format_budget(10_550_170)
        second_budget = utils.format_budget(10)
        third_budget = utils.format_budget(0)
        fourth_budget = utils.format_budget(498_905)

        self.assertEqual("10 550 170", first_budget)
        self.assertEqual("10", second_budget)
        self.assertEqual("0", third_budget)
        self.assertEqual("498 905", fourth_budget)

    def test_get_client_ip(self):
        first_request = self.factory.get("/genres/")
        second_request = self.factory.get("/movie/terminator/")

        first_user_ip = utils.get_client_ip(first_request)
        second_user_ip = utils.get_client_ip(second_request)

        self.assertEqual("127.0.0.1", first_user_ip)
        self.assertEqual("127.0.0.1", second_user_ip)

    def test_convert_years_for_random_movies(self):
        first_case_years = utils.convert_years_for_random_movies("All years")
        second_case_years = utils.convert_years_for_random_movies("1980 - 2000")
        third_case_years = utils.convert_years_for_random_movies("After 2020")

        self.assertEqual(None, first_case_years)
        self.assertEqual(["1980", "2000"], second_case_years)
        self.assertEqual([2020, date.today().year], third_case_years)

    def test_format_currency_date(self):
        first_currency_date = utils.format_currency_date("2018-7-15")
        second_currency_date = utils.format_currency_date("1998-11-5")
        third_currency_date = utils.format_currency_date("2005-12-25")

        self.assertEqual("15.7.2018", first_currency_date)
        self.assertEqual("5.11.1998", second_currency_date)
        self.assertEqual("25.12.2005", third_currency_date)

    def test_generate_random_password(self):
        first_query_dict = QueryDict("", mutable=True)
        second_query_dict = QueryDict("", mutable=True)
        third_query_dict = QueryDict("", mutable=True)

        first_query_dict.update({"password_length": 8})
        second_query_dict.update({"password_length": 20})
        third_query_dict.update({"password_length": 32})

        first_password = utils.generate_random_password(first_query_dict)
        second_password = utils.generate_random_password(second_query_dict)
        third_password = utils.generate_random_password(third_query_dict)

        self.assertEqual([8, 20, 32], [len(first_password), len(second_password), len(third_password)])

    def test_add_class_color_to_movie_rating(self):
        movie_rating = {
            "imDb": 7.5,
            "metacritic": 50,
            "rottenTomatoes": 42
        }

        first_result = utils.add_class_color_to_movie_rating(None)
        second_result = utils.add_class_color_to_movie_rating(movie_rating)

        self.assertEqual(None, first_result)
        self.assertEqual("green", second_result.get("imDb_color"))
        self.assertEqual("orange", second_result.get("metacritic_color"))
        self.assertEqual("red", second_result.get("rottenTomatoes_color"))


class CrudUtilsTestCase(TestCase):
    def setUp(self):
        first_genre = models.Genre.objects.create(name="action", url="action")
        second_genre = models.Genre.objects.create(name="drama", url="drama")
        third_genre = models.Genre.objects.create(name="adventure", url="adventure")

        first_movie = models.Movie.objects.create(title="First movie", world_premiere=date(year=1990, month=1, day=1))
        second_movie = models.Movie.objects.create(title="Second movie", world_premiere=date(year=2008, month=1, day=1))
        third_movie = models.Movie.objects.create(title="Third movie", world_premiere=date(year=2002, month=1, day=1))

        first_movie.genres.add(first_genre, third_genre)
        second_movie.genres.add(second_genre)
        third_movie.genres.add(first_genre)

        self.genre_year = crud_utils.GenreYear()

    def test_calculate_age(self):
        first_birth_date = date.today()
        first_death_date = None
        second_birth_date = date(year=1988, month=8, day=31)
        second_death_date = date(year=2022, month=1, day=23)

        first_result = crud_utils.calculate_age(first_birth_date, first_death_date)
        second_result = crud_utils.calculate_age(second_birth_date, second_death_date)

        self.assertEqual(0, first_result)
        self.assertEqual(33, second_result)

    def test_get_genres(self):
        genres = list(models.Genre.objects.all().distinct())
        results = self.genre_year.get_genres()

        is_equal = True
        for res in results:
            if res not in genres:
                is_equal = False

        self.assertEqual(True, is_equal)

    def test_get_years(self):
        years = list(models.Movie.objects.all().values("year").order_by("year"))
        results = self.genre_year.get_years()

        self.assertEqual(years, results)


class TestAPICase(TestCase):
    def test_currency_api(self):
        results = currency_api.get_cbr_data(None)
        self.assertEqual("", results.error_message)

    def test_crypto_currency_api(self):
        results = crypto_currency_api.get_coin_market_cap_data(limit="10")
        self.assertEqual("", results.error_message)

    def test_weather_api(self):
        results = weather_api.get_yandex_weather_data()
        self.assertEqual("", results.error_message)

    def test_movies_api(self):
        results = movies_api.get_movie_rating("Inception")
        self.assertNotEqual(None, results)
