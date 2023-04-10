from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from snowpenguin.django.recaptcha3.fields import ReCaptchaField
from allauth.account.forms import LoginForm, SignupForm, ResetPasswordForm

from rating_movies import models
from rating_movies.services.crud import read


class ReviewForm(forms.ModelForm):
    """Форма добавления отзыва"""
    recaptcha = ReCaptchaField()

    class Meta:
        model = models.Review
        fields = ("name", "email", "text", "recaptcha")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control border", "required": True,
                                           "id": "contactusername", "name": "name"}),
            "email": forms.EmailInput(attrs={"class": "form-control border", "required": True,
                                             "id": "contactemail", "name": "email"}),
            "text": forms.Textarea(attrs={"class": "form-control border", "rows": 5,
                                          "required": True, "name": "text", "id": "contactcomment"}),
        }


class ActorDirectorForm(forms.ModelForm):
    """Форма добавления актёра/режиссёра"""
    class Meta:
        model = models.Actor
        fields = ("name", "birth_date", "description", "image")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control border",
                                           "id": "id_name", "required": True, "name": "name"}),
            "birth_date": forms.DateInput(attrs={"class": "form-control border", "maxlength": "10",
                                                 "required": True, "placeholder": "format: \"YYYY-MM-DD\"",
                                                 "id": "id_birth_date", "name": "birth_date"},
                                          format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"class": "form-control border",
                                                 "rows": 5, "id": "id_description", "required": True,
                                                 "name": "description"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control-file",
                                                     "id": "id_image", "name": "image"})
        }


class CategoryForm(forms.ModelForm):
    """Форма для добавления категории"""
    def clean_url(self):
        new_slug = self.cleaned_data["url"]
        return models.slugify(new_slug)

    class Meta:
        model = models.Category
        fields = ("name", "url", "description")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control border",
                                           "required": True, "id": "id_name", "name": "name"}),
            "url": forms.TextInput(attrs={"class": "form-control border",
                                          "required": True, "id": "id_url", "name": "url"}),
            "description": forms.Textarea(attrs={"class": "form-control border",
                                                 "rows": 5, "id": "id_description", "required": True,
                                                 "name": "description"}),
        }


class GenreForm(forms.ModelForm):
    """Форма добавления жанра"""
    def clean_url(self):
        new_slug = self.cleaned_data["url"]
        return models.slugify(new_slug)

    class Meta:
        model = models.Genre
        fields = ("name", "url", "description")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control border",
                                           "required": True, "id": "id_name", "name": "name"}),
            "url": forms.TextInput(attrs={"class": "form-control border",
                                          "required": True, "id": "id_url", "name": "url"}),
            "description": forms.Textarea(attrs={"class": "form-control border",
                                                 "rows": 5, "id": "id_description", "required": True,
                                                 "name": "description"}),
        }


class MovieForm(forms.ModelForm):
    """Форма добавления фильма"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].empty_label = "Выберите категорию"

    class Meta:
        model = models.Movie
        fields = ("title", "tagline", "description", "poster", "country",
                  "directors", "actors", "genres", "world_premiere", "budget",
                  "fees_in_usa", "fees_in_world", "category", "draft")

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control border",
                                            "required": True, "id": "id_title", "name": "title"}),
            "tagline": forms.TextInput(attrs={"class": "form-control border",
                                              "required": True, "id": "id_tagline", "name": "tagline"}),
            "description": forms.Textarea(attrs={"class": "form-control border",
                                                 "rows": 5, "id": "id_description", "required": True,
                                                 "name": "description"}),
            "poster": forms.ClearableFileInput(attrs={"class": "form-control-file", "id": "id_poster",
                                                      "name": "poster"}),
            "country": forms.TextInput(attrs={"class": "form-control border",
                                              "required": True, "id": "id_country", "name": "country"}),
            "directors": forms.SelectMultiple(attrs={"class": "form-control border", "required": True,
                                                     "id": "id_actors", "name": "actors"}),
            "actors": forms.SelectMultiple(attrs={"class": "form-control border", "required": True,
                                                  "id": "id_actors", "name": "actors"}),
            "genres": forms.SelectMultiple(attrs={"class": "form-control border", "style": "height: 100px;",
                                                  "required": True, "id": "id_genres", "name": "genres"}),
            "world_premiere": forms.DateInput(attrs={"class": "form-control border", "maxlength": "10",
                                                     "required": True, "placeholder": "format: \"YYYY-MM-DD\"",
                                                     "id": "id_world_premiere", "name": "world_premiere"},
                                              format="%Y-%m-%d"),
            "budget": forms.TextInput(attrs={"class": "form-control border",
                                             "required": True, "id": "id_budget", "name": "budget"}),
            "fees_in_usa": forms.TextInput(attrs={"class": "form-control border", "required": True,
                                                  "id": "id_fees_in_usa", "name": "fees_in_usa"}),
            "fees_in_world": forms.TextInput(attrs={"class": "form-control border", "required": True,
                                                    "id": "id_fees_in_world", "name": "fees_in_world"}),
            "category": forms.Select(attrs={"class": "form-control border", "style": "height: 50px;",
                                            "required": True, "id": "id_category", "name": "category"}),
            "draft": forms.CheckboxInput(attrs={"class": "form-draft", "id": "id_draft", "name": "draft"}),
        }


class MovieShotForm(forms.ModelForm):
    """Форма добавления кадров из фильма"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["movie"].empty_label = "Выберите фильм"

    class Meta:
        model = models.MovieShots
        fields = ("title", "description", "image", "movie")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control border",
                                            "required": True, "id": "id_title", "name": "title"}),
            "description": forms.Textarea(attrs={"class": "form-control border",
                                                 "rows": 5, "required": True, "id": "id_description",
                                                 "name": "description"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control-file",
                                                     "required": True, "id": "id_image", "name": "image"}),
            "movie": forms.Select(attrs={"class": "form-control border", "style": "height: 50px;",
                                         "required": True, "id": "id_movie", "name": "movie"}),
        }


class RatingStarForm(forms.ModelForm):
    """Форма добавления звезды рейтинга"""

    class Meta:
        model = models.RatingStar
        fields = ("value", )
        widgets = {
            "value": forms.NumberInput(attrs={"class": "form-control border",
                                              "required": True, "id": "id_value", "name": "value"}),
        }

    def clean_value(self):
        value = self.cleaned_data.get("value", 0)
        if int(value) > 5:
            raise ValidationError(f"Переданное значение \"{value}\" превышает 5")
        return value


class RatingForm(forms.ModelForm):
    """Форма добавления рейтинга"""
    star = forms.ModelChoiceField(
        queryset=read.get_all_rating_stars(), widget=forms.RadioSelect(), empty_label=None
    )

    class Meta:
        model = models.Rating
        fields = ("star", )


class RandomMoviesForm(forms.Form):
    """Форма с выбором псевдослучайных фильмов"""
    years_range_choice_list = [
        ("All years", "Все годы"),
        ("1900 - 1950", "1900 - 1950"),
        ("1950 - 1980", "1950 - 1980"),
        ("1980 - 2000", "1980 - 2000"),
        ("2000 - 2010", "2000 - 2010"),
        ("2010 - 2020", "2010 - 2020"),
        ("After 2020", "После 2020"),
    ]
    # диапазон дат для отображения в форме

    movies_number = forms.IntegerField(
        min_value=1, max_value=read.get_count_movies(), label="Количество фильмов",
        widget=forms.NumberInput(attrs={"class": "form-control border", "value": 1})
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=read.get_all_genres_ordered_by_parameter("id"), label="Жанры", required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control border", "required": False})
    )
    countries = forms.MultipleChoiceField(
        choices=read.get_unique_countries(), label="Страны", required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control border"})
    )
    years = forms.ChoiceField(
        choices=years_range_choice_list, label="Годы выхода фильмов", required=False,
        widget=forms.Select(attrs={"class": "form-control border"})
    )


def define_login_field() -> forms.CharField:
    """Returns a field for entering a login"""
    login_field = forms.CharField(
        label=_("Username"),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": " ",
                "autocomplete": "username",
                "class": "account_input_field"
            }
        )
    )
    return login_field


def define_email_field(custom_label: str = "Email address",
                       custom_class: str = "account_input_field",
                       custom_id: str = "id_user_email",
                       custom_autocomplete: str = "email") -> forms.EmailField:
    """Returns a field for entering an email"""
    email_field = forms.EmailField(
        label=_(f"{custom_label}"),
        min_length=4,
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "required": True,
                "placeholder": " ",
                "autocomplete": f"{custom_autocomplete}",
                "class": f"{custom_class}",
                "id": f"{custom_id}"
            }
        )
    )
    return email_field


def define_password_field(custom_label: str = "Password",
                          custom_class: str = "account_input_field",
                          custom_autocomplete: str = "new-password") -> forms.CharField:
    """Returns a field for entering a password"""
    password_field = forms.CharField(
        label=_(f"{custom_label}"),
        widget=forms.PasswordInput(
            attrs={
                "placeholder": " ",
                "autocomplete": f"{custom_autocomplete}",
                "class": f"{custom_class}"
            }
        )
    )
    return password_field


class RegisterUserForm(SignupForm):
    """Форма регистрации"""
    username = define_login_field()
    email = define_email_field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"] = define_password_field()
        self.fields["password2"] = define_password_field(
            custom_label="Password (again)"
        )


class LoginUserForm(LoginForm):
    """Форма авторизации"""
    password = define_password_field(
        custom_autocomplete="current_password"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"] = define_login_field()


class ResetUserPasswordForm(ResetPasswordForm):
    """Форма сброса пароля"""
    email = define_email_field()


class CryptoCurrencyForm(forms.Form):
    """Форма для выбора количества криптовалюты"""
    crypto_currencies_rows = [
        (10, 10),
        (20, 20),
        (50, 50),
        (100, 100)
    ]
    rows = forms.ChoiceField(
        choices=crypto_currencies_rows, label="Количество криптовалют",
        widget=forms.Select(
            attrs={
                "class": "form-control border select_crypto_currency",
            }
        )
    )
    sorting = forms.CharField(
        widget=forms.HiddenInput(
            attrs={"value": "ascending:0"}
        )
    )
