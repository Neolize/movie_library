from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from modeltranslation.admin import TranslationAdmin

from rating_movies.models import Category, Actor, Genre, Movie, \
    MovieShots, RatingStar, Rating, Review, OtherSourcesRating, UserProfile


class MovieAdminForm(forms.ModelForm):
    """Форма с виджетом ckeditor"""
    description_ru = forms.CharField(widget=CKEditorUploadingWidget(), label="Описание")
    description_en = forms.CharField(widget=CKEditorUploadingWidget(), label="Описание")

    class Meta:
        model = Movie
        fields = "__all__"


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    """Категории"""
    list_display = ("id", "name", "url")
    list_display_links = ("id", "name", "url")
    search_fields = ("name", "url")
    prepopulated_fields = {"url": ("name", )}


@admin.register(Genre)
class GenreAdmin(TranslationAdmin):
    """Жанры"""
    list_display = ("id", "name", "url")
    list_display_links = ("id", "name", "url")
    search_fields = ("name", "url")
    prepopulated_fields = {"url": ("name", )}


class ReviewInline(admin.TabularInline):
    """Отзывы на странице фильма"""
    model = Review
    extra = 1
    readonly_fields = ("name", "email")


class MovieShotsInline(admin.TabularInline):
    """Кадры из фильма на странице фильма"""
    model = MovieShots
    extra = 1
    readonly_fields = ("get_image", )

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f"<img src=\"{obj.image.url}\" width=150 alt=\"\" />")

    get_image.short_description = "Изображение"


@admin.register(Movie)
class MovieAdmin(TranslationAdmin):
    """Фильмы"""
    list_display = ("id", "title", "world_premiere", "country", "get_poster", "url", "draft")
    list_display_links = ("id", "title", "url")
    search_fields = ("title", "description", "category__name", "genres__name")
    list_editable = ("draft", )
    list_filter = ("draft", "year")
    prepopulated_fields = {"url": ("title",)}
    readonly_fields = ("get_poster", )
    inlines = [MovieShotsInline, ReviewInline]
    actions = ["add_to_published", "remove_from_published"]
    save_on_top = True
    save_as = True
    form = MovieAdminForm
    fieldsets = (
        (None, {
            "fields": (("title", "tagline"), )
        }),
        (None, {
            "fields": ("description", ("poster", "get_poster"))
        }),
        (None, {
            "fields": (("year", "world_premiere", "country"),)
        }),
        ("Actors", {
            "classes": ("collapse", ),
            "fields": (("directors", "actors", "genres", "category"), )
        }),
        (None, {
            "fields": (("budget", "fees_in_usa", "fees_in_world"), )
        }),
        ("Options", {
            "fields": (("url", "draft"),)
        })
    )

    def get_poster(self, obj):
        if obj.poster:
            return mark_safe(f"<img src=\"{obj.poster.url}\" width=100 alt=\"\" />")

    def remove_from_published(self, request, queryset):
        """Снять с публикации"""
        row_update = queryset.update(draft=True)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f"{message_bit}")

    def add_to_published(self, request, queryset):
        """Опубликовать"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f"{message_bit}")

    get_poster.short_description = "Постер"

    remove_from_published.short_description = "Снять с публикации"
    remove_from_published.allowed_permissions = ("change",)

    add_to_published.short_description = "Опубликовать"
    add_to_published.allowed_permissions = ("change", )


@admin.register(Actor)
class ActorAdmin(TranslationAdmin):
    """Актёры и режиссёры"""
    list_display = ("id", "name", "age", "get_image", "url")
    list_display_links = ("id", "name", "url")
    search_fields = ("name", "url")
    readonly_fields = ("get_image", )

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f"<img src=\"{obj.image.url}\" width=100 alt=\"\" />")

    get_image.short_description = "Изображение"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Отзывы"""
    list_display = ("id", "name", "email", "parent", "added")
    list_display_links = ("id", "name", "email")
    search_fields = ("name", "email")
    list_filter = ("added", )
    readonly_fields = ("name", "email")


@admin.register(MovieShots)
class MovieShotsAdmin(TranslationAdmin):
    """Кадры из фильма"""
    list_display = ("title", "get_image")
    readonly_fields = ("get_image", )
    save_as = True

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f"<img src=\"{obj.image.url}\" width=100 alt=\"\" />")

    get_image.short_description = "Изображение"


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинг"""
    list_display = ("ip", "movie", "star")


@admin.register(RatingStar)
class RatingStarAdmin(admin.ModelAdmin):
    """Звёзды рейтинга"""
    list_display = ("value", )


@admin.register(OtherSourcesRating)
class OtherSourcesRatingAdmin(admin.ModelAdmin):
    """Movie rating obtained from other sources"""
    list_display = ("id", "movie")
    list_display_links = ("id", "movie")
    

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile"""
    list_display = ("id", "user")
    list_display_links = ("id", "user")


admin.site.site_title = "Django rating movies"
admin.site.site_header = "Django rating movies"
