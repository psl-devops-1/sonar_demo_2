from config.database import db
from models.role import Role


class RoleDao:

    def getRoleById(self, rol_id):
        return db.session.get(Role, id)


    def getRoleByName(self, roleName):
        return Role.query.filter_by(
            role_name=roleName
        ).first()

    def getAllRoles(self):
        return Role.query.order_by(
            Role.id
        ).all()


    def saveRole(self, role):
        db.session.add(role)
        db.session.commit()


        return role

    def deleteRole(self, role):
        db.session.delete(role)
        db.session.commit()