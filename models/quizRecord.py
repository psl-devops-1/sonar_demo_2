from datetime import datetime, timezone

from config.database import db

class QuizRecord(db.Model):

    __tablename__ = "quiz_records"

    id = db.Column(
        db.Integer,
        primary_key = True,
        autoincrement=True
    )

    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey("quizzes.id"),
        nullable=False,
        index=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    score = db.Column(
        db.Integer,
        nullable=False
    )

    quiz_answer = db.Column(
        db.JSON,
        nullable=False
    )
    """ 
    questionId: slectedOption,
    questionIdL selctedOption
    """


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
    quiz = db.relationship(
        "Quiz",
        back_populates="quiz_records"
    )

    student = db.relationship(
        "User",
        back_populates="quiz_records"
    )