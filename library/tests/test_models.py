from django.test import TestCase
from library.models import *


class TestAuthor(TestCase):
    """ Test Author"""

    def setUp(self):
        self.author = Author.objects.create(
            name='Stephen King'
        )
        self.author2 = Author.objects.create(
            name='John Doe'
        )

        self.book_king = Book.objects.create(
            title='Test',
            type='ebook',
            rating=4,
            rating_count=123,
            review_count=123,
            image_url='http://google.com',
        )
        self.book_king.author.add(self.author)

        self.book_doe = Book.objects.create(
            title='Test',
            type='ebook',
            rating=4,
            rating_count=123,
            review_count=123,
            image_url='http://google.com',
        )
        self.book_doe.author.add(self.author2)

        self.book_king_doe = Book.objects.create(
            title='Test',
            type='ebook',
            rating=4,
            rating_count=123,
            review_count=123,
            image_url='http://google.com',
        )
        self.book_king_doe.author.add(self.author, self.author2)

    def test_stringify(self):
        author = Author.objects.get(name='Stephen King')
        self.assertEqual(author.name, str(author))

    def test_get_books_for_author(self):
        books = Book.objects.filter(author=self.author)
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0], self.book_king)
        self.assertEqual(books[1], self.book_king_doe)


class TestGenre(TestCase):
    """Test Genre"""

    def setUp(self):
        self.genre = Genre.objects.create(name='Fantasy')
        self.genre2 = Genre.objects.create(name='Non-Fiction')

        self.book = Book.objects.create(
            title='Test',
            type='ebook',
            rating=4,
            rating_count=123,
            review_count=123,
            image_url='http://google.com',
        )
        self.book.genre.add(self.genre)

        self.book2 = Book.objects.create(
            title='Test',
            type='ebook',
            rating=4,
            rating_count=123,
            review_count=123,
            image_url='http://google.com',
        )
        self.book2.genre.add(self.genre2)

        self.book3 = Book.objects.create(
            title='Test',
            type='ebook',
            rating=4,
            rating_count=123,
            review_count=123,
            image_url='http://google.com',
        )
        self.book3.genre.add(self.genre, self.genre2)

    def test_name(self):
        genre = Genre.objects.get(name='Fantasy')
        self.assertEqual(genre.name, str(genre))

    def test_get_books_for_genre(self):
        books = Book.objects.filter(genre=self.genre)
        self.assertEqual(len(books), 2)
        self.assertEqual(books[0], self.book)
        self.assertEqual(books[1], self.book3)
