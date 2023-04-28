import json
from datetime import date
from time import time

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify as django_slugify


def get_current_year():
    return date.today().year


def is_unique_url(model: any, url: str) -> bool:
    if model.objects.filter(url__iexact=url).exists():
        return False
    return True


def slugify(some_str: str):
    alphabet = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
                "й": "j", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
                "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch", "ы": "i", "э": "e",
                "ю": "yu",
                "я": "ya"}
    return django_slugify("".join(alphabet.get(letter, letter) for letter in some_str.lower()))


def generate_unique_slug(slug: str):
    return f"{slug}-{int(time())}"


class Category(models.Model):
    """Категории"""
    name = models.CharField("Категория", max_length=150, db_index=True)
    description = models.TextField("Описание", blank=True)
    url = models.SlugField(max_length=160, unique=True)

    class Meta:
        db_table = "Category"
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.url})


class Actor(models.Model):
    """Актёры и режиссёры"""
    name = models.CharField("Имя", max_length=100, db_index=True)
    age = models.PositiveSmallIntegerField("Возраст", default=0)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="actors/%Y/%m/%d/")
    url = models.SlugField(max_length=160, unique=True, blank=True)
    birth_date = models.DateField("Дата рождения", default=date.today)
    death_date = models.DateField("Дата смерти", blank=True, null=True)

    class Meta:
        db_table = "Actor"
        verbose_name = "Актёры и режиссёры"
        verbose_name_plural = "Актёры и режиссёры"
        ordering = ["id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.update_age()
        if not self.pk:
            self.url = slugify(str(self.name))
            if not is_unique_url(model=Actor, url=self.url):
                self.url = generate_unique_slug(slug=self.url)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("actor_director_detail", kwargs={"slug": self.url})

    def get_update_url(self):
        return reverse("update_actor_director", kwargs={"slug": self.url})

    def get_delete_url(self):
        return reverse("delete_actor_director", kwargs={"slug": self.url})

    def update_age(self):
        """Add or update actor/director age by subtracting birth_date from death_date or today's date"""
        if self.death_date:
            time_delta = self.death_date - self.birth_date
        else:
            time_delta = date.today() - self.birth_date

        self.age = int(time_delta.days / 365)


class Genre(models.Model):
    """Жанры"""
    name = models.CharField("Имя", max_length=100)
    description = models.TextField("Описание", blank=True)
    url = models.SlugField(max_length=160, unique=True)

    class Meta:
        db_table = "Genre"
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ["id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("genre_detail", kwargs={"slug": self.url})


class Movie(models.Model):
    """Фильмы"""
    title = models.CharField("Название", max_length=100, db_index=True)
    tagline = models.CharField("Слоган", max_length=150, default="")
    description = models.TextField("Описание", blank=True)
    poster = models.ImageField("Постер", upload_to="movies/%Y/%m/%d/")
    year = models.PositiveSmallIntegerField("Дата выхода",
                                            default=get_current_year)
    country = models.CharField("Страна", max_length=50)
    directors = models.ManyToManyField("Actor", verbose_name="Режиссёр",
                                       related_name="movie_director")
    actors = models.ManyToManyField("Actor", verbose_name="Актёры",
                                    related_name="movie_actor")
    genres = models.ManyToManyField("Genre", verbose_name="Жанры",
                                    related_name="movie_genre")
    world_premiere = models.DateField("Премьера в мире", default=date.today)
    budget = models.PositiveBigIntegerField("Бюджет", default=0,
                                            help_text="Указывать сумму в долларах")
    fees_in_usa = models.PositiveBigIntegerField(
        "Сборы в США", default=0, help_text="Указывать сумму в долларах")
    fees_in_world = models.PositiveBigIntegerField(
        "Сборы в мире", default=0, help_text="Указывать сумму в долларах")
    category = models.ForeignKey(
        "Category", verbose_name="Категория", on_delete=models.SET_NULL,
        null=True, related_name="movie_category")
    url = models.SlugField(max_length=160, unique=True, blank=True)
    draft = models.BooleanField("Черновик", default=False)

    class Meta:
        db_table = "Movie"
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            self.add_url()
            self.add_year()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("movie_detail", kwargs={"slug": self.url})

    def get_update_url(self):
        return reverse("update_movie", kwargs={"slug": self.url})

    def add_url(self) -> None:
        self.url = slugify(str(self.title))
        if not is_unique_url(model=Movie, url=self.url):
            self.url = generate_unique_slug(slug=self.url)

    def add_year(self):
        self.year = str(self.world_premiere).split("-")[0]


class MovieShots(models.Model):
    """Кадры из фильма"""
    title = models.CharField("Заголовок", max_length=100)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="movie_shots/%Y/%m/%d/")
    movie = models.ForeignKey(
        "Movie", verbose_name="Фильм", on_delete=models.CASCADE)

    class Meta:
        db_table = "MovieShots"
        verbose_name = "Кадр из фильма"
        verbose_name_plural = "Кадры из фильма"

    def __str__(self):
        return self.title


class RatingStar(models.Model):
    """Звезда рейтинга"""
    value = models.SmallIntegerField("Значение", default=0, unique=True)

    class Meta:
        db_table = "RatingStar"
        verbose_name = "Звезда рейтинга"
        verbose_name_plural = "Звёзды рейтинга"
        ordering = ["-value"]

    def __str__(self):
        return f"{self.value}"


class Rating(models.Model):
    """Рейтинг"""
    ip = models.CharField("IP адрес", max_length=15)
    star = models.ForeignKey("RatingStar", on_delete=models.CASCADE, verbose_name="Звезда")
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE, verbose_name="Фильм")

    class Meta:
        db_table = "Rating"
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"

    def __str__(self):
        return f"{self.star} - {self.movie}"


class Review(models.Model):
    """Отзыв"""
    email = models.EmailField("Email")
    name = models.CharField("Имя", max_length=100)
    text = models.TextField("Сообщение", max_length=5000)
    added = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", verbose_name="Родитель", related_name="review_parent",
                               on_delete=models.SET_NULL, blank=True, null=True)
    movie = models.ForeignKey("Movie", verbose_name="Фильм", on_delete=models.CASCADE)

    class Meta:
        db_table = "Review"
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.name} - {self.movie}"


class OtherSourcesRating(models.Model):
    """Movie rating obtained from other sources"""
    rating = models.JSONField("Рейтинг", encoder=json.JSONEncoder, decoder=json.JSONDecoder, default=None)
    movie = models.ForeignKey("Movie", verbose_name="Фильм", on_delete=models.CASCADE, related_name="movie_rating")

    class Meta:
        db_table = "OtherSourcesRating"
        verbose_name = "Рейтинг из других источников"
        verbose_name_plural = "Рейтинги из других источников"

    def __str__(self):
        return f"{self.movie} - {self.rating}"


class UserProfile(models.Model):
    """Extending the "User" model"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_profile")
    movies = models.ManyToManyField(
        "Movie",
        through="UserProfileMovie",
        verbose_name="Фильмы",
        related_name="user_movies",
        blank=True,
    )

    class Meta:
        db_table = "UserProfile"
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        movies = self.movies.count()
        template = "movie" if movies == 1 else "movies"
        return f"User \"{self.user}\" has {movies} {template}"


class UserProfileMovie(models.Model):
    """Intermediate model for "UserProfile" """
    user_profile = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="user_profile_movie",)
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE,  related_name="user_movie",)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "UserProfileMovie"

    def __str__(self):
        return f"User_profile: {self.user_profile}; movie: {self.movie};  added: {self.added}"
