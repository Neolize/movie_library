from rest_framework import serializers

from rating_movies import models


class RecursiveReviewSerializer(serializers.Serializer):
    """Recursive output all children comments"""
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class FilterReviewListSerializer(serializers.ListSerializer):
    """Filtering only parent comments"""
    def to_representation(self, data):
        new_data = [data_item for data_item in data if data_item.parent is None]
        return super().to_representation(data=new_data)


class ActorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Actor
        fields = ("id", "name", "age", "image")


class ActorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Actor
        fields = ("id", "name", "age", "description", "birth_date", "death_date", "image", "url")


class ReviewDetailSerializer(serializers.ModelSerializer):
    """Review serializer for MovieDetailSerializer"""
    children_reviews = RecursiveReviewSerializer(many=True, source="review_parent")

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = models.Review
        fields = ("id", "name", "email", "text", "added", "children_reviews")


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = "__all__"


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = "__all__"


class ReviewDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ("pk", )


class MovieListSerializer(serializers.ModelSerializer):
    category_id = serializers.SlugRelatedField(source="category", slug_field="id", read_only=True)
    category_name = serializers.SlugRelatedField(source="category", slug_field="name", read_only=True)
    user_rating = serializers.BooleanField()
    average_rating = serializers.IntegerField()

    class Meta:
        model = models.Movie
        fields = ("id", "title", "tagline", "country", "world_premiere",
                  "url", "category_id", "category_name", "user_rating", "average_rating")


class MovieDetailSerializer(serializers.ModelSerializer):
    actors = ActorListSerializer(many=True, read_only=True)
    directors = ActorListSerializer(many=True, read_only=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    category_id = serializers.SlugRelatedField(source="category", slug_field="id", read_only=True)
    category_name = serializers.SlugRelatedField(source="category", slug_field="name", read_only=True)
    average_rating = serializers.IntegerField()
    reviews = ReviewDetailSerializer(many=True, read_only=True)
    movie_rating = serializers.SlugRelatedField(slug_field="rating", read_only=True, many=True)

    class Meta:
        model = models.Movie
        fields = ("id", "title", "tagline", "description", "year", "country", "world_premiere",
                  "budget", "fees_in_usa", "fees_in_world", "url", "directors", "actors",
                  "genres", "category_id", "category_name", "average_rating", "movie_rating", "reviews")


class RatingUpdateOrCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = ("star", "movie")

    def create(self, validated_data: dict):
        rating, _ = models.Rating.objects.update_or_create(
            ip=validated_data.get("ip", None),
            movie=validated_data.get("movie", None),
            defaults={"star": validated_data.get("star", None)}
        )
        return rating


class RatingDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = ("ip", "movie")


class MovieListForGenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Movie
        fields = ("id", "title")


class GenreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Genre
        fields = ("id", "name", "description", "url")


class GenreDetailSerializer(serializers.ModelSerializer):
    movies = MovieListForGenreSerializer(read_only=True, many=True)

    class Meta:
        model = models.Genre
        fields = ("id", "name", "description", "url", "movies")


class MovieListForCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Movie
        fields = ("id", "title", "url")


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ("id", "name", "description", "url")


class CategoryDetailSerializer(serializers.ModelSerializer):
    movie_category = MovieListForCategorySerializer(read_only=True, many=True)

    class Meta:
        model = models.Category
        fields = ("id", "name", "description", "url", "movie_category")
