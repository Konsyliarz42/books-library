from app import app, api, database, Resource, request, fields
from app.models import Book, Author, book_model, author_model
from flask import jsonify

@app.shell_context_processor
def make_shell_context():
    return {
        "database": database,
        "Book": Book,
        "Author": Author
    }

#================================================================
def add_value_from_form(form, name, last_value=None):
    try:
        value = last_value
        value = form[name]
    except:
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
        elif not author:
            author = False

        return author
    else:
        return False

#================================================================
@api.route('/books')
class BooksAll(Resource):
    def get(self):
        books = Book.query.all()
        books_in_dict = list()

        for book in books:
            authors = [{'name': f"{author.first_name} {author.last_name}", 'id': author.id} for author in book.authors]

            books_in_dict.append({
                'id': book.id, 'title': book.title, 'premiere': book.premiere,
                'price': book.price, 'authors': authors
            })
            
        return jsonify(books_in_dict)

    #--------------------------------
    @api.expect(book_model, validate=True)
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

                if author:
                    book.authors.append(author)
                else:
                    return {'Error 400': "Author's name of the book is incorrect"}, 400

        # Add the book to database
        database.session.add(book)
        database.session.commit()

        return {'added': book.title}, 201

    #--------------------------------
    def delete(self):
        books = Book.query.all()

        for book in books:
            database.session.delete(book)

        database.session.commit()

        return {'deleted': 'all books'}, 200


@api.route('/books/<int:id>')
class BooksById(Resource):
    def get(self, id):
        book    = Book.query.get(id)

        if book:
            authors = [{'name': f"{author.first_name} {author.last_name}", 'id': author.id} for author in book.authors]

            return jsonify({
                'id': book.id, 'title': book.title, 'premiere': book.premiere,
                'price': book.price, 'authors': authors
            })
        
        return {'Error': 'Book is not find'}, 404

    #--------------------------------
    def put(self, id):
        book    = Book.query.get(id)
        form    = request.get_json()

        if book:
            book.title      = add_value_from_form(form, 'title', book.title)
            book.premiere   = add_value_from_form(form, 'premiere', book.premiere)
            book.price      = add_value_from_form(form, 'price', book.price)
            authors         = add_value_from_form(form, 'authors')
            aut             = list()

            if authors:
                for name in authors:
                    author = check_author(name)

                    if author:
                        aut.append(author)

                if aut:
                    book.authors = aut

            database.session.add(book)
            database.session.commit()

            return {'modified': f"{book.title}"}, 200

        return {'Error': 'Book is not find'}, 404

    #--------------------------------
    def delete(self, id):
        book = Book.query.get(id)

        if book:
            database.session.delete(book)
            database.session.commit()

            return {'deleted': f"{book.title}"}, 200

        return {'Error': 'Book is not find'}, 404
        

#================================================================
@api.route('/authors')
class AuthorsAll(Resource):
    def get(self):
        authors = Author.query.all()
        authors_in_dict = list()

        for author in authors:
            authors_in_dict.append({
                'id': author.id, 'first_name': author.first_name, 'last_name': author.last_name,
                'birth': author.birth, 'death': author.death
            })

        return jsonify(authors_in_dict)

    #--------------------------------
    @api.expect(author_model, validate=True)
    def post(self):
        form = request.get_json()

        author = Author(
            first_name  = add_value_from_form(form, 'first_name'),
            last_name   = add_value_from_form(form, 'last_name'),
            birth       = add_value_from_form(form, 'birth'),
            death       = add_value_from_form(form, 'death')
        )

        if Author.query.filter_by(first_name=author.first_name, last_name=author.last_name).all():
            return {'Error 409': "The author is already in database"}, 409

        database.session.add(author)
        database.session.commit()

        return {'added': str(author)}, 201

    #--------------------------------
    def delete(self):
        authors = Author.query.all()

        for author in authors:
            database.session.delete(author)

        database.session.commit()

        return {'deleted': 'all authors'}, 200

@api.route('/authors/<int:id>')
class AuthorsById(Resource):
    def get(self, id):
        author = Author.query.get(id)

        if author:
            return jsonify({
                    'id': author.id, 'first_name': author.first_name, 'last_name': author.last_name,
                    'birth': author.birth, 'death': author.death
                })

        return {'Error': 'Author is not find'}, 404

    #--------------------------------
    def put(self, id):
        author          = Author.query.get(id)
        before_change   = author
        form            = request.get_json()

        if author:
            author.birth        = add_value_from_form(form, 'birth', author.birth)
            author.death        = add_value_from_form(form, 'death', author.death)
            author.first_name   = add_value_from_form(form, 'first_name', author.first_name)
            author.last_name    = add_value_from_form(form, 'last_name', author.last_name)

            database.session.add(author)
            database.session.commit()

            return {'modified': f"{before_change.first_name} {before_change.last_name}"}, 200

        return {'Error': 'Author is not find'}, 404

    #--------------------------------
    def delete(self, id):
        author = Author.query.get(id)

        if author:
            database.session.delete(author)
            database.session.commit()

            return {'deleted': f"{author.first_name} {author.last_name}"}, 200

        return {'Error': 'Author is not find'}, 404

#================================================================
if __name__ == "__main__":
    app.run(debug=False)