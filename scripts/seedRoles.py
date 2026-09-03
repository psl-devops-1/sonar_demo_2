import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))


from app import app
from config.database import db
from models.role import Role


with app.app_context():
    roles = [
        "student",
        "instructor",
        "admin"
    ]

    for roleName in roles:
        exisitng = Role.query.filter_by(
            role_name=roleName
        ).first()

        if not exisitng:
            db.session.add(
                Role(role_name=roleName)
            )

    db.session.commit()
    print("Roles seeded")