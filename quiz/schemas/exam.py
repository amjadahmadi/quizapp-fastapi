import datetime

from pydantic import BaseModel, Field
from core.utils import PyObjectId, ObjectId


class ExamResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    start_time: str
    end_time: str
    uni_name: str
    random_question: bool
    random_answer: bool
    one_page: bool
    master_id: PyObjectId = Field(default_factory=PyObjectId, alias="master_id")
    uid: str
    time_stamp_start: float = None
    time_stamp_end: float = None


    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Exam(BaseModel):
    name: str
    start_time: str
    end_time: str
    uni_name: str
    password: str
    random_question: bool = True
    random_answer: bool = True
    one_page: bool = True
    master_id: str = None
    users: list = None


class Questions(BaseModel):
    exam_id: str = None
    type: str = None
    question: str
    file_name: str = None
    file_address: str = None
    options: list[dict] = None


class LoadQuestions(BaseModel):
    exam_id: str


class QuestionsR(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    exam_id: PyObjectId = Field(default_factory=PyObjectId, alias="exam_id")
    type: str
    question: str = None
    file_name: str = None
    file_address: str = None
    options: list[dict] = None
    answer: dict = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class StuAnswers(BaseModel):
    a_list:list[QuestionsR]
    dont_ans:int
    true_ans:int
    wrong_ans:int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

