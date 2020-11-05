from flask_restx import Api, Resource
from flask import jsonify, request
from datetime import datetime

from .models import Book, Author, Client
from .models import database

api = Api()


def add_value_from_form(form, name, last_value=None):
    if type(last_value) == datetime:
        last_value = last_value.strftime('%Y-%m-%d')

    try:
        value = last_value
        value = form[name]

        if name in ['birth', 'death', 'premiere']:
            value = datetime.strptime(value, '%Y-%m-%d')
            
    except KeyError:
        pass

    return value


def check_author(name, create=False):
    name = name.strip().split(' ')

    if len(name) > 1:
        author = Author.query.filter_by(first_name=name[0], last_name=name[1]).first()

        # Create book's author if not exist in database   
        if not author and create:
            author = Author(first_name=name[0], last_name=name[1])
            database.session.add(author)
            database.session.commit()
        elif not author:
            author = False

        return author
    else:
        return False


def check_book(title, create=False):
    if len(title) > 1:
        book = Book.query.filter_by(title=title).first()

        # Create a book if not exist in database   
        if not book and create:
            book = Book(title=title)
            database.session.add(book)
            database.session.commit()
        elif not book:
            book = False

        return book
    else:
        return False


def check_client(name, create=False):
    name = name.strip().split(' ')

    if len(name) > 1:
        client = Client.query.filter_by(first_name=name[0], last_name=name[1]).first()

        # Create book's client if not exist in database   
        if not client and create:
            client = Client(first_name=name[0], last_name=name[1])
            database.session.add(client)
            database.session.commit()
        elif not client:
            client = False

        return client
    else:
        return False


@api.route('/books')
class BooksAll(Resource):

    def get(self):
        books       = Book.query.all()
        books_list  = list()

        for book in books:
            authors = [{'name': f"{author.first_name} {author.last_name}", 'id': author.id} for author in book.authors]

            book = {
                'id': book.id, 'title': book.title, 'premiere': book.premiere,
                'price': book.price, 'authors': authors, 'client_id': book.client_id
            }

            books_list.append(book)
        
        return jsonify(books_list)

    @api.expect(api.model('Book', Book.FIELDS), validate=True)
    def post(self):
        form = request.get_json()

        # Create book
        book = Book(
            title       = add_value_from_form(form, 'title'),
            premiere    = add_value_from_form(form, 'premiere'),
            price       = add_value_from_form(form, 'price')
        )

        # Check the book in database
        if Book.query.filter(Book.title == book.title).all():
            return {'Error 409': "The book is already in database"}, 409

        # Add authors to the book from database
        authors_book = add_value_from_form(form, 'authors')

        if authors_book:
            for name in authors_book:
                author = check_author(name, True)
                book.authors.append(author)

        # Add client
        name = add_value_from_form(form, 'client')
        
        if name:
            client = check_client(name, True)

            if client:
                client.books.append(book)

        # Add the book to database
        database.session.add(book)
        database.session.commit()

        return {'added': book.title}, 201

    def delete(self):
        books = Book.query.all()

        for book in books:
            book.authors = []
            database.session.commit()
            database.session.delete(book)

        database.session.commit()

        return {'deleted': 'all books'}, 200


@api.route('/books/<int:id>')
class BooksById(Resource):

    def get(self, id):
        book = Book.query.get(id)

        if book:
            authors = [{'name': f"{author.first_name} {author.last_name}", 'id': author.id} for author in book.authors]

            return jsonify({
                'id': book.id, 'title': book.title, 'premiere': book.premiere,
                'price': book.price, 'authors': authors, 'client_id': book.client_id
            })
        
        return {'Error': 'Book is not find'}, 404

    def put(self, id):
        book = Book.query.get(id)
        before_change = book
        form = request.get_json()

        if book:
            book.title = add_value_from_form(form, 'title', book.title)
            book.premiere = add_value_from_form(form, 'premiere', book.premiere)
            book.price = add_value_from_form(form, 'price', book.price)
            authors = add_value_from_form(form, 'authors')
            client = add_value_from_form(form, 'client')

            # Check authors
            if authors:
                aut = list()

                for name in authors:
                    author = check_author(name, True)
                    aut.append(author)

                if aut:
                    book.authors = aut

            # Check client
            if client:
                client = check_client(client, True)                
                book.client_id = client.id

            # Update the book in database
            database.session.add(book)
            database.session.commit()

            return {'modified': f"{before_change.title}"}, 200

        return {'Error': 'Book is not find'}, 404

    def delete(self, id):
        book = Book.query.get(id)

        if book:
            book.authors= []
            database.session.commit()
            database.session.delete(book)
            database.session.commit()

            return {'deleted': f"{book.title}"}, 200

        return {'Error': 'Book is not find'}, 404
        

@api.route('/authors')
class AuthorsAll(Resource):

    def get(self):
        authors = Author.query.all()
        authors_in_dict = list()

        for author in authors:
            books = [{'title': book.title, 'id': book.id} for book in author.books]

            authors_in_dict.append({
                'id': author.id, 'first_name': author.first_name, 'last_name': author.last_name,
                'birth': author.birth, 'death': author.death, 'books': books
            })

        return jsonify(authors_in_dict)

    @api.expect(api.model('Author', Author.FIELDS), validate=True)
    def post(self):
        form = request.get_json()

        author = Author(
            first_name  = add_value_from_form(form, 'first_name'),
            last_name   = add_value_from_form(form, 'last_name'),
            birth       = add_value_from_form(form, 'birth'),
            death       = add_value_from_form(form, 'death')
        )

        # Check the author in database
        if Author.query.filter_by(first_name=author.first_name, last_name=author.last_name).all():
            return {'Error 409': "The author is already in database"}, 409

        # Add authors to the book from database
        authors_books = add_value_from_form(form, 'books')

        if authors_books:
            for title in authors_books:
                book = check_book(title, True)
                author.books.append(book)

        database.session.add(author)
        database.session.commit()

        return {'added': str(author)}, 201

    def delete(self):
        authors = Author.query.all()

        for author in authors:
            author.books = []
            database.session.commit()
            database.session.delete(author)

        database.session.commit()

        return {'deleted': 'all authors'}, 200


@api.route('/authors/<int:id>')
class AuthorsById(Resource):

    def get(self, id):
        author = Author.query.get(id)

        if author:
            books = [{'title': book.title, 'id': book.id} for book in author.books]

            return jsonify({
                    'id': author.id, 'first_name': author.first_name, 'last_name': author.last_name,
                    'birth': author.birth, 'death': author.death, 'books': books
                })

        return {'Error': 'Author is not find'}, 404

    def put(self, id):
        author = Author.query.get(id)
        before_change = author
        form = request.get_json()

        if author:
            author.birth = add_value_from_form(form, 'birth', author.birth)
            author.death = add_value_from_form(form, 'death', author.death)
            author.first_name = add_value_from_form(form, 'first_name', author.first_name)
            author.last_name = add_value_from_form(form, 'last_name', author.last_name)
            books = add_value_from_form(form, 'books')
            boo = list()

            if books:
                for title in books:
                    book = check_book(title, True)
                    boo.append(book)

                if boo:
                    author.books = boo

            database.session.add(author)
            database.session.commit()

            return {'modified': f"{before_change.first_name} {before_change.last_name}"}, 200

        return {'Error': 'Author is not find'}, 404

    def delete(self, id):
        author = Author.query.get(id)

        if author:
            author.books = []
            database.session.commit()
            database.session.delete(author)
            database.session.commit()

            return {'deleted': f"{author.first_name} {author.last_name}"}, 200

        return {'Error': 'Author is not find'}, 404


@api.route('/clients')
class ClientsAll(Resource):

    def get(self):
        clients = Client.query.all()
        clients_list = list()

        for client in clients:
            books = [{'title': book.title, 'id': book.id} for book in client.books]

            client = {
                'id': client.id, 'first_name': client.first_name, 'last_name': client.last_name,
                'books': books
            }

            clients_list.append(client)

        return jsonify(clients_list)

    @api.expect(api.model('Client', Client.FIELDS), validate=True)
    def post(self):
        form = request.get_json()

        client = Client(
            first_name = add_value_from_form(form, 'first_name'),
            last_name = add_value_from_form(form, 'last_name'),
        )

        # Check the client in database
        if Client.query.filter_by(first_name=client.first_name, last_name=client.last_name).all():
            return {'Error 409': "The client is already in database"}, 409

        # Add books to the client
        books = add_value_from_form(form, 'books')

        if books:
            for title in books:
                book = check_book(title, True)
                client.books.append(book)

        # Add the client to database
        database.session.add(client)
        database.session.commit()

        return {'added': str(client)}, 201

    def delete(self):
        clients = Client.query.all()

        for client in clients:
            client.books = []
            database.session.commit()
            database.session.delete(client)

        database.session.commit()

        return {'deleted': 'all clients'}, 200


@api.route('/clients/<int:id>')
class ClientsById(Resource):

    def get(self, id):
        client  = Client.query.get(id)

        if client:
            books   = [{'title': book.title, 'id': book.id} for book in client.books]

            return jsonify({
                    'id': client.id, 'first_name': client.first_name, 'last_name': client.last_name,
                    'books': books
            })

        return {'Error': 'Client is not find'}, 404

    def put(self, id):
        client = Client.query.get(id)
        before_change = client
        form = request.get_json()

        if client:
            client.first_name = add_value_from_form(form, 'first_name', client.first_name)
            client.last_name = add_value_from_form(form, 'last_name', client.last_name)
            books = add_value_from_form(form, 'books')
            boo = list()

            if books:
                for title in books:
                    book = check_book(title, True)
                    boo.append(book)

                if boo:
                    client.books = boo

            database.session.add(client)
            database.session.commit()

            return {'modified': f"{before_change.first_name} {before_change.last_name}"}, 200

        return {'Error': 'Client is not find'}, 404

    def delete(self, id):
        client = Client.query.get(id)

        if client:
            client.books = []
            database.session.commit()
            database.session.delete(client)
            database.session.commit()

            return {'deleted': f"{client.first_name} {client.last_name}"}, 200

        return {'Error': 'Client is not find'}, 404
