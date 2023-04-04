import random

from bson.objectid import ObjectId


class Question:
    def __init__(self, exam_id: ObjectId, type: str, question: str = None, file_name: str = None, file_address: str = None,
                 options: list[dict] = None) -> None:
        self.question = question
        self.file_name = file_name
        self.file_address = file_address
        self.options = options
        self.type = type
        self.exam_id = exam_id


    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        if val not in ['test', 'description', 'file']:
            raise ValueError("invalid type")
        self._type = val

    @property
    def exam_id(self):
        return self._exam_id

    @exam_id.setter
    def exam_id(self, val):
        self._exam_id = ObjectId(val)

    @staticmethod
    def random(list_question: list):
        new_list = []
        while len(list_question) != 0:
            choice = random.choice(list_question)
            list_question.remove(choice)
            new_list.append(choice)
        return new_list

    def return_dict(self):
        return {
            'question': self.question,
            'file_name': self.file_name,
            'file_address': self.file_address,
            'type': self.type,
            'exam_id': self.exam_id,
            'options': self.options
        }
