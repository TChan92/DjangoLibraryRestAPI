from rest_framework import serializers
from library.models import *


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'id',
            'name',
        ]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            'id',
            'name',
        ]


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = [
            'available',
            'owned',
        ]

    def create(self, validated_data):
        return Inventory.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.owned = validated_data.get('owned', instance.owned)
        instance.available = validated_data.get('available', instance.available)
        instance.save()
        return instance


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    inventory = InventorySerializer(required=False)

    class Meta:
        model = Book
        fields = [
            'id',
            'isbn',
            'title',
            'type',
            'edition',
            'pages',
            'rating',
            'rating_count',
            'review_count',
            'image_url',
            'description',
            'author',
            'genre',
            'inventory',
        ]
        depth = 1

    def create(self, validated_data):
        # DRF's HTML form passes in '' instead of None, so I have to manually override fields that take int
        pages = validated_data.get('pages', None)
        if pages is '':
            pages = None
        rating = validated_data.get('rating', None)
        if rating is '':
            rating = None
        rating_count = validated_data.get('rating_count', None)
        if rating_count is '':
            rating_count = None
        review_count = validated_data.get('review_count', None)
        if review_count is '':
            review_count = None

        return Book.objects.create(
            isbn=validated_data.get('isbn', ''),
            title=validated_data.get('title'),
            type=validated_data.get('type'),
            edition=validated_data.get('edition', ''),
            pages=pages,
            rating=rating,
            rating_count=rating_count,
            review_count=review_count,
            image_url=validated_data.get('image_url', ''),
            description=validated_data.get('description', ''),
        )

    def update(self, instance, validated_data):
        """ Manually overwrite this to remove inventory information"""
        instance.isbn = validated_data.get('isbn', instance.isbn)
        instance.title = validated_data.get('title', instance.title)
        instance.type = validated_data.get('type', instance.type)
        instance.edition = validated_data.get('edition', instance.edition)
        instance.pages = validated_data.get('pages', instance.pages)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.rating_count = validated_data.get('rating_count', instance.rating_count)
        instance.review_count = validated_data.get('review_count', instance.review_count)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
