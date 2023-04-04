import re
from core.database import get_db
from core.utils import get_password_hash


class User:
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    db_collection = get_db()['users']

    def __init__(self, name, family, email, password, type) -> None:
        self.name = name
        self.family = family
        self.email = email
        self.password = password
        self.type = type

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):

        if type(val) == str and len(val) < 20:
            self._name = val
        else:
            raise ValueError("invalid name")

    @property
    def family(self):
        return self._name

    @family.setter
    def family(self, val):
        if type(val) == str and len(val) < 20:
            self._family = val
        else:
            raise ValueError("invalid family")

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, val):
        if not re.fullmatch(self.regex, val):
            raise ValueError("invalid email")
        if self.db_collection.find_one({'email': val}):
            raise ValueError("email already exist")
        self._email = val

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        if val not in ['master', 'student']:
            raise ValueError("invalid type")
        self._type = val

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, val):
        if len(val) < 4:
            raise ValueError("password is short")
        self.__password = get_password_hash(val)

    def return_dict(self):
        return {
            'name': self.name,
            'family': self.family,
            'email': self.email,
            'type': self.type,
            'password': self.password
        }
