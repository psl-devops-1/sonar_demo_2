import os
from dotenv import load_dotenv
load_dotenv()
os.environ["FLASK_ENV"] = "testing"
import pytest
from app import app as flask_app
from config.database import db
from models import(
    Role, User, Course, CourseInstructor, Enrollment,
    Module, Lesson, Material, LessonProgress, Quiz, Question, QuizRecord
)



TEST_DATABASE_URI = os.environ.get("TEST_DATABASE_URI")


@pytest.fixture(scope="session")
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URI,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
        "JWT_SECRET_KEY": "test-jwt-secret-key",
        "JWT_TOKEN_LOCATION": ["headers", "cookies"]
    })

    with flask_app.app_context():
        assert "lms_test" in str(db.engine.url), f"CRITCAL SAFETY STOP: db is not connected to test db"
        db.create_all()
        yield flask_app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    connection = db.engine.connect()
    transaction = connection.begin()
    session = db.scoped_session(lambda: db.create_session(bind=connection))

    db.session = session

    yield session
    session.close()
    transaction.rollback()
    connection.close()