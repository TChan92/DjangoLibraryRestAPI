This was a project that I made over a weekend to create a Rest API that could would expose a library database.
The database is populated using book_data.csv

Requirements:
Postgresql (I used 11.4, but any modern version should be fine)
Python (I used 3.7, but 3.6 should also work)
Pip

virtualenv

Install and run (*NIX):
1. Download zip file and extract
2. Go into zip file `cd Library`
3. Set the following Environment Variables
    * `export DB_USER=<postgres_USER>`
    * `export DB_PASS=<postgres_password>`
    * `export DB_HOST=localhost`
    * `DB_PORT=5432`
Replace  variables in <> with appropriate variables
4. Make sure that Postgres has a database named library `CREATE DATABASE library;`
5. Create a virtual environment `virtualenv venv`
6. Install requirements with `pip install -r requirements.txt`
7. Run Django's migrations to setup database `python manage.py migrate`
8. Load data from book_data.csv `python manage.py load_book_data book_data.csv`
9. Runserver `python manage.py runserver`

My code is tested, with library/tests/test_views.py covering most of the rest api. Both views.py and serializers.py both have very high unit test coverage
`python manage.py test`

Examples of usage:
Get listing of all books:
http://localhost:8000/books/

Get detailed information about a single book:
http://localhost:8000/books/1/

Both listing books and getting detailed information about a single book return the same number of fields for consistency.
The information is paginated to prevent too much information from being returned at once. 

Filter and sort (Sorting is done by ?ordering=<param>):

Author can be filtered and sorted on 'name'

Genre can be filtered and sorted on 'name'

Book can be filtered on 'isbn', 'title', 'type', 'edition', 'pages', 'rating', 'rating_count', 'review_count', 'author__name', 'genre__name', 

Book can be sorted on 'id', 'title', 'pages', 'ratings', 'edition'

Examples:
* http://localhost:8000/books/?title=Circe
* http://localhost:8000/books/?author__name=Stephen+King&ordering=pages

Examples of checking a book out of the library and returning using put or patch can be found in demo_api.py

List all authors:
http://localhost:8000/authors/

List all Genres:
http://localhost:8000/genres/

Nested resources are supported on Author and Genre endpoints
Examples:
* http://localhost:8000/authors/1/books/  Lists all the books for author 1
* http://localhost:8000/genres/1/books/   Lists all the books for genre 1
* http://localhost:8000/authors/1/genres/ Lists all the genres that author 1 has written
* http://localhost:8000/genres/1/authors/ Lists all the Authors that have written for books for Genre 1


CRUD is supported on Authors, Genres and Books
Examples can be found in demo_api.py
PUT can only be used for updating at this time and not creating.
Author and Genres require {'name': 'name'} to create

Books can take{'title': 'title', 'type': <type>, 'inventory': {'owned': int, 'available': int}}
valid types are 'Kindle Edition', 'Hardcover', 'ebook', 'Paperback'

title, type and inventory dict are required

Notes:
* Django Rest Framework was used because of the many benefits that it provides (Browsable API, documentation, support).
* Since this API does not support users, it would only be suitable for internal use.
* If it were to be made suitable for external use, users and authentication would have to be supported.
* Also if this were a real application I would prepend /api/<api_version>/ on all of the api endpoints, but since this is only api and won't change, I didn't bother. 
* I had considered a checkout action so /books/1/checkout/ would checkout the book, but I decided that wasn't restful and removed it.
