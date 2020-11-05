from flask import Flask
from config import Config
from flask_migrate import Migrate

from . import models
from . import routes

from .models import database

app = Flask(__name__)
app.config.from_object(Config)

routes.api.init_app(app)
models.database.init_app(app)
migrate = Migrate(app, models.database)


@app.shell_context_processor
def make_shell_context():
    return {
        "database": models.database,
        "Book": models.Book,
        "Author": models.Author,
        "Client": models.Client
    }