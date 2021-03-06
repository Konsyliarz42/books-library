from flask_sqlalchemy import SQLAlchemy
from flask_restx import fields

database = SQLAlchemy()

books_authors = database.Table(
    'books_authors',
    database.Column('book_id', database.Integer, database.ForeignKey('book.id')),
    database.Column('author_id', database.Integer, database.ForeignKey('author.id'))
)


class Book(database.Model):

    FIELDS = {
        'title': fields.String(required=True),
        'premiere': fields.String(),
        'price': fields.Float(),
        'authors': fields.List(fields.String()),
        'client_id': fields.Integer()
    }

    id = database.Column(database.Integer, primary_key=True)
    title = database.Column(database.String(256), nullable=False)
    premiere = database.Column(database.Date())
    price = database.Column(database.Float)
    client_id = database.Column(database.Integer, database.ForeignKey('client.id'))

    authors = database.relationship(
        "Author",
        secondary=books_authors,
        backref=database.backref('authors', lazy=True),
        lazy="dynamic"
    )

    def __str__(self):
        return f"Book: {self.title} by {self.authors}"


class Author(database.Model):

    FIELDS = {
        'first_name': fields.String(required=True),
        'last_name': fields.String(required=True),
        'birth': fields.String(),
        'death': fields.String(),
        'books': fields.List(fields.String())
    }

    id = database.Column(database.Integer, primary_key=True)
    first_name = database.Column(database.String(256), nullable=False)
    last_name = database.Column(database.String(256), nullable=False)
    birth = database.Column(database.Date())
    death = database.Column(database.Date())

    books = database.relationship(
        "Book",
        secondary=books_authors,
        backref=database.backref('books', lazy=True),
        lazy="dynamic"
    )

    def __str__(self):
        return f"Author: {self.first_name} {self.last_name} ({self.birth} - {self.death})"


class Client(database.Model):

    FIELDS = {
        'first_name': fields.String(required=True),
        'last_name': fields.String(required=True),
        'books': fields.List(fields.String())
    }

    id = database.Column(database.Integer, primary_key=True)
    first_name = database.Column(database.String(256), nullable=False)
    last_name = database.Column(database.String(256), nullable=False)
    books = database.relationship("Book", backref='book')

    def __str__(self):
        return f"Client: {self.first_name} {self.last_name}"
