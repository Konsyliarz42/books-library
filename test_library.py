import unittest, faker, random
from flask import Flask
from flask_testing import TestCase

from library import database, app

#================================================================
def list_of_authors(quantity):
    fake    = faker.Faker()
    authors = list()

    for _ in range(quantity):
        authors.append({
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'birth': str(fake.date()),
            'death': str(fake.date())
        })
    
    return authors

#--------------------------------
def list_of_books(quantity):
    fake    = faker.Faker()
    books   = list()

    for _ in range(quantity):
        authors_list = list()

        for __ in range(random.randint(1, 5)):
            authors_list.append(fake.name())

        books.append({
            'title': fake.company(),
            'premiere': str(fake.date()),
            'price': random.random(),
            'authors': authors_list
        })

    return books

#================================================================
class TestLibrary(TestCase):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    #--------------------------------
    def create_app(self):
        return app

    #--------------------------------
    def setUp(self):
        database.create_all()

    #--------------------------------
    def tearDown(self):
        database.session.remove()
        database.drop_all()

#----------------------------------------------------------------

    # Get all books from database
    def test_get_books(self):
        for book in list_of_books(30):
            self.client.post("/books", json=book)

        response = self.client.get("/books")
        self.assertEqual(response.status_code, 200)

    # Add new book to database
    def test_post_book(self):
        book        = list_of_books(1)[0]
        response    = self.client.post("/books", json=book)
        self.assertEqual(response.status_code, 201)

    # Create author when add a book
    def test_created_author(self):
        book = list_of_books(1)[0]
        self.client.post("/books", json=book)

        response = self.client.get("/authors")
        self.assertNotEqual(len(response.json), 0)

    # Create a book without optional parameter
    def test_post_book_without_optional(self):
        book        = list_of_books(1)[0]
        parameters  = ['premiere', 'price', 'authors']

        book.pop(parameters[random.randint(0, len(parameters) - 1)])
        response = self.client.post("/books", json=book)

        self.assertEqual(response.status_code, 201)

    # Create a book without requirement parameter
    def test_post_book_without_requirement(self):
        book = list_of_books(1)[0]
        book.pop('title')

        response = self.client.post("/books", json=book)
        self.assertEqual(response.status_code, 400)

    # Delete all books from database
    def test_delete_books(self):
        for book in list_of_books(30):
            self.client.post("/books", json=book)

        response = self.client.delete("/books")
        self.assertEqual(response.status_code, 200)

    # Get a book by id
    def test_get_book(self):
        book = list_of_books(1)[0]
        self.client.post("/books", json=book)

        response = self.client.get("/books/1")
        self.assertEqual(response.status_code, 200)

    # Get a book by id when database is empty
    def test_get_book_empty_database(self):
        response = self.client.get("/books/1")
        self.assertEqual(response.status_code, 404)

    # Modifide a book
    def test_put_book(self):
        book = list_of_books(1)[0]
        self.client.post("/books", json=book)

        book        = list_of_books(1)[0]
        response    = self.client.put("/books/1", json=book)

        self.assertEqual(response.status_code, 200)

    # Modifide a book without all parameters
    def test_put_book_without_parameters(self):
        book = list_of_books(1)[0]
        self.client.post("/books", json=book)

        book        = {}
        response    = self.client.put("/books/1", json=book)

        self.assertEqual(response.status_code, 200)

    # Modifide a book when database is empty
    def test_put_book_empty_database(self):
        book        = list_of_books(1)[0]
        response    = self.client.put("/books/1", json=book)

        self.assertEqual(response.status_code, 404)

    # Delete a book
    def test_delete_book(self):
        book = list_of_books(1)[0]
        self.client.post("/books", json=book)

        response = self.client.delete("/books/1")
        self.assertEqual(response.status_code, 200)

    # Delete a book when database is empty
    def test_delete_book_empty_database(self):
        response = self.client.delete("/books/1")
        self.assertEqual(response.status_code, 404)

#----------------------------------------------------------------

    # Get all authors from database
    def test_get_authors(self):
        for author in list_of_authors(30):
            self.client.post("/authors", json=author)

        response = self.client.get("/authors")
        self.assertEqual(response.status_code, 200)

    # Add new author to database
    def test_post_authors(self):
        author      = list_of_authors(1)[0]
        response    = self.client.post("/authors", json=author)

        self.assertEqual(response.status_code, 201)

    # Add new author to database without optional parameters
    def test_post_authors_without_optional(self):
        author      = list_of_authors(1)[0]
        parameters  = ['birth', 'death']

        author.pop(parameters[random.randint(0, len(parameters) - 1)])
        response    = self.client.post("/authors", json=author)

        self.assertEqual(response.status_code, 201)

    # Add new author to database without requirement parameters
    def test_post_authors_without_requirement(self):
        author      = list_of_authors(1)[0]
        parameters  = ['first_name', 'last_name']

        author.pop(parameters[random.randint(0, len(parameters) - 1)])
        response    = self.client.post("/authors", json=author)

        self.assertEqual(response.status_code, 400)

    # Delete all authors
    def test_delete_authors(self):
        for author in list_of_authors(30):
            self.client.post("/authors", json=author)

        response = self.client.delete("/authors")
        self.assertEqual(response.status_code, 200)

    # Get author by id
    def test_get_author(self):
        author = list_of_authors(1)[0]
        self.client.post("/authors", json=author)

        response = self.client.get("/authors/1")
        self.assertEqual(response.status_code, 200)

    # Get author by id when database is empty
    def test_get_author_empty_database(self):
        response = self.client.get("/authors/1")
        self.assertEqual(response.status_code, 404)

    # Modifide author
    def test_put_author(self):
        author = list_of_authors(1)[0]
        self.client.post("/authors", json=author)

        author      = list_of_authors(1)[0]
        response    = self.client.put("/authors/1", json=author)

        self.assertEqual(response.status_code, 200)

    # Modifide author without all parameters
    def test_put_author_without_parameters(self):
        author = list_of_authors(1)[0]
        self.client.post("/authors", json=author)

        author      = {}
        response    = self.client.put("/authors/1", json=author)

        self.assertEqual(response.status_code, 200)

    # Modifide author when database is empty
    def test_put_author_empty_database(self):
        author      = list_of_authors(1)[0]
        response    = self.client.put("/authors/1", json=author)

        self.assertEqual(response.status_code, 404)

    # Delete author
    def test_delete_author(self):
        author = list_of_authors(1)[0]
        self.client.post("/authors", json=author)

        response = self.client.delete("/authors/1")
        self.assertEqual(response.status_code, 200)

    # Delete author when database is empty
    def test_delete_author_empty_database(self):
        response = self.client.delete("/authors/1")
        self.assertEqual(response.status_code, 404)

#================================================================
if __name__ == '__main__':
    unittest.main()