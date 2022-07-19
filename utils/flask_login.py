import os
from flask_login import UserMixin
from app import login
from utils import common2 as cm2


class User(UserMixin):
    def __init__(self):
        # self.is_active (False)
        self.user_id = None
        # self.common_user_name = os.environ.get('ST_COMMON_USER_NAME') or 'common_user'
        # self.common_pwd = os.environ.get('ST_COMMON_GROUP_PWD')

    def get_id(self):
        return self.user_id

    def check_password(self, pwd):
        # if self.user_id and str(self.common_pwd).upper() == str(pwd).upper():
        if self.user_id:
            # self.is_active = True
            return True
        else:
            return False

    def get_user(self, user_id):
        # if user_id and self.check_user_name(user_id):
        if user_id and cm2.validate_user_existence(user_id):
            self.user_id = user_id
            return self
        else:
            return None

    def validate_user(self, user_id, pwd):
        status, error_str = cm2.validate_user_login(user_id, pwd)
        if user_id and status:
            self.user_id = user_id
            return self, None
        else:
            return None, error_str

    # def check_user_name(self, user_id):
    #     default_user = cm2.get_client_ip() + os.environ.get('ST_USER_NAME_POSTFIX')
    #     if user_id == default_user:
    #         return True
    #     else:
    #         return False

    @login.user_loader
    def load_user(id):
        user = User()
        return user.get_user(id)