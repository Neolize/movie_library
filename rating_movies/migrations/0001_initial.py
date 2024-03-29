# Generated by Django 4.0.3 on 2023-04-08 07:52

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import json.decoder
import json.encoder
import rating_movies.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Имя')),
                ('name_ru', models.CharField(db_index=True, max_length=100, null=True, verbose_name='Имя')),
                ('name_en', models.CharField(db_index=True, max_length=100, null=True, verbose_name='Имя')),
                ('age', models.PositiveSmallIntegerField(default=0, verbose_name='Возраст')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('description_ru', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('image', models.ImageField(upload_to='actors/%Y/%m/%d/', verbose_name='Изображение')),
                ('url', models.SlugField(blank=True, max_length=160, unique=True)),
                ('birth_date', models.DateField(default=datetime.date.today, verbose_name='Дата рождения')),
            ],
            options={
                'verbose_name': 'Актёры и режиссёры',
                'verbose_name_plural': 'Актёры и режиссёры',
                'db_table': 'Actor',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=150, verbose_name='Категория')),
                ('name_ru', models.CharField(db_index=True, max_length=150, null=True, verbose_name='Категория')),
                ('name_en', models.CharField(db_index=True, max_length=150, null=True, verbose_name='Категория')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('description_ru', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('url', models.SlugField(max_length=160, unique=True)),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'db_table': 'Category',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Имя')),
                ('name_en', models.CharField(max_length=100, null=True, verbose_name='Имя')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('description_ru', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('url', models.SlugField(max_length=160, unique=True)),
            ],
            options={
                'verbose_name': 'Жанр',
                'verbose_name_plural': 'Жанры',
                'db_table': 'Genre',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=100, verbose_name='Название')),
                ('title_ru', models.CharField(db_index=True, max_length=100, null=True, verbose_name='Название')),
                ('title_en', models.CharField(db_index=True, max_length=100, null=True, verbose_name='Название')),
                ('tagline', models.CharField(default='', max_length=150, verbose_name='Слоган')),
                ('tagline_ru', models.CharField(default='', max_length=150, null=True, verbose_name='Слоган')),
                ('tagline_en', models.CharField(default='', max_length=150, null=True, verbose_name='Слоган')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('description_ru', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('poster', models.ImageField(upload_to='movies/%Y/%m/%d/', verbose_name='Постер')),
                ('year', models.PositiveSmallIntegerField(default=rating_movies.models.get_current_year, verbose_name='Дата выхода')),
                ('country', models.CharField(max_length=50, verbose_name='Страна')),
                ('country_ru', models.CharField(max_length=50, null=True, verbose_name='Страна')),
                ('country_en', models.CharField(max_length=50, null=True, verbose_name='Страна')),
                ('world_premiere', models.DateField(default=datetime.date.today, verbose_name='Премьера в мире')),
                ('budget', models.PositiveBigIntegerField(default=0, help_text='Указывать сумму в долларах', verbose_name='Бюджет')),
                ('fees_in_usa', models.PositiveBigIntegerField(default=0, help_text='Указывать сумму в долларах', verbose_name='Сборы в США')),
                ('fees_in_world', models.PositiveBigIntegerField(default=0, help_text='Указывать сумму в долларах', verbose_name='Сборы в мире')),
                ('url', models.SlugField(blank=True, max_length=160, unique=True)),
                ('draft', models.BooleanField(default=False, verbose_name='Черновик')),
                ('actors', models.ManyToManyField(related_name='movie_actor', to='rating_movies.actor', verbose_name='Актёры')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movie_category', to='rating_movies.category', verbose_name='Категория')),
                ('directors', models.ManyToManyField(related_name='movie_director', to='rating_movies.actor', verbose_name='Режиссёр')),
                ('genres', models.ManyToManyField(related_name='movie_genre', to='rating_movies.genre', verbose_name='Жанры')),
            ],
            options={
                'verbose_name': 'Фильм',
                'verbose_name_plural': 'Фильмы',
                'db_table': 'Movie',
            },
        ),
        migrations.CreateModel(
            name='RatingStar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(default=0, unique=True, verbose_name='Значение')),
            ],
            options={
                'verbose_name': 'Звезда рейтинга',
                'verbose_name_plural': 'Звёзды рейтинга',
                'db_table': 'RatingStar',
                'ordering': ['-value'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Профиль пользователя',
                'verbose_name_plural': 'Профили пользователей',
                'db_table': 'UserProfile',
            },
        ),
        migrations.CreateModel(
            name='UserProfileMovie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_movie', to='rating_movies.movie')),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile_movie', to='rating_movies.userprofile')),
            ],
            options={
                'db_table': 'UserProfileMovie',
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='movies',
            field=models.ManyToManyField(blank=True, related_name='user_movies', through='rating_movies.UserProfileMovie', to='rating_movies.movie', verbose_name='Фильмы'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('name', models.CharField(max_length=100, verbose_name='Имя')),
                ('text', models.TextField(max_length=5000, verbose_name='Сообщение')),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rating_movies.movie', verbose_name='Фильм')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='review_parent', to='rating_movies.review', verbose_name='Родитель')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'db_table': 'Review',
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=15, verbose_name='IP адрес')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rating_movies.movie', verbose_name='Фильм')),
                ('star', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rating_movies.ratingstar', verbose_name='Звезда')),
            ],
            options={
                'verbose_name': 'Рейтинг',
                'verbose_name_plural': 'Рейтинги',
                'db_table': 'Rating',
            },
        ),
        migrations.CreateModel(
            name='OtherSourcesRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.JSONField(decoder=json.decoder.JSONDecoder, default=None, encoder=json.encoder.JSONEncoder, verbose_name='Рейтинг')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movie_rating', to='rating_movies.movie', verbose_name='Фильм')),
            ],
            options={
                'verbose_name': 'Рейтинг из других источников',
                'verbose_name_plural': 'Рейтинги из других источников',
                'db_table': 'OtherSourcesRating',
            },
        ),
        migrations.CreateModel(
            name='MovieShots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок')),
                ('title_ru', models.CharField(max_length=100, null=True, verbose_name='Заголовок')),
                ('title_en', models.CharField(max_length=100, null=True, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('description_ru', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('image', models.ImageField(upload_to='movie_shots/%Y/%m/%d/', verbose_name='Изображение')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rating_movies.movie', verbose_name='Фильм')),
            ],
            options={
                'verbose_name': 'Кадр из фильма',
                'verbose_name_plural': 'Кадры из фильма',
                'db_table': 'MovieShots',
            },
        ),
    ]
