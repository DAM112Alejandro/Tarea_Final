def userSchema(user) -> dict:
    return {
        "username": user["username"],
        "email": user["email"],
        "password": user["password"]
    }
    
def userListSchema(users) -> list:
    return [userSchema(user) for user in users]