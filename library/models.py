from django.db import models


class Author(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Book(models.Model):
    # Ideally isbn should be BigIntegerField with unique=True, but:
    # 1. all the ISBN's in the book_data.csv are the same
    # 2. There is a bunch of blank entries for ISBN
    isbn = models.CharField(max_length=20, blank=True)  # max_length is 20 to account for dashes
    title = models.TextField()
    # ASSUMPTION: These are the only formats which will be loaded
    TYPES = [
        ('Kindle Edition', 'Kindle Edition'),
        ('Hardcover', 'Hardcover'),
        ('ebook', 'ebook'),
        ('Paperback', 'Paperback'),
    ]
    type = models.CharField(choices=TYPES, blank=True, max_length=25)
    edition = models.TextField(blank=True)
    pages = models.IntegerField(null=True)
    rating = models.FloatField(null=True)
    rating_count = models.IntegerField(null=True)
    review_count = models.IntegerField(null=True)
    image_url = models.TextField(blank=True)
    description = models.TextField(blank=True)

    author = models.ManyToManyField(Author)
    genre = models.ManyToManyField(Genre)


class Inventory(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    available = models.PositiveIntegerField()
    owned = models.PositiveIntegerField()

