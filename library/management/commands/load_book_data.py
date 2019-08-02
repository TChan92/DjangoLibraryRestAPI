import csv
import random
from django.core.management import BaseCommand
from library.models import *


def __get_authors(row):
    """
    Gets one or more Author objects corresponding to the field for a single row
    :param row: Series
    :return: list of Author objects
    """
    authors_list = row['book_authors'].split('|')

    authors = []

    for author in authors_list:
        author_object, created = Author.objects.get_or_create(
            name=author
        )

        authors.append(author_object)

    return authors


def __get_genres(row):
    """
    Gets one or more Genre objects corresponding to the field for a single row
    :param row: Series
    :return: list of Genre objects
    """
    genres_list = row['genres'].split('|')

    genres = []

    for genre in genres_list:
        genre_object, create = Genre.objects.get_or_create(
            name=genre
        )

        genres.append(genre_object)

    return genres


def __get_pages(row):
    """
    Gets rid of the <space>pages
    :param row: Series
    :return: int or None
    """
    pages = row['book_pages']
    if len(pages) > 0:
        pages = pages.split(' ')[0]  # First number as string
        pages = int(pages)
    else:
        pages = None
    return pages


def load_csv(data_csv):
    """
    Loads the data for a csv similar to book_data
    :param data_csv: str, path to book_data.csv or equivalent
    """

    with open(data_csv, 'r') as csv_file:
        reader = csv.DictReader(csv_file, quotechar='"')

        for row in reader:

            # This is wrapped in a try except so that if a single line fails, the rest of the rows are still loaded.
            # If the desired behavior is to instead have the entire load fail on a single error, this should be replaced
            # with from "django.db import transaction" at the top and with transaction.atomic() instead of try-except
            try:
                authors = __get_authors(row)

                genres = __get_genres(row)

                description = row['book_desc']

                edition = row['book_edition']

                format = row['book_format']

                isbn = row['book_isbn']

                pages = __get_pages(row)

                rating = float(row['book_rating'])

                rating_count = int(row['book_rating_count'])

                review_count = int(row['book_review_count'])

                title = row['book_title']

                image_url = row['image_url']

                book, created = Book.objects.get_or_create(
                    isbn=isbn,
                    title=title,
                    type=format,
                    edition=edition,
                    pages=pages,
                    rating=rating,
                    rating_count=rating_count,
                    review_count=review_count,
                    image_url=image_url,
                    description=description,
                )
                book.save()

                for author in authors:
                    book.author.add(author)
                for genre in genres:
                    book.genre.add(genre)

                book.save()

                copies = random.randint(1, 5)
                inventory = Inventory.objects.filter(book=book)
                if not inventory.exists():
                    inventory = Inventory.objects.create(
                        book=book,
                        available=copies,
                        owned=copies,
                    )

            except Exception as e:
                print('Row could not be loaded due to {}: {}'.format(e, row))

    print('Finished loading')


class Command(BaseCommand):
    help = 'Loads the data from book_data.csv'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', help='path to book_data.csv or equivalent')

    def handle(self, *args, **options):
        load_csv(options['csv_file'])
