import os

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    if os.environ.get("FLASK_ENV") == "testing" or app.config.get("TESTING"):
        dbURI = os.environ.get("TEST_DATABASE_URI")
    else:
        dbURI = os.environ.get("DATABASE_URI")

   
    app.config["SQLALCHEMY_DATABASE_URI"] = dbURI

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)