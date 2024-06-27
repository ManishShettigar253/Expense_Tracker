from flask_login import UserMixin
from bson import ObjectId

class User(UserMixin):
    def __init__(self, email, password, user_id=None):
        self.email = email
        self.password = password
        self.user_id = str(user_id) if user_id else None

    def get_id(self):
        return self.user_id

    @staticmethod
    def get(user_id):
        from app import users  # Import here to avoid circular import
        try:
            user_data = users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data['email'], user_data['password'], user_data['_id'])
        except (TypeError, ValueError):
            pass
        return None
