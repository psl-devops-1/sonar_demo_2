from datetime import datetime, timezone
from config.database import db

class Quiz(db.Model):

    __tablename__ = "quizzes"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    course_instructor_id = db.Column(
        db.Integer,
        db.ForeignKey("course_instructors.id"),
        nullable=False,
        index=True
    )

    instructor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    quiz_name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text
    )


    created_at = db.Column(
            db.DateTime,
            default=lambda: datetime.now(timezone.utc),
            nullable=False
        )
        
    updated_at = db.Column(
        db.DateTime,        
        default=lambda: datetime.now(timezone.utc),
        onupdate= lambda: datetime.now(timezone.utc),
        nullable=False
    )

    

    course_instructor = db.relationship(
        "CourseInstructor",
        back_populates="quizzes"
    )

    questions = db.relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )

    quiz_records = db.relationship(
        "QuizRecord",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )
    instructor = db.relationship(
        "User",
        back_populates="quizzes"

    )

    