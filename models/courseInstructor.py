from datetime import datetime, timezone

from config.database import db

class CourseInstructor(db.Model):
    __tablename__ = "course_instructors"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False,
        index=True
    )

    instructor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
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
    
    __table_args__ = (
        db.UniqueConstraint(
            "course_id",
            "instructor_id",
            name="uq_course_instructor"
        ),
    )

    course  = db.relationship(
        "Course",
        back_populates="instructors"
    )

    instructor = db.relationship(
        "User",
        back_populates="course_instructors"
    )

    enrollments = db.relationship(
        "Enrollment",
        back_populates="course_instructor",
        cascade="all, delete-orphan"
    )

    materials = db.relationship(
        "Material",
        back_populates="course_instructor"
    )
    quizzes = db.relationship("Quiz", back_populates="course_instructor")


    def toDict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "instructor_id": self.instructor_id,
            "course_name": self.course.course_name if self.course else None,
            "instructor_name": self.instructor.name if self.instructor else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None

            }