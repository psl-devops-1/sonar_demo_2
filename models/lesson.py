from datetime import datetime, timezone
from config.database import db


class Lesson(db.Model):

    __tablename__ = "lessons"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    module_id = db.Column(
        db.Integer,
        db.ForeignKey("modules.id"),
        nullable=False,
        index=True
    )

    lesson_name = db.Column(
        db.String(150),
        nullable=False
    )

    content = db.Column(
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


    module = db.relationship(
        "Module",
        back_populates="lessons"
    )

    materials = db.relationship(
        "Material",
        back_populates="lesson",
        cascade="all, delete-orphan"
    )

    progress_records = db.relationship(
        "LessonProgress",
        back_populates="lesson",
        cascade="all, delete-orphan"
    )

    def toDict(self):
        return {
            "id": self.id,
            "module_id": self.module_id,
            "lesson_name": self.lesson_name,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }