from datetime import datetime, timezone
from config.database import db

class LessonProgress(db.Model):

    __tablename__ = "lesson_progress"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    enrollment_id = db.Column(
        db.Integer,
        db.ForeignKey("enrollments.id",
                      ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    lesson_id = db.Column(
        db.Integer,
        db.ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    completed = db.Column(
        db.Boolean,
        nullable=False,
        default=False
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
            "enrollment_id",
            "lesson_id",
            name="uq_enrollment_lesson_progress"
        ),
    )

    enrollment = db.relationship(
        "Enrollment",
        back_populates="lesson_progress_records"
    )

    lesson = db.relationship(
        "Lesson",
        back_populates="progress_records"
    )

    def toDict(self):
        return {
            "id": self.id,
            "enrollment_id": self.enrollment_id,
            "lesson_id": self.lesson_id,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }