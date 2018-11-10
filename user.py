from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_name, password, is_active, is_admin, balance, user_id=None):
        self.user_name = user_name
        self.password = password
        self.id = user_id
        self.internal_is_active = is_active
        self.internal_is_admin = is_admin
        self.balance = balance

    def get_pw(self):
        return self.password

    def get_user_name(self):
        return self.user_name

    @property
    def is_active(self):
        return self.internal_is_active

    @is_active.setter
    def is_active(self, value):
        self.internal_is_active = value

    @property
    def is_admin(self):
        return self.internal_is_admin

    @is_admin.setter
    def is_admin(self, value):
        self.internal_is_admin = value

