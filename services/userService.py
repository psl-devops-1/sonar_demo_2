from models.user import User
from dao.userDao import UserDao
from dao.roleDao import RoleDao
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:
    def __init__(self):
        self.userDao = UserDao()
        self.roleDao = RoleDao()


    def register(self, name, email, password, roleName="student"):
        name = name.strip()
        email = email.strip()
        roleName = roleName.strip().lower()
        password = password.strip()


        if not name:
            raise ValueError("name is required")

        if not email:
            raise ValueError("email is required")
        if not password:
            raise ValueError("Password is required")
        if self.userDao.userExistsByEmail(email):
            raise ValueError("Email already registered")

        role = self.roleDao.getRoleByName(roleName)
        print(role)

        if not role:
            raise ValueError("Invalid Role")

   
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role_id=role.id
        )

        return self.userDao.saveUser(user)


    def authenticate(self, email, password):
        email = email.strip().lower()
        user = self.userDao.getUserByEmail(email)

        if not user:
            return None

        if not check_password_hash(
            user.password,
            password
        ):
            return None

        return user


    def getUserById(self, userId):
        return self.userDao.getById(userId)

    def getAllUsers(self):
        return self,self.userDao.getAll()

    
