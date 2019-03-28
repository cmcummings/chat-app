# exceptions.py

class UserError(Exception):
    pass

class UsernameTakenError(UserError):
    pass

class InvalidLoginError(UserError):
    pass