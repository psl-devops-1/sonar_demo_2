from datetime import datetime, timezone

from config.database import db


class Question(db.Model):

    __tablename__ = "questions"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey("quizzes.id"),
        nullable=False,
        index=True
    )

    question_text = db.Column(
        db.Text,
        nullable=False
    )

    question_options = db.Column(
        db.JSON,
        nullable=False
    )  
    """ 
     Paris: false,
     Spain : True,
     Georgia : False,
     France: False
       """

    points = db.Column(
        db.Integer,
        nullable=False,
        default=1
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
  
    
    

    quiz = db.relationship(
        "Quiz",
        back_populates="questions"
    )