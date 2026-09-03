from datetime import datetime, timezone

from config.database import db

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True
    )

    role_name = db.Column(db.String(50), nullable=False, unique=True)
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


    users = db.relationship("User", back_populates="role")

    def toDict(self, includeDates=False):
        return {
            "id": self.id,
            "role_name": self.role_name,
            "created_at" : self.created_at.isoformat() if self.created_at else None,
            "updated_at" : self.updated_at.isoformat() if self.updated_at else None
    

        }

  