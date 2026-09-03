from datetime import datetime, timezone
from config.database import db

class Material(db.Model):
    __tablename__ = "materials"

 

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    lesson_id = db.Column(
        db.Integer,
        db.ForeignKey("lessons.id"),
        nullable=False,
        index=True
    )

    course_instructor_id = db.Column(
        db.Integer,
        db.ForeignKey("course_instructors.id"),
        nullable=False
    )


    file_name = db.Column(
        db.String(150),
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=False
    )

    file_type = db.Column(
        db.String(50),
        nullable=False
    )



    access = db.Column(
        db.String(50),
        default="public",
        nullable=False
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
            "lesson_id",
            "file_name",
            name="uq_material_lesson_file_name"
        ),
    )
    lesson = db.relationship(
        "Lesson",
        back_populates="materials"
    )

    course_instructor = db.relationship(
        "CourseInstructor",
        back_populates="materials"
    )


    def toDict(self):
        return {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "course_instructor_id": self.course_instructor_id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "access": self.access,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }