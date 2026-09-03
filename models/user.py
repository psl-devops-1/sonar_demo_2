from datetime import datetime, timezone
from config.database import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.String(100),
        nullable=False

    )

    email = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
        index=True
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id"),
        nullable=False,
        index=True
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

    role = db.relationship(
        "Role",
        back_populates="users"
    )

    course_instructors =  db.relationship(
        "CourseInstructor",
        back_populates="instructor"
    )

    enrollments = db.relationship(
        "Enrollment",
        back_populates="student"
    )

    quizzes = db.relationship(
        "Quiz",
        back_populates="instructor"
    )

    quiz_records = db.relationship(
        "QuizRecord",
        back_populates="student"
    )


    def toDict(self):
        return {
            "id":  self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.role_name if self.role else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

