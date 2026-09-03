from datetime import datetime, timezone
from config.database import db

class Module(db.Model):
    __tablename__ = "modules"

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

    module_name = db.Column(
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
    course = db.relationship(
        "Course",
        back_populates="modules"
    )


    lessons = db.relationship(
        "Lesson",
        back_populates="module",
        cascade="all, delete-orphan"
    )


    def toDict(self):
        return {
            "id": self.id,
            "course": self.course_id,
            "module_name": self.module_name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }