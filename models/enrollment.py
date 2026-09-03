from datetime import datetime, timezone
from config.database import db

class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    student_id = db.Column(
        db.Integer,
       db.ForeignKey("users.id"),
       nullable=False,
       index=True
    )

  
    course_instructor_id = db.Column(
        db.Integer,
        db.ForeignKey("course_instructors.id"),
        nullable=False,
        index=True
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="not_started",  #not started, ongoing, completed?
       
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
            "student_id",
            "course_instructor_id"            ,
            name="uq_student_course_instructor"
        ),
    )

    student = db.relationship(
        "User",
        back_populates="enrollments"
    )

    course_instructor = db.relationship(
        "CourseInstructor",
        back_populates="enrollments"
    )

    lesson_progress_records = db.relationship(
        "LessonProgress",
        back_populates="enrollment",
        cascade="all, delete-orphan"
    )

    def toDict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_instructor_id": self.course_instructor_id,
            "student_name": self.student.name if self.student else None,
            "course_name": self.course_instructor.course.course_name if self.course_instructor else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }