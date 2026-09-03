from flask import session

from services.userService import UserService
userService = UserService()

def getCurrentUser():
    userId = session.get("user_id")
    if not userId:
        return None

    return userService.getUserById(userId)
