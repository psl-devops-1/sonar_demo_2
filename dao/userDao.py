from config.database import db
from models.role import Role
from models.user import User


class UserDao:

    def getUserById(self, userId):
        return db.session.get(User, userId)


    def getUserByEmail(self, email):
        return User.query.filter_by(
            email=email
        ).first()

    def getAllUsers(self):
        return User.query.order_by(
            User.id).all()

    def saveUser(self, user):
        db.session.add(user)
        db.session.commit()
        return user


    def deleteUser(self, user):
        db.session.delete(user)
        db.session.commit()

    def userExistsByEmail(self, email):
        return User.query.filter_by(
            email=email
        ).first() is not None

    def getUsersByRole(self, roleName):
        return (
            User.query.join(User.role)
            .filter(Role.role_name == roleName)
            .order_by(User.id)
            .all()
        )
    