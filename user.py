from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_name, password, user_id=None):
        self.user_name = user_name
        self.password = password
        self.id = user_id
    def get_pw(self):
        return self.password
    def get_user_name(self):
        return self.user_name