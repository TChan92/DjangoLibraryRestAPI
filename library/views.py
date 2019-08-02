from copy import deepcopy

from django.core.paginator import Paginator
from rest_framework import viewsets, generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from library.models import *
from library.serializers import *
from Library.settings import API_PAGE_SIZE

# HOST = 'http://localhost:8000'


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().order_by('id')
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name']
    ordering_fields = ['name']

    @action(methods=['get'], detail=True)
    def books(self, request, pk=None):
        author = self.get_object()
        books = author.book_set.all().order_by('id')
        books_paginator = Paginator(books, API_PAGE_SIZE)

        count = books.count()

        # Set Pagination Info
        path = 'http://{}/authors/{}/books/'.format(request.get_host(), pk)
        page = request.query_params.get('page', '1')
        page = int(page)
        # Get Paginated Results
        books = books_paginator.page(page)
        serializer = BookSerializer(books, many=True)

        # Calculate Page
        if page * API_PAGE_SIZE < count:
            next_page = path + '?page={}'.format(page + 1)
        else:
            next_page = None

        if page > 2:
            prev_page = path + '?page={}'.format(page - 1)
        elif page == 2:
            prev_page = path
        else:
            prev_page = None

        return Response({
            'count': count,
            'next': next_page,
            'previous': prev_page,
            'results': serializer.data,
        })

    @action(methods=['get'], detail=True)
    def genres(self, request, pk=None):
        author = self.get_object()
        genres = Genre.objects.filter(book__author=author).order_by('id')
        genres_paginator = Paginator(genres, API_PAGE_SIZE)

        count = genres.count()

        # Set Pagination Info
        path = 'http://{}/authors/{}/genres/'.format(request.get_host(), pk)
        page = request.query_params.get('page', '1')
        page = int(page)
        # Get Paginated Results
        genres = genres_paginator.page(page).object_list
        serializer = GenreSerializer(genres, many=True)

        # Calculate Page
        if page * API_PAGE_SIZE < count:
            next_page = path + '?page={}'.format(page + 1)
        else:
            next_page = None

        if page > 2:
            prev_page = path + '?page={}'.format(page - 1)
        elif page == 2:
            prev_page = path
        else:
            prev_page = None

        return Response({
            'count': count,
            'next': next_page,
            'previous': prev_page,
            'results': serializer.data,
        })


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('id')
    serializer_class = GenreSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name']
    ordering_fields = ['name']

    @action(methods=['get'], detail=True)
    def books(self, request, pk=None):
        genre = self.get_object()
        books = genre.book_set.all().order_by('id')
        books_paginator = Paginator(books, API_PAGE_SIZE)

        count = books.count()

        # Set Pagination Info
        path = 'http://{}/genres/{}/books/'.format(request.get_host(), pk)
        page = request.query_params.get('page', '1')
        page = int(page)
        # Get Paginated Results
        books = books_paginator.page(page)
        serializer = BookSerializer(books, many=True)

        if page * API_PAGE_SIZE < count:
            next_page = path + '?page={}'.format(page + 1)
        else:
            next_page = None

        if page > 2:
            prev_page = path + '?page={}'.format(page - 1)
        elif page == 2:
            prev_page = path
        else:
            prev_page = None

        return Response({
            'count': count,
            'next': next_page,
            'previous': prev_page,
            'results': serializer.data,
        })

    @action(methods=['get'], detail=True)
    def authors(self, request, pk=None):
        genre = self.get_object()
        authors = Author.objects.filter(book__genre=genre).order_by('id')
        authors_paginator = Paginator(authors, API_PAGE_SIZE)

        count = authors.count()

        # Set Pagination Info
        path = 'http://{}/genres/{}/authors/'.format(request.get_host(), pk)
        page = request.query_params.get('page', '1')
        page = int(page)
        # Get Paginated Results
        authors = authors_paginator.page(page).object_list
        serializer = GenreSerializer(authors, many=True)

        # Calculate Page
        if page * API_PAGE_SIZE < count:
            next_page = path + '?page={}'.format(page + 1)
        else:
            next_page = None

        if page > 2:
            prev_page = path + '?page={}'.format(page - 1)
        elif page == 2:
            prev_page = path
        else:
            prev_page = None

        return Response({
            'count': count,
            'next': next_page,
            'previous': prev_page,
            'results': serializer.data,
        })


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('id')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'isbn',
        'title',
        'type',
        'edition',
        'pages',
        'rating',
        'rating_count',
        'review_count',
        'author__name',
        'genre__name',
    ]
    ordering_fields = [
        'id',
        'title',
        'pages',
        'rating',
        'edition',
    ]

    @staticmethod
    def valid_inventory(inventory_data):
        """Tests validity of owned and availasble"""
        if inventory_data['owned'] < 1:
            return False
        if inventory_data['available'] < 0:
            return False
        if inventory_data['owned'] < inventory_data['available']:
            return False
        return True

    @staticmethod
    def __standardize_inventory(request_data):
        """
        DRF's HTML form passes in inventory.owned and inventory.available instead of inventory as a dictionary.
        This method standardizes it
        """

        if 'inventory.owned' in request_data or 'inventory.available' in request_data:
            inventory_data = {}
            if 'inventory.available' in request_data:
                inventory_data['available'] = request_data['inventory.available']

            if 'inventory.owned' in request_data:
                inventory_data['owned'] = request_data['inventory.owned']

            request_data['inventory'] = inventory_data


    # Needed to be overwritten because of nested serializer
    def create(self, request, *args, **kwargs):
        # Create mutable version of request.data
        request_data = deepcopy(request.data)

        # Standardize difference between normal json data and DRF HTML form data
        self.__standardize_inventory(request_data)

        # Check that Inventory data is passed in
        if 'inventory' not in request_data:
            data = {
                'reason': 'inventory dictionary with owned and available must be part of the request data',
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Used for creating Inventory
        inventory_data = {
            'owned': request_data['inventory']['owned'],
            'available': request_data['inventory']['available'],
        }
        if not self.valid_inventory(inventory_data):
            data = {
                       'reason': 'Invalid owned or available.'
                   },
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Try to create book
        try:
            book = BookSerializer().create(request_data)
        except Exception as e:
            data = {
                'reason': 'Invalid book data'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # Give inventory_data the Book object and create Inventory object
        inventory_data['book'] = book
        InventorySerializer().create(inventory_data)

        return Response({'status': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)

    # Needed to be overwritten because of nested serializer
    def update(self, request, *args, **kwargs):
        # Create mutable version of request.data
        request_data = deepcopy(request.data)

        book = Book.objects.get(pk=kwargs['pk'])

        # If not updating Inventory information, then need to get current Inventory Information
        if not self.__updating_inventory(request_data):
            inventory = Inventory.objects.get(book=book)
            request_data['inventory'] = InventorySerializer(inventory).data

        # Save Book Information
        book_serializer = BookSerializer(book, data=request_data)
        if not book_serializer.is_valid():
            return Response({'reason': 'Invalid Book Data'}, status=status.HTTP_400_BAD_REQUEST)
        book_serializer.save()

        # If updating Inventory Information
        if self.__updating_inventory(request_data):
            # Standardize difference between normal json data and DRF HTML form data
            self.__standardize_inventory(request_data)

            # Create dict to hold inventory data only
            inventory_data = {
                'owned': request_data['inventory']['owned'],
                'available': request_data['inventory']['available'],
            }
            if not self.valid_inventory(inventory_data):
                data = {
                           'reason': 'Invalid inventory data.'
                       },
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            inventory = Inventory.objects.get(book=book)

            inventory_serializer = InventorySerializer(inventory, data=inventory_data)

            # Check data validity
            if not (inventory_serializer.is_valid()):
                data = {
                    'reason': 'Invalid inventory data.'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            # Update Inventory
            inventory_serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def __updating_inventory(request_data):
        """Checks whether the user has passed in inventory data and is updating inventory"""
        return 'inventory' in request_data or \
               'inventory.owned' in request_data or \
               'inventory.available' in request_data

    # Needed to be overwritten because of nested serializer
    def partial_update(self, request, *args, **kwargs):
        # Create mutable version of request.data
        request_data = deepcopy(request.data)

        book = Book.objects.get(pk=kwargs['pk'])

        # If not updating Inventory information, then need to get current Inventory Information
        if not self.__updating_inventory(request_data):
            inventory = Inventory.objects.get(book=book)
            request_data['inventory'] = InventorySerializer(inventory).data

        # Save Book Information
        book_serializer = BookSerializer(book, data=request_data, partial=True)
        if not book_serializer.is_valid():
            return Response({'reason': 'Invalid Book Data'}, status=status.HTTP_400_BAD_REQUEST)
        book_serializer.save()

        # If updating Inventory Information
        if self.__updating_inventory(request_data):
            # Standardize difference between normal json data and DRF HTML form data
            self.__standardize_inventory(request_data)

            # Handle passed in inventory data
            inventory_data = {}
            if 'owned' in request_data['inventory']:
                inventory_data['owned'] = request_data['inventory']['owned']
            if 'available' in request_data['inventory']:
                inventory_data['available'] = request_data['inventory']['available']
            inventory = Inventory.objects.get(book=book)

            inventory_serializer = InventorySerializer(inventory, data=inventory_data, partial=True)

            # Check data validity
            if not (inventory_serializer.is_valid()):
                data = {
                    'reason': 'Invalid inventory data.'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            # Update Inventory
            inventory_serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
