from models.role import Role
from dao.roleDao import RoleDao


class RoleService:
    def __init__(self):
        self.roleDao = RoleDao()

    def createRole(self, roleName):
        roleName = roleName.strip().lower()

        if not roleName:
            raise ValueError("Role name is required")

        existingRole = self.roleDao.getByName(roleName)

        if existingRole:
            raise ValueError("Role already exists")

        role = Role(
            roleName = roleName
        )

        return self.roleDao.saveRole(role)


    def getRoleByName(self, roleName):
        return self.roleDao.getRoleByName(
            roleName.strip().lower()
        )

    def getRoleById(self, roleId):
        return self.roleDao.getById(roleId)

    def getAllRoles(self):
        return self.roleDao.getAll()

    