from app import database, api, fields

#================================================================
books_authors = database.Table(
    'books_authors',
    database.Column('book_id', database.Integer, database.ForeignKey('book.id')),
    database.Column('author_id', database.Integer, database.ForeignKey('author.id'))
)

#================================================================
class Book(database.Model):
    id          = database.Column(database.Integer,     primary_key=True)
    title       = database.Column(database.String(256), nullable=False)
    premiere    = database.Column(database.String(256))
    price       = database.Column(database.Float)

    authors = database.relationship(
        "Author",
        secondary=books_authors,
        backref=database.backref('authors', lazy=True),
        lazy="dynamic"
    )
    
    #--------------------------------
    def __str__(self):
        return f"{self.title} by {self.authors}"

#----------------------------------------------------------------
book_model  = api.model('Book',{
        'title':fields.String(required=True),
        'premiere':fields.String(),
        'price':fields.Float(),
        'authors':fields.List(fields.String())
})

#================================================================
class Author(database.Model):
    id          = database.Column(database.Integer,     primary_key=True)
    first_name  = database.Column(database.String(256), nullable=False)
    last_name   = database.Column(database.String(256), nullable=False)
    birth       = database.Column(database.String(256))
    death       = database.Column(database.String(256))

    #--------------------------------
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.birth} - {self.death})"

#----------------------------------------------------------------
author_model  = api.model('Author',{
        'first_name':fields.String(required=True),
        'last_name':fields.String(required=True),
        'birth':fields.String(),
        'death':fields.String()
})
