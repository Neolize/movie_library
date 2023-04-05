from django.urls import path

from rating_movies import views


urlpatterns = [
    path("", views.MoviesView.as_view(), name="home"),
    path("filtering/", views.JsonFilteringMoviesView.as_view(), name="filtering"),
    path("sorting", views.JsonSortingMoviesView.as_view(), name="sorting"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("actors_and_directors/", views.ActorsDirectorsView.as_view(), name="actors_directors"),
    path("categories/", views.CategoriesView.as_view(), name="categories"),
    path("genres/", views.GenresView.as_view(), name="genres"),

    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("genre/<slug:slug>/", views.GenreDetailView.as_view(), name="genre_detail"),
    path("movie/<slug:slug>/", views.MovieDetailView.as_view(), name="movie_detail"),
    path("actor_director/<slug:slug>/", views.ActorDirectorDetailView.as_view(), name="actor_director_detail"),

    path("random_movies/", views.RandomMoviesView.as_view(), name="random_movies"),
    path("weather/", views.WeatherView.as_view(), name="weather"),
    path("crypto_currency/", views.CryptoCurrencyView.as_view(), name="crypto_currency"),
    path("currency/", views.CurrencyView.as_view(), name="currency"),
    path("random_password/", views.RandomPasswordView.as_view(), name="random_password"),

    path("review/<int:pk>/", views.AddReviewView.as_view(), name="add_review"),
    path("add/actor_director/", views.AddActorDirectorView.as_view(), name="add_actor_director"),
    path("add/category/", views.AddCategoryView.as_view(), name="add_category"),
    path("add/genre/", views.AddGenreView.as_view(), name="add_genre"),
    path("add/movie/", views.AddMovieView.as_view(), name="add_movie"),
    path("add/movie_shots/", views.AddMovieShotView.as_view(), name="add_movie_shots"),
    path("add/rating_star/", views.AddRatingStar.as_view(), name="add_rating_star"),
    path("add/rating/", views.AddRating.as_view(), name="add_rating"),

    path("update/movie/<slug:slug>/", views.UpdateMovieView.as_view(), name="update_movie"),
    path("update/actor_director/<slug:slug>/", views.UpdateActorDirectorView.as_view(), name="update_actor_director"),

    path("delete/actor_director/<slug:slug>/", views.DeleteActorDirectorView.as_view(), name="delete_actor_director"),

    path("signup/", views.RegisterUserView.as_view(), name="signup"),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("password/reset/", views.UserPasswordResetView.as_view(), name="password_reset"),
    path("logout/", views.LogoutUserView.as_view(), name="logout"),
    path("socialaccount/login/", views.SocialAccountLoginUserView.as_view(), name="socialaccount_login"),

    path("user_profile/", views.UserProfileView.as_view(), name="user_profile"),
    path("movie/<slug:movie_slug>/add_to_watchlist/", views.add_movie_to_watchlist_view, name="add_to_watchlist"),

    path("add/phone_mask/", views.show_phone_mask, name="phone_mask"),

    path("page_not_found/", views.show_beautiful_page_not_found, name="page_not_found"),
]
