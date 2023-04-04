from typing import Tuple

from bson.objectid import ObjectId
from passlib.context import CryptContext
import jdatetime
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def to_gorgian(value:str) -> str:
    value = value.split(' ')
    value_date = value[0].split('/')
    value_hours = value[1].split(':')
    value = str(jdatetime.date(day=int(value_date[2]), month=int(value_date[1]),
                               year=int(value_date[0])).togregorian()) + f' {value_hours[0]}:{value_hours[1]}'

    return value


def from_gorgian(value):
    time_p1 = str(value).split(' ')
    time_p2 = str(time_p1[0]).split('-')
    final_time = str(jdatetime.date.fromgregorian(day=int(time_p2[2]), month=int(time_p2[1]),
                                                  year=int(time_p2[0]))) + " " + time_p1[1]

    return final_time

