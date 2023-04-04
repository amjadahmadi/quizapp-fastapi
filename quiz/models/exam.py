import re
from core.database import get_db
from core.utils import *
from uuid import uuid4
from bson.objectid import ObjectId


class Exam:
    db_collection = get_db()['exam']

    def __init__(self, name, start_time, end_time, uni_name, password, random_question, random_answer, one_page,
                 master_id) -> None:
        self.name = name
        self.start_date = start_time
        self.end_date = end_time
        self.password = password
        self.uni_name = uni_name
        self.random_question = random_question
        self.random_answer = random_answer
        self.one_page = one_page
        self.master_id = ObjectId(master_id)
        self.uid = str(uuid4()).split('-')[0]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):

        if type(val) == str and (0 < len(val) < 20):
            self._name = val
        else:
            raise ValueError("invalid name")

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, val):
        self._start_date = to_gorgian(val)

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, val):
        self._end_date = to_gorgian(val)

    @property
    def uni_name(self):
        return self._uni_name

    @uni_name.setter
    def uni_name(self, val):
        if type(val) == str and 0 < len(val):
            self._uni_name = val
        else:
            raise ValueError("invalid college name")

    @property
    def random_question(self):
        return self._random_question

    @random_question.setter
    def random_question(self, val):
        if not val in (True, False):
            return ValueError("invalid rando question")
        self._random_question = val

    @property
    def random_answer(self):
        return self._random_answer

    @random_answer.setter
    def random_answer(self, val):
        if not val in (True, False):
            return ValueError("invalid rando answer")
        self._random_answer = val

    @property
    def one_page(self):
        return self._one_page

    @one_page.setter
    def one_page(self, val):
        if not val in (True, False):
            return ValueError("invalid one page")
        self._one_page = val

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, val):
        if len(val) < 4:
            raise ValueError("password is short")
        self.__password = get_password_hash(val)

    @staticmethod
    def change_date_to_jalali(exam):
        exam['time_stamp_start'] = datetime.timestamp(datetime.strptime(exam["start_time"], '%Y-%m-%d %H:%M'))
        exam['time_stamp_end'] = datetime.timestamp(datetime.strptime(exam["end_time"], '%Y-%m-%d %H:%M'))
        exam["start_time"] = from_gorgian(exam["start_time"])
        exam["end_time"] = from_gorgian(exam["end_time"])
        return exam

    @staticmethod
    def validate_date(exam):
        if not (datetime.strptime(exam["start_time"], '%Y-%m-%d %H:%M') <= datetime.now() <= datetime.strptime(exam["end_time"], '%Y-%m-%d %H:%M')):
            raise ValueError('date of exam')

    def return_dict(self):
        return {
            'name': self.name,
            'uni_name': self.uni_name,
            'random_answer': self.random_answer,
            'random_question': self.random_question,
            'password': self.password,
            'one_page': self.one_page,
            'master_id': self.master_id,
            'start_time': self.start_date,
            'end_time': self.end_date,
            'uid': self.uid
        }
