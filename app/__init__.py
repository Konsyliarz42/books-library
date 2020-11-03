from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api, Resource, fields

app = Flask(__name__)
app.config.from_object(Config)

api         = Api(app)
database    = SQLAlchemy(app)
migrate     = Migrate(app, database)

from app import models

#database.drop_all()
#database.create_all()

@app.shell_context_processor
def make_shell_context():
    return {
        "database": database,
        "Book": models.Book,
        "Author": models.Author,
        "Client": models.Client
    }