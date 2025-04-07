import hashlib
from database import create_new_user, fetch_user

def md5_hash(key):
    return hashlib.md5(key.encode()).hexdigest()

def validate_login_credentials(username, password):
    user = fetch_user(username.lower())
    if(user is None):
        return (False, "Username doesn't exist !")
    if(user.password_hash == md5_hash(password)):
        return (True, "Validated")
    return (False, "Wrong password used !")

def validate_register_credentials(username, password):

    for char in username:
        if(char in " /\\:;~&.,*(){}[]'\""):
            return (False, "Username contains spaces or special characters from  /\\:;~&.,*(){}[]'\"")
    for char in password:
        if(char in " /\\:;~&.,*(){}[]'\""):
            return (False, "Password contains spaces or special characters from  /\\:;~&.,*(){}[]'\"")

    user = fetch_user(username.lower())
    if(user is None):
        password_hash = md5_hash(password)
        create_new_user(username.lower(), password_hash)
        return (True, "Validated")
    else:
        return (False, "Username already exists !")