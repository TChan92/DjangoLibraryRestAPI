from rest_framework.test import APIRequestFactory, APITestCase, APIClient
from django.test import TestCase
from library.models import *
from library.views import *
from library.serializers import *


class TestBookViews(APITestCase):
    """Tests the BookView"""

    def setUp(self):
        self.client = APIClient()

        # Author
        self.author = Author.objects.create(
            name='John Doe'
        )

        self.author2 = Author.objects.create(
            name='Jonah Doe'
        )

        # Genre
        self.genre = Genre.objects.create(
            name='Fiction'
        )

        # Book
        self.book = Book.objects.create(
            id=1,
            isbn='9.78E+12',
            title='Test',
            type='ebook',
            edition='1st',
            pages=123,
            rating=4,
            rating_count=12,
            review_count=123456,
            image_url='http://google.com',
        )
        self.book.author.add(self.author)
        self.book.genre.add(self.genre)
        self.book.save()
        self.inventory = Inventory.objects.create(
            book=self.book,
            owned=1,
            available=1,
        )
        self.book_serialized = BookSerializer(self.book).data

        self.book2 = Book.objects.create(
            id=2,
            isbn='',
            title='Test2',
            type='Hardcover',
            edition='2nd',
            pages=1234,
            rating=5,
            rating_count=1234,
            review_count=1235,
            image_url='Test_URL',
        )
        self.book2.author.add(self.author2)

        self.book2_serialized = BookSerializer(self.book2).data

    def get_request(self, url):
        """
        Send Get request to URL and returns results Checks status code for 200
        :param url: str, url
        :returns: response, respons.data['results']
        """
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        return response, results

    def filter_results(self, url, filter_param):
        """Send Get request with filter"""
        response, results = self.get_request(url + filter_param)

        self.assertEqual(len(results), 1)
        # Here I always filter to find self.book
        self.assertEqual(results[0], self.book_serialized)

    def ordering(self, url, ordering_params, reversed=False):
        """
        Send Get request with sorting
        :param url: str, url
        :param ordering_params: str, field to order on
        :param reversed: bool, whether the results are sorted in reverse order
        """
        response, results = self.get_request('{}?ordering={}'.format(url, ordering_params))

        self.assertEqual(len(results), 2)
        if not reversed:
            self.assertEqual(results[0], self.book_serialized)
            self.assertEqual(results[1], self.book2_serialized)
        else:
            self.assertEqual(results[1], self.book_serialized)
            self.assertEqual(results[0], self.book2_serialized)

    def test_get_listing_all_books(self):
        """Test getting data for all books"""
        response, results = self.get_request('/books/')

        self.assertEqual(results[0], self.book_serialized)
        self.assertEqual(results[1], self.book2_serialized)

    def test_get_all_books_pagination(self):
        """Test that the pagination works"""
        for i in range(API_PAGE_SIZE * 2):
            Book.objects.create(
                isbn='9.78E+12',
                title='Test{}'.format(i),
                type='ebook',
                edition='1st',
                pages=123,
                rating=4,
                rating_count=12,
                review_count=123,
                image_url='TEST_URL'
            )

        response, results = self.get_request('/books/')
        self.assertContains(response, 'next')
        self.assertEqual(len(results), API_PAGE_SIZE)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(response.data['next'], 'http://testserver/books/?page=2')

        response2, results2 = self.get_request(response.data['next'])
        self.assertContains(response2, 'previous')
        self.assertEqual(response2.data['previous'], 'http://testserver/books/')
        self.assertEqual(response2.data['next'], 'http://testserver/books/?page=3')

        response3, results3 = self.get_request(response2.data['next'])
        self.assertContains(response3, 'previous')
        self.assertEqual(response3.data['previous'], 'http://testserver/books/?page=2')
        self.assertEqual(response3.data['next'], None)

    def test_get_detailed_info_for_book(self):
        """Test getting data for a single book"""
        response = self.client.get('/books/1/')

        self.assertEqual(response.status_code, 200)
        results = response.data
        self.assertEqual(results, self.book_serialized)

    def test_filter_isbn(self):
        """Tests filtering by ISBN. Note: Since isbns are all the same or blank, this is kinda pointless"""
        self.filter_results('/books/', '?isbn=9.78E%2B12')

    def test_filter_title(self):
        """Tests filtering by Title"""
        self.filter_results('/books/', '?title=Test')

    def test_filter_type(self):
        """Tests filtering by type"""
        self.filter_results('/books/', '?type=ebook')

    def test_filter_edition(self):
        """Tests filtering by Edition"""
        self.filter_results('/books/', '?edition=1st')

    def test_filter_pages(self):
        """Tests filtering by pages"""
        self.filter_results('/books/', '?pages=123')

    def test_filter_rating(self):
        """Tests filtering by Rating"""
        self.filter_results('/books/', '?rating=4')

    def test_filter_rating_count(self):
        """Tests filtering by count"""
        self.filter_results('/books/', '?rating_count=12')

    def test_filter_review_count(self):
        """Tests filtering by review_count"""
        self.filter_results('/books/', '?review_count=123456')

    def test_filter_author_name(self):
        """Tests filtering by review_count"""
        self.filter_results('/books/', '?author__name=John+Doe')

    def test_filter_genre_name(self):
        """Tests filtering by review_count"""
        self.filter_results('/books/', '?genre__name=Fiction')

    def test_ordering_id(self):
        self.ordering('/books/', 'id')

    def test_ordering_id_reversed(self):
        self.ordering('/books/', '-id', reversed=True)

    def test_ordering_title(self):
        """Test ordering by field"""
        self.ordering('/books/', 'title')

    def test_order_title_reversed(self):
        """Test ordering by field reversed"""
        self.ordering('/books/', '-title', reversed=True)

    def test_ordering_pages(self):
        """Test order by pages"""
        self.ordering('/books/', 'pages')

    def test_ordering_pages_reversed(self):
        """Test ordering by pages reversed"""
        self.ordering('/books/', '-pages', reversed=True)

    def test_ordering_rating(self):
        """Test ordering by rating"""
        self.ordering('/books/', 'rating')

    def test_ordering_rating_reversed(self):
        """Test ordering by rating reversed"""
        self.ordering('/books/', '-rating', reversed=True)

    def test_ordering_edition(self):
        """Test ordering by edition"""
        self.ordering('/books/', 'edition')

    def test_ordering_edition_reversed(self):
        """Test ordering by edition reversed"""
        self.ordering('/books/', '-edition', reversed=True)

    def test_multiple_ordering(self):
        """Test ordering by multiple objects"""
        temp_book = Book.objects.create(
            isbn='9.78E+12',
            title='Test1',
            type='ebook',
            edition='1st',
            pages=123,
            rating=4,
            rating_count=12,
            review_count=123456,
            image_url='http://google.com',
        )
        temp_book_serialized = BookSerializer(temp_book).data
        response, results = self.get_request('/books/?ordering=edition,title')

        self.assertEqual(results[0], self.book_serialized)
        self.assertEqual(results[1], temp_book_serialized)
        self.assertEqual(results[2], self.book2_serialized)

    def test_update_inventory_json(self):
        """Test sending PUT request to update inventory"""
        data = self.book_serialized
        data['inventory']['owned'] = 3
        data['inventory']['available'] = 3
        response = self.client.put('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/books/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['inventory']['owned'], 3)
        self.assertEqual(response.data['inventory']['available'], 3)

    def test_update_inventory_drf_form(self):
        """Test sending PUT request to update inventory"""
        data = self.book_serialized
        data.pop('inventory')
        # How data is from drf html forms
        data['inventory.owned'] = 3
        data['inventory.available'] = 3
        response = self.client.put('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/books/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['inventory']['owned'], 3)
        self.assertEqual(response.data['inventory']['available'], 3)

    def test_update_inventory_invalid(self):
        """Test sending bad data to books"""
        data = self.book_serialized
        data['inventory']['owned'] = 3
        data['inventory']['available'] = 5
        response = self.client.put('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 400)

        response = self.client.get('/books/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['inventory']['owned'], 1)
        self.assertEqual(response.data['inventory']['available'], 1)

    def test_update_title(self):
        """Tests updating the title"""
        data = self.book_serialized
        data['title'] = 'new_title'

        response = self.client.put('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/books/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'new_title')

    def test_update_title_no_inventory_data(self):
        """Tests updating the title"""
        data = self.book_serialized
        data['title'] = 'new_title'
        data.pop('inventory')

        response = self.client.put('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/books/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'new_title')

    def test_update_invalid_inventory_data(self):
        """Tests updating with bad inventory data"""
        data = self.book_serialized
        data['inventory']['owned'] = 0
        response = self.client.put('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 400)

        data['inventory']['available'] = -2
        data['inventory']['owned'] = 1
        response = self.client.put('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 400)

        data['inventory']['available'] = 2
        data['inventory']['owned'] = 1
        response = self.client.put('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_partial_update_title(self):
        """Test updating using PATCH"""
        data = {
            'title': 'new_test_title'
        }
        response = self.client.patch('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/books/1/')
        self.assertEqual(response.data['title'], 'new_test_title')
        self.assertEqual(response.data['rating'], self.book.rating)

    def test_partial_update_available(self):
        """Test updating using PATCH"""
        data = {
            'inventory': {
                'available': 0
            }
        }
        response = self.client.patch('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/books/1/')
        self.assertEqual(response.data['inventory']['available'], 0)
        self.assertEqual(response.data['inventory']['owned'], self.inventory.owned)

    def test_partial_update_available_drf(self):
        """Test updating using PATCH"""
        data = {
            'inventory.available': 0
        }
        response = self.client.patch('/books/1/', data, format='json')

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/books/1/')
        self.assertEqual(response.data['inventory']['available'], 0)
        self.assertEqual(response.data['inventory']['owned'], self.inventory.owned)

    def test_create_book(self):
        data = {
            'title': '123',
            'type': 'ebook',
            'inventory': {
                'owned': 1,
                'available': 1
            }
        }
        response = self.client.post('/books/', data, format='json')

        self.assertEqual(response.status_code, 201)

        response, results = self.get_request('/books/?title=123')
        self.assertEqual(results[0]['title'], '123')
        self.assertEqual(results[0]['type'], 'ebook')
        self.assertEqual(results[0]['inventory']['owned'], 1)
        self.assertEqual(results[0]['inventory']['available'], 1)

    def test_create_book_bad_data(self):
        """Try to create book using None as a title"""
        data = {
            'title': None,
            'type': '',
            'inventory': {
                'owned': 1,
                'available': 1
            }
        }
        response = self.client.post('/books/', data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_create_book_no_inventory(self):
        data = {
            'title': 'test',
            'type': 'ebook',
        }
        response = self.client.post('/books/', data)

        self.assertEqual(response.status_code, 400)

    def test_create_book_invalid_inventory(self):
        data = {
            'title': 'test',
            'type': 'ebook',
            'inventory': {
                'owned': -1,
                'available': 0,
            }
        }
        response = self.client.post('/books/', data, format='json')

        self.assertEqual(response.status_code, 400)

        data = {
            'title': 'test',
            'type': 'ebook',
            'inventory': {
                'owned': 1,
                'available': -2,
            }
        }
        response = self.client.post('/books/', data, format='json')

        self.assertEqual(response.status_code, 400)

        data = {
            'title': 'test',
            'type': 'ebook',
            'inventory': {
                'owned': 1,
                'available': 2,
            }
        }
        response = self.client.post('/books/', data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_delete_book(self):
        response = self.client.delete('/books/1/')

        self.assertEqual(response.status_code, 204)

        response2 = self.client.get('/books/1/')

        self.assertEqual(response2.status_code, 404)

class TestAuthorViews(TestCase):
    """Tests the Author Views"""

    def setUp(self):
        self.client = APIClient()

        # Author
        self.author = Author.objects.create(
            id=1,
            name='John Doe',
        )
        self.author_serialized = AuthorSerializer(self.author).data

        self.author2 = Author.objects.create(
            name='Jane Doe',
        )
        self.author2_serialized = AuthorSerializer(self.author2).data

        # Book
        self.book = Book.objects.create(
            isbn='9.78E+12',
            title='Test',
            type='ebook',
            edition='1st',
            pages=123,
            rating=4,
            rating_count=12,
            review_count=123456,
            image_url='http://google.com',
        )
        self.book.author.add(self.author)
        self.book.save()
        self.book_serialized = BookSerializer(self.book).data

        self.book2 = Book.objects.create(
            isbn='',
            title='Test2',
            type='Hardcover',
            edition='2nd',
            pages=1234,
            rating=5,
            rating_count=1234,
            review_count=1235,
            image_url='Test_URL',
        )

        self.serialized_book2 = BookSerializer(self.book2).data

    def test_filter_name(self):
        """Test filtering by name"""
        response = self.client.get('/authors/?name=John+Doe')

        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(results[0], self.author_serialized)

    def test_nested_books(self):
        """Test getting all the books for an author"""
        response = self.client.get('/authors/1/books/')

        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(results[0], self.book_serialized)

    def test_nested_genres(self):
        """Test getting Genres for an author"""
        genre = Genre.objects.create(
            name='Genre'
        )
        self.book.genre.add(genre)

        response = self.client.get('/authors/1/genres/')

        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(results[0]['name'], 'Genre')

    def test_create_author(self):
        """Creating a new author"""
        response = self.client.post('/authors/', {'name': 'NEW_AUTHOR'})

        self.assertEqual(response.status_code, 201)
        response = self.client.get('/authors/?name=NEW_AUTHOR')
        results = response.data['results']
        self.assertEqual(results[0]['name'], 'NEW_AUTHOR')

    def test_create_author_invalid_request(self):
        """Creating a new author"""
        response = self.client.post('/authors/', {})

        self.assertEqual(response.status_code, 400)

    def test_update_author(self):
        """Test Update with PUT"""
        data = {
            'name': 'updated'
        }
        response = self.client.put('/authors/1/', data, format='json')

        self.assertEqual(response.status_code, 200)

        response = self.client.get('/authors/1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'updated')

    def test_partial_update_author(self):
        """Test Update with PATCH"""
        data = {
            'name': 'New_author'
        }
        response = self.client.patch('/authors/1/', data)

        self.assertEqual(response.status_code, 200)

        response = self.client.get('/authors/1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'New_author')

    def test_delete_author(self):
        """Delete an author"""

        response = self.client.delete('/authors/1/')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('/authors/1/')
        self.assertEqual(response.status_code, 404)


class TestGenreViews(APITestCase):
    """Tests the Genre Views"""

    def setUp(self):
        self.client = APIClient()

        # Author
        self.author = Author.objects.create(
            name='John Doe',
        )
        self.author_serialized = AuthorSerializer(self.author).data

        self.author2 = Author.objects.create(
            name='Jane Doe',
        )
        self.author2_serialized = AuthorSerializer(self.author2).data

        # Genre
        self.genre = Genre.objects.create(
            id=1,
            name='Test_genre',
        )

        self.genre_serialized = GenreSerializer(self.genre).data

        # Book
        self.book = Book.objects.create(
            isbn='9.78E+12',
            title='Test',
            type='ebook',
            edition='1st',
            pages=123,
            rating=4,
            rating_count=12,
            review_count=123456,
            image_url='http://google.com',
        )
        self.book.author.add(self.author)
        self.book.genre.add(self.genre)
        self.book.save()
        self.book_serialized = BookSerializer(self.book).data

        self.book2 = Book.objects.create(
            isbn='',
            title='Test2',
            type='Hardcover',
            edition='2nd',
            pages=1234,
            rating=5,
            rating_count=1234,
            review_count=1235,
            image_url='Test_URL',
        )

        self.serialized_book2 = BookSerializer(self.book2).data

    def get_request(self, url):
        """
        Send Get request to URL and returns results Checks status code for 200
        :param url: str, url
        :returns: response, respons.data['results']
        """
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        return response, results

    def test_filter_name(self):
        """Test filtering by name"""
        response, results = self.get_request('/genres/?name=Test_genre')

        self.assertEqual(results[0], self.genre_serialized)

    def test_nested_books(self):
        """Test getting all the books for a genre"""
        response = self.client.get('/genres/1/books/')

        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(results[0], self.book_serialized)

    def test_nested_genre_pagination(self):
        """Test pagination for nested books for a genre"""
        for i in range(API_PAGE_SIZE * 2):
            book = Book.objects.create(
                isbn='9.78E+12',
                title='Test',
                type='ebook',
                edition='1st',
                pages=123,
                rating=4,
                rating_count=12,
                review_count=123456,
                image_url='http://google.com',
            )
            book.genre.add(self.genre)

        response, results = self.get_request('/genres/1/books/')
        self.assertContains(response, 'next')
        self.assertEqual(len(results), API_PAGE_SIZE)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(response.data['next'], 'http://testserver/genres/1/books/?page=2')

        response2, results2 = self.get_request(response.data['next'])
        self.assertContains(response2, 'previous')
        self.assertEqual(len(results2), API_PAGE_SIZE)
        self.assertNotEqual(results, results2)
        self.assertEqual(response2.data['previous'], 'http://testserver/genres/1/books/')
        self.assertEqual(response2.data['next'], 'http://testserver/genres/1/books/?page=3')

        response3, results3 = self.get_request(response2.data['next'])
        self.assertContains(response3, 'previous')
        self.assertEqual(response3.data['previous'], 'http://testserver/genres/1/books/?page=2')
        self.assertEqual(response3.data['next'], None)

    def test_nested_authors(self):
        """Test getting all the authors for a genre"""
        response, results = self.get_request('/genres/1/authors/')

        self.assertEqual(results[0]['name'], self.author.name)

    def test_create_genre(self):
        """Test Create Genre"""
        data = {
            'name': 'New_Genre'
        }
        response = self.client.post('/genres/', data)

        self.assertEqual(response.status_code, 201)

        response = self.client.get('/genres/?name=New_Genre')

        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(results[0]['name'], 'New_Genre')

    def test_update_genre(self):
        """Test Update with PUT"""
        data = {
            'name': 'New_genre'
        }
        response = self.client.put('/genres/1/', data)

        self.assertEqual(response.status_code, 200)

        response = self.client.get('/genres/1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'New_genre')

    def test_partial_update_genre(self):
        """Test Update with PATCH"""
        data = {
            'name': 'New_genre'
        }
        response = self.client.patch('/genres/1/', data)

        self.assertEqual(response.status_code, 200)

        response = self.client.get('/genres/1/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'New_genre')

    def test_delete_genre(self):
        """Test Delete Genre"""
        response = self.client.delete('/genres/1/')

        self.assertEqual(response.status_code, 204)

        response = self.client.get('/genres/1/')

        self.assertEqual(response.status_code, 404)
