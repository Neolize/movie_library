from datetime import datetime, date as datetime_date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, Http404, HttpResponseServerError, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, ListView, DetailView
from django.core.handlers.wsgi import WSGIRequest
from allauth.account.views import LoginView, SignupView, PasswordResetView, LogoutView


from rating_movies import models, forms
from rating_movies.services import utils
from rating_movies.services.crud import create, read, update, delete
from rating_movies.permissions import StaffPermissionsMixin
from rating_movies.services.crud.crud_utils import GenreYear

from rating_movies.services.api.crypto_currency.crypto_currency_service import get_crypto_currency_data
from rating_movies.services.api.currency.currency_service import get_currency_data
from rating_movies.services.api.weather.weather_service import get_weather_data
from rating_movies.services.api.crypto_currency.crypto_currency_sorting import sort_crypto_currency


def show_page_not_found(request, exception):
    text = "<h1 style=\"width: 250px; margin: auto; margin-top: 50px;\">Page not found</h1>"
    return HttpResponseNotFound(text)


def show_beautiful_page_not_found(request):
    template = "rating_movies/detail/page_not_found.html"
    return render(request, template, context={"previous_url": utils.get_previous_url(request)})


class MoviesView(GenreYear, ListView):
    """Список фильмов"""
    model = models.Movie
    template_name = "rating_movies/main.html"
    queryset = read.get_all_movies_ordered_by_parameter("-world_premiere")
    context_object_name = "movies"
    paginate_by = 6


class JsonFilteringMoviesView(ListView):
    """Movies filtering with ajax"""
    template_name = "rating_movies/main.html"
    context_object_name = "movies"

    def get_queryset(self):
        return read.get_filtered_movies(years=self.get_years_from_request(), genres=self.get_genres_from_request())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["years"] = list(map(int, self.get_years_from_request()))
        context["genres"] = list(map(int, self.get_genres_from_request()))
        # чтобы отметить выбранный(-ые) checkbox с годом и жанром их нужно преобразовать к integer,
        # так как поле id у модели Genre и поле year у модели Movie тоже integer
        return context

    def get(self, request, *args, **kwargs):
        queryset = list(self.get_queryset())
        return JsonResponse({"movies": queryset})

    def get_years_from_request(self) -> list:
        return self.request.GET.getlist("year")

    def get_genres_from_request(self) -> list:
        return self.request.GET.getlist("genre")


class JsonSortingMoviesView(ListView):
    """Movies sorting with ajax"""
    template_name = "rating_movies/main.html"
    context_object_name = "movies"

    def get_queryset(self, **kwargs):
        return read.get_sorted_movies(**kwargs)

    def get(self, *args, **kwargs):
        sorting = self.request.GET.get("sorting", "2")  # base sorting by world premiere
        sorting_order = self.request.GET.get("sorting_order", "descending")  # base order by descending
        queryset = self.get_queryset(sorting=sorting, sorting_order=sorting_order)

        if not isinstance(queryset, list):
            queryset = list(queryset)

        return JsonResponse({"movies": queryset})


class SearchView(GenreYear, ListView):
    """Поиск фильмов по названию"""
    template_name = "rating_movies/main.html"
    context_object_name = "movies"
    paginate_by = 3

    def get_queryset(self):
        return read.search_movies(parameter=self.get_entered_parameter())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f"q={self.get_entered_parameter()}&"  # формируем url для пагинации
        context["entered_title"] = self.get_entered_parameter()
        return context

    def get_entered_parameter(self):
        # возвращает введённое пользователем название фильма
        return self.request.GET.get("q", "")


class ActorsDirectorsView(GenreYear, ListView):
    """Список актёров и режиссёров"""
    template_name = "rating_movies/list/actors_directors.html"
    queryset = read.get_all_actors_directors_ordered_by_parameter("name")


class CategoriesView(GenreYear, ListView):
    """Список категорий"""
    template_name = "rating_movies/list/categories.html"
    queryset = read.get_all_categories_ordered_by_parameter("id")
    context_object_name = "categories"


class GenresView(GenreYear, ListView):
    """Список жанров"""
    template_name = "rating_movies/list/genres.html"
    queryset = read.get_all_genres_ordered_by_parameter("id")
    context_object_name = "genres"


class GenreDetailView(GenreYear, ListView):
    """Список фильмов заданного жанра"""
    template_name = "rating_movies/main.html"
    context_object_name = "movies"
    allow_empty = False

    def get(self, request, *args, **kwargs):
        self.queryset = read.get_genre_movies(genre_slug=kwargs.get("slug", ""))
        return super().get(request, *args, **kwargs)


class CategoryDetailView(GenreYear, ListView):
    """Список объектов в данной категории"""
    template_name = "rating_movies/main.html"
    context_object_name = "movies"
    allow_empty = False

    def get(self, request, *args, **kwargs):
        self.queryset = read.get_related_objects_to_category(category_url=kwargs.get("slug", ""))
        return super().get(request, *args, **kwargs)


class MovieDetailView(GenreYear, DetailView):
    """Полное описание фильма"""
    template_name = "rating_movies/detail/movie_detail.html"
    context_object_name = "movie"
    star_form = forms.RatingForm
    review_form = forms.ReviewForm

    def get_object(self, queryset=None):
        self.movie = read.get_movie_by_parameters(url=self.kwargs.get("slug"))
        if not self.movie:
            raise Http404("Such movie does not exist")
        utils.change_movie_fields(self.movie)
        return self.movie

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        context["star_form"] = self.star_form
        context["review_form"] = self.review_form
        context["user_rating"] = str(read.get_movie_rating(request=self.request, movie_id=self.movie.pk))
        # для корректного сравнения в шаблоне user_rating должен быть типа str
        context["average_rating"] = read.fetch_average_movie_rating(movie_id=self.movie.pk)
        context["movie_rating"] = utils.add_class_color_to_movie_rating(read.get_other_sources_rating(self.movie))
        # return movie rating from api with identified colors
        context["movie_reviews"] = read.get_movie_reviews(self.movie)
        context["is_movie"] = read.is_movie_in_user_watchlist(movie=self.movie, user=self.request.user)
        return context


class ActorDirectorDetailView(GenreYear, DetailView):
    """Полное описание актёра/режиссёра"""
    template_name = "rating_movies/detail/actor_director_detail.html"
    context_object_name = "actor_director"

    def get_object(self, queryset=None):
        actor_director = read.get_actor_director_by_parameters(url=self.kwargs.get("slug"))
        if not actor_director:
            raise Http404("Such actor/director doest not exist")
        return actor_director


class RandomMoviesView(View):
    """Страница с выбором псевдослучайных фильмов"""
    template = "rating_movies/detail/random_movies.html"
    form = forms.RandomMoviesForm

    def get(self, request):
        data = {
            "form": self.form,
            "movies": read.get_random_movies(),
        }
        return render(request, self.template, context=data)

    def post(self, request: WSGIRequest):
        form = self.form(request.POST)
        random_movies = read.get_random_movies_from_form(form=form)

        if random_movies:
            data = {
                "form": self.form,
                "movies": random_movies,
            }
            return render(request, self.template, context=data)

        data = {
            "form": form,
            "movies": read.get_random_movies()
        }
        return render(request, self.template, context=data)


class AddReviewView(View):
    """Добавление отзыва"""
    form = forms.ReviewForm

    def post(self, request: WSGIRequest, pk: int):
        form = self.form(request.POST)
        movie = read.get_movie_by_parameters(pk=pk)

        create.create_review(form=form, movie=movie, request=request)
        return redirect(to=movie.get_absolute_url())


class AddRating(View):
    """Добавление рейтинга"""
    form = forms.RatingForm

    def post(self, request: WSGIRequest):
        form = self.form(request.POST)

        if create.update_or_create_rating(form=form, request=request):
            return HttpResponse(status=201)
        return HttpResponse(status=400)


class AddActorDirectorView(LoginRequiredMixin, View):
    """Добавление актёра или режиссёра"""
    template = "rating_movies/add/add_actor_director.html"
    form = forms.ActorDirectorForm
    login_url = reverse_lazy("login")

    def get(self, request):
        return render(request, self.template, context={"form": self.form})

    def post(self, request: WSGIRequest):
        form = self.form(request.POST, request.FILES)
        actor_director_creation = create.ActorDirectorCreation(form=form)

        if new_actor_director := actor_director_creation.create_actor_director():
            return redirect(new_actor_director.get_absolute_url())
        return render(request, self.template, context={"form": form})


class AddCategoryView(LoginRequiredMixin, View):
    """Добавление категории"""
    template = "rating_movies/add/add_category.html"
    form = forms.CategoryForm
    login_url = reverse_lazy("login")

    def get(self, request):
        return render(request, self.template, context={"form": self.form})

    def post(self, request: WSGIRequest):
        form = self.form(request.POST)
        category_creation = create.CategoryCreation(form=form)

        if category_creation.create_category():
            return redirect("categories")
        return render(request, self.template, context={"form": form})


class AddGenreView(LoginRequiredMixin, View):
    """Добавление жанра"""
    template = "rating_movies/add/add_genre.html"
    form = forms.GenreForm
    login_url = "login"

    def get(self, request):
        return render(request, self.template, context={"form": self.form})

    def post(self, request: WSGIRequest):
        form = self.form(request.POST)
        genre_creation = create.GenreCreation(form=form)

        if genre_creation.create_genre():
            return redirect("genres")
        return render(request, self.template, context={"form": form})


class AddMovieView(LoginRequiredMixin, View):
    """Добавление фильма"""
    template = "rating_movies/add/add_movie.html"
    form = forms.MovieForm
    login_url = reverse_lazy("login")

    def get(self, request):
        return render(request, self.template, context={"form": self.form})

    def post(self, request: WSGIRequest):
        form = self.form(request.POST, request.FILES)
        movie_creation = create.MovieCreation(form=form)

        if new_movie := movie_creation.create_movie():
            return redirect(new_movie.get_absolute_url())
        return render(request, self.template, context={"form": form})


class AddMovieShotView(LoginRequiredMixin, View):
    """Добавление кадров из фильма"""
    template = "rating_movies/add/add_movie_shot.html"
    form = forms.MovieShotForm
    login_url = reverse_lazy("login")

    def get(self, request):
        return render(request, self.template, context={"form": self.form})

    def post(self, request: WSGIRequest):
        form = self.form(request.POST, request.FILES)
        movie_shot_creation = create.MovieShotCreation(form=form)

        if new_movie_shot := movie_shot_creation.create_movie_shot():
            return redirect(new_movie_shot.movie.get_absolute_url())
        return render(request, self.template, context={"form": form})


class AddRatingStar(LoginRequiredMixin, View):
    """Добавление звезды рейтинга"""
    template = "rating_movies/add/add_rating_star.html"
    form = forms.RatingStarForm
    login_url = reverse_lazy("login")

    def get(self, request):
        return render(request, self.template, context={"form": self.form})

    def post(self, request: WSGIRequest):
        form = self.form(request.POST)

        if create.create_rating_star(form=form):
            return redirect(to="home")
        return render(request, self.template, context={"form": form})


class DeleteActorDirectorView(LoginRequiredMixin, StaffPermissionsMixin, View):
    """Удаление актёра/режиссёра"""
    redirect_to = "actors_directors"
    error_message = "An error occurred while deleting an actor/a director on the server"
    error_style = "margin: 35px 0 0 35px;"
    raise_exception = True

    def post(self, request, slug: str):
        actor_director = read.get_actor_director_by_parameters(url=slug)
        if not actor_director:
            raise Http404("Such actor/director does not exist")

        if not delete.delete_actor_director(actor_director=actor_director):
            return HttpResponseServerError(f"<h1 style=\"{self.error_style}\">{self.error_message}<h2>")
        return redirect(to=self.redirect_to)


class UpdateMovieView(LoginRequiredMixin, StaffPermissionsMixin, View):
    """Изменение фильма"""
    template = "rating_movies/update/update_movie.html"
    form = forms.MovieForm
    login_url = reverse_lazy("login")

    def get(self, request, slug: str):
        movie = read.get_movie_by_parameters(url=slug)
        if not movie:
            raise Http404("Such movie does not exist")

        form = self.form(instance=movie)
        data = {
            "form": form,
            "movie": movie,
        }
        return render(request, self.template, context=data)

    def post(self, request: WSGIRequest, slug: str):
        movie = read.get_movie_by_parameters(url=slug)
        if not movie:
            raise Http404("Such movie does not exist")

        form = self.form(request.POST, request.FILES, instance=movie)
        update_movie = update.update_movie(form=form)

        if update_movie:
            return redirect(to=movie.get_absolute_url())
        data = {
            "form": form,
            "movie": movie,
        }
        return render(request, self.template, context=data)


class UpdateActorDirectorView(LoginRequiredMixin, StaffPermissionsMixin, View):
    """Изменение актёра/режиссёра"""
    template = "rating_movies/update/update_actor_director.html"
    form = forms.ActorDirectorForm
    login_url = reverse_lazy("login")

    def get(self, request: WSGIRequest, slug: str):
        actor_director = read.get_actor_director_by_parameters(url=slug)
        if not actor_director:
            raise Http404("Such actor/director does not exist")

        form = self.form(instance=actor_director)
        data = {
            "form": form,
            "actor_director": actor_director
        }
        return render(request, self.template, context=data)

    def post(self, request: WSGIRequest, slug: str):
        actor_director = read.get_actor_director_by_parameters(url=slug)
        if not actor_director:
            raise Http404("Such actor/director does not exist")

        form = self.form(request.POST, request.FILES, instance=actor_director)
        update_actor_director = update.update_actor_director(form=form)

        if update_actor_director:
            return redirect(to=actor_director.get_absolute_url())
        data = {
            "form": form,
            "actor_director": actor_director
        }
        return render(request, self.template, context=data)


class RegisterUserView(SignupView):
    """Регистрация пользователя"""
    template_name = "account/signup.html"
    form_class = forms.RegisterUserForm
    success_url = reverse_lazy("home")


class LoginUserView(LoginView):
    """Авторизация пользователя"""
    template_name = "account/login.html"
    form_class = forms.LoginUserForm
    success_url = reverse_lazy("home")


class UserPasswordResetView(PasswordResetView):
    """Сброс пароля пользователя"""
    template_name = "account/password_reset.html"
    form_class = forms.ResetUserPasswordForm
    success_url = reverse_lazy("login")


class SocialAccountLoginUserView(LoginView):
    """Авторизация пользователя через
     сторонние учётные записи"""
    template_name = "socialaccount/login.html"


class LogoutUserView(LogoutView):
    """Выход из системы"""
    template_name = "account/logout.html"
    login_url = reverse_lazy("login")

    def get_redirect_url(self):
        return reverse_lazy("login")


class WeatherView(View):
    """Страница с данными о погоде"""
    template = "rating_movies/detail/weather.html"

    def get(self, request):
        data = {
            "weather_data": get_weather_data(),
            "current_datetime": datetime.now().strftime("%b %d, %H:%M"),
            "back_link": utils.get_previous_url(request)
        }
        return render(request, self.template, context=data)


class CryptoCurrencyView(View):
    """Страница с данными о криптовалюте"""
    template = "rating_movies/detail/crypto_currency.html"
    form = forms.CryptoCurrencyForm

    def get(self, request):
        data = {
            "crypto_currency_data": get_crypto_currency_data(),
            "form": self.form,
            "back_link": utils.get_previous_url(request)
        }
        return render(request, self.template, context=data)

    def post(self, request: WSGIRequest):
        rows = request.POST.get("rows")
        sorting = request.POST.get("sorting")
        crypto_currency_data = get_crypto_currency_data(rows=rows)

        data = {
            "crypto_currency_data": sort_crypto_currency(sorting=sorting, crypto_currency_data=crypto_currency_data),
            "form": self.form(request.POST),
            "back_link": utils.get_previous_url(request)
        }
        return render(request, self.template, context=data)


class CurrencyView(View):
    """Страница с данными о курсе валют"""
    template = "rating_movies/detail/currency.html"
    current_date = str(datetime_date.today())

    def get(self, request):
        data = {
            "currency_data": get_currency_data(),
            "date_value": utils.format_currency_date(self.current_date),
            "max_date": self.current_date,
            "back_link": utils.get_previous_url(request)
        }
        return render(request, self.template, context=data)

    def post(self, request: WSGIRequest):
        received_date = request.POST.get("date")
        data = {
            "currency_data": get_currency_data(received_date),
            "date_value": utils.format_currency_date(received_date),
            "max_date": self.current_date,
            "back_link": utils.get_previous_url(request)
        }
        return render(request, self.template, context=data)


class RandomPasswordView(View):
    """Страница с генерацией случайного пароля"""
    base_template = "rating_movies/detail/random_password.html"
    generated_password_template = "rating_movies/detail/generated_password.html"

    def get(self, request: WSGIRequest):
        return render(request, self.base_template, context=self.get_context_data())

    def post(self, request: WSGIRequest):
        password = utils.generate_random_password(request.POST)
        return JsonResponse({"password": password})

    def get_context_data(self) -> dict:
        return {
            "default_length": 12,
            "max_length": 32,
            "min_length": 8,
            "back_link": utils.get_previous_url(self.request)
        }


class UserProfileView(LoginRequiredMixin, View):
    """User profile page"""
    template = "rating_movies/detail/user_profile.html"

    def get(self, request: WSGIRequest):
        user_movies = read.get_all_user_movies(request.user)
        data = {
            "user_movies": user_movies,
            "movies_number": 0 if user_movies is None else len(user_movies),
        }
        return render(request, self.template, context=data)


@login_required(login_url=reverse_lazy("login"))
def add_movie_to_watchlist_view(request: WSGIRequest, movie_slug: str):
    movie = read.get_movie_by_parameters(url=movie_slug)
    create.add_movie_to_user_movie_list(user=request.user, movie=movie)
    return redirect(movie.get_absolute_url())


def show_phone_mask(request):
    template = "rating_movies/add/phone_mask.html"
    return render(request, template)
