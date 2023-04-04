import os
import pathlib
from datetime import datetime

import redis
import starlette.datastructures
from fastapi import APIRouter, Depends, File, UploadFile, Request
from fastapi_jwt_auth import AuthJWT
from starlette.responses import JSONResponse
from bson.objectid import ObjectId
from core.database import get_db, get_db_cash
from pymongo import MongoClient
from schemas.exam import ExamResponse, Questions, QuestionsR, LoadQuestions,StuAnswers, Exam as Exam_schema
from models.exam import Exam
from models.question import Question
from core.utils import verify_password

router = APIRouter(
    tags=['exam'],
    prefix='/exam'
)


@router.post('/register')
def register_exam(request: Exam_schema, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    exam_collection = db['exam']
    try:
        exam = Exam(**request.__dict__)
        exam_collection.insert_one(exam.return_dict())
        return 'successes'
    except ValueError as e:
        return JSONResponse(status_code=406, content={"detail": str(e)})


@router.get('/my-exam/{master_id}', response_model=list[ExamResponse])
def my_exam(master_id, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends(),
            db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    if user_id != master_id:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})

    exam_collection = db['exam']
    try:
        exam = exam_collection.find({'master_id': ObjectId(master_id)})
        exam_list = []
        for i in exam:
            exam_list.append(Exam.change_date_to_jalali(i))

        return exam_list
    except ValueError as e:
        return JSONResponse(status_code=406, content={"detail": str(e)})


@router.post('/create_question')
def create_question(request: Questions, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends(),
                    db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    exam = db['exam']
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    if user_id != exam.find_one({'_id': ObjectId(request.exam_id)})['master_id']:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})

    questions_collection = db['questions']
    try:
        print(request.__dict__)
        question = Question(**request.__dict__)
        questions_collection.insert_one(question.return_dict())
        return 'successes'
    except ValueError as e:
        return JSONResponse(status_code=406, content={"detail": str(e)})


@router.post("/upload-file/{exam_id}")
def create_question_file(exam_id, uploaded_file: UploadFile = File(...), db: MongoClient = Depends(get_db),
                         Authorize: AuthJWT = Depends(), db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    exam = db['exam']
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    if user_id != exam.find_one({'_id': ObjectId(exam_id)})['master_id']:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})
    file_location = f"/files/questions/{exam_id}"
    path = os.getcwd()
    question_collection = db['questions']
    if not os.path.isdir(path + file_location):
        os.mkdir(path + file_location)

    with open(file_location + '/' + uploaded_file.filename, "wb") as file_object:
        file_object.write(uploaded_file.file.read())
    question = Question(type="file", exam_id=ObjectId(exam_id), file_name=uploaded_file.filename,
                        file_address=file_location)
    question_collection.insert_one(question.return_dict())
    return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}"}


@router.get('/get_question/{question_id}', response_model=QuestionsR)
def get_question(question_id, db: MongoClient = Depends(get_db),
                 Authorize: AuthJWT = Depends(), db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    questions = db['questions']
    question = questions.aggregate(
        [
            {'$match': {'_id': ObjectId(question_id)}},
            {"$lookup": {'from': "exam", 'localField': "exam_id", 'foreignField': "_id", 'as': "exam"}},
            {"$project": {'_id': 1, 'type': 1, 'question': 1, 'file_name': 1, 'file_address': 1, 'options': 1,
                          'exam.master_id': 1}}
        ]
    )

    result = list(question)[0]
    if user_id != result['exam'][0]['master_id']:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})
    return result


@router.get('/get_exam/{exam_id}', response_model=ExamResponse)
def get_exam(exam_id, db: MongoClient = Depends(get_db),
             Authorize: AuthJWT = Depends(), db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    exam_collection = db['exam']
    exam = exam_collection.find_one({'_id': ObjectId(exam_id)})
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    if user_id != exam['master_id']:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})

    exam = Exam.change_date_to_jalali(exam)
    return exam


@router.post('/edit_question/{question_id}')
def edit_question(question_id, request: Questions, db: MongoClient = Depends(get_db),
                  Authorize: AuthJWT = Depends(), db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    questions = db['questions']
    question = questions.aggregate(
        [
            {'$match': {'_id': ObjectId(question_id)}},
            {"$lookup": {'from': "exam", 'localField': "exam_id", 'foreignField': "_id", 'as': "exam"}},
            {"$project": {'_id': 1, 'type': 1, 'question': 1, 'file_name': 1, 'file_address': 1, 'options': 1,

                          'exam.master_id': 1}}
        ]
    )

    result = list(question)[0]
    print(result)
    if user_id != result['exam'][0]['master_id']:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})

    questions.update_one({'_id': ObjectId(question_id)}, {
        '$set': {'question': request.question, 'options': request.options if request.options else result['options']}})
    return 'ok'


@router.delete('/edit_question/{question_id}')
def delete_question(question_id, db: MongoClient = Depends(get_db),
                    Authorize: AuthJWT = Depends(), db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    questions = db['questions']
    question = questions.aggregate(
        [
            {'$match': {'_id': ObjectId(question_id)}},
            {"$lookup": {'from': "exam", 'localField': "exam_id", 'foreignField': "_id", 'as': "exam"}},
            {"$project": {'_id': 1, 'type': 1, 'question': 1, 'file_name': 1, 'file_address': 1, 'options': 1,
                          'exam.master_id': 1}}
        ]
    )

    result = list(question)[0]
    print(result)
    if user_id != result['exam'][0]['master_id']:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})

    questions.delete_one({'_id': ObjectId(question_id)})
    return 'ok'


@router.post('/edit_exam/{exam_id}')
def edit_exam(exam_id, request: Exam_schema, db: MongoClient = Depends(get_db),
              Authorize: AuthJWT = Depends(), db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    exam_collection = db['exam']
    exam = exam_collection.find_one({'_id': ObjectId(exam_id)})
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    if user_id != exam['master_id']:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})
    new_exam = Exam(**request.__dict__)
    new_exam = new_exam.return_dict()
    new_exam['master_id'] = exam['master_id']
    exam_collection.update_one({'_id': ObjectId(exam_id)}, {'$set': new_exam})
    return 'ok'


@router.delete('/edit_exam/{exam_id}')
def delete_exam(exam_id, db: MongoClient = Depends(get_db),
                Authorize: AuthJWT = Depends(), db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    exam_collection = db['exam']
    exam = exam_collection.find_one({'_id': ObjectId(exam_id)})
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    if user_id != exam['master_id']:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})
    exam_collection.delete_one({'_id': ObjectId(exam_id)})
    return "ok"


@router.get('/search_exam/{text}', response_model=list[ExamResponse])
def search_exam(text, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    exam = db['exam']
    exam_list = exam.aggregate(
        [

            {"$lookup": {'from': "users", 'localField': "master_id", 'foreignField': "_id", 'as': "master"}},
            {"$project": {'_id': 1, 'name': 1, 'start_time': 1, 'end_time': 1, 'random_answer': 1, 'random_question': 1,
                          'uni_name': 1, 'one_page': 1, 'uid': 1, 'master_id': 1,
                          'master.name': 1}},
            {"$match": {"$or": [{'master.name': {'$regex': text}}, {'name': {'$regex': text}},
                                {'uid': {'$regex': text}}, {'uni_name': {'$regex': text}}]}}
        ])

    return list(exam_list)


@router.get('/add_exam')
def add_exam(request: Request, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    exams = db['exam']
    stu_id, exam_id, password = request.headers.get('stu_id'), request.headers.get('exam_id'), request.headers.get(
        'password')
    exam = exams.find_one({'_id': ObjectId(exam_id)})
    if not verify_password(password, exam['password']):
        return JSONResponse(status_code=402, content={"detail": 'wrong password'})
    exams.update_one({'_id': ObjectId(exam_id)}, {"$addToSet": {"stu_in_exam": {"user": ObjectId(stu_id)}}})
    return JSONResponse(status_code=200, content={"detail": 'successes'})


@router.get('/stu_page/{stu_id}', response_model=list[ExamResponse])
def stu_page(stu_id, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends(),
             db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    if user_id != stu_id:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})
    exams = db['exam']
    exam = exams.find({"stu_in_exam": {"$elemMatch": {"user": ObjectId(stu_id)}}})
    exam_list = []
    for i in exam:
        exam_list.append(Exam.change_date_to_jalali(i))
    return list(exam_list)


@router.post('/stu_answer/{exam_id}')
@router.post('/stu_answer')
async def stu_answer(r: Request, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends(),
                     exam_id: str | int = 0):
    Authorize.jwt_required()
    answers = await r.form()
    questions = db['questions']
    file_location = f"/files/answers/{answers['stu_id']}"
    path = os.getcwd()
    for i in answers:
        if i != 'stu_id':

            answer_type, question_id = i.split('_')
            user_answer = list(questions.aggregate(
                [
                    {"$match": {"_id": ObjectId(question_id)}},
                    {"$project": {
                        "answer": {"$filter": {"input": "$answers",
                                                "cond": {"$eq": ['$$this.user', ObjectId(answers['stu_id'])]}}}
                    }},
                ]))

            if answer_type == 'test' or answer_type == 'descriptive':
                if user_answer[0]['answer']:
                    questions.update_one({'_id': ObjectId(question_id),"answers.user":ObjectId(answers['stu_id'])},{"$set":{"answers.$.answer":answers[i],'answers.$.type': answer_type}})
                else:
                    questions.update_one({'_id': ObjectId(question_id)}, {"$push": {
                        "answers": {"user": ObjectId(answers['stu_id']), "answer": answers[i], 'type': answer_type}}})
            else:
                if not os.path.isdir(path + file_location):
                    os.mkdir(path + file_location)

                if not os.path.isdir(path + file_location + f"/{question_id}"):
                    os.mkdir(path + file_location + f"/{question_id}")

                with open(path + file_location + f"/{question_id}" + '/' + answers[i].filename, "wb") as file_object:
                    file = await answers[i].read()
                    file_object.write(file)

                if user_answer[0]['answer']:
                    questions.update_one({'_id': ObjectId(question_id),"answers.user":ObjectId(answers['stu_id'])},{"$set":{"answers.$.file_address":file_location + f"/{question_id}",'answers.$.file_name': answers[i].filename}})
                else:
                    questions.update_one(
                        {'_id': ObjectId(question_id)},
                        {"$push":
                             {"answers":
                                  {"user": ObjectId(answers['stu_id']), 'type': answer_type,
                                   "file_name": answers[i].filename, "file_address": file_location + f"/{question_id}"}}})

    if exam_id:
        exams = db['exam']
        exams.update_one({'_id': ObjectId(exam_id), 'stu_in_exam.user': ObjectId(answers['stu_id'])},
                         {"$set": {"stu_in_exam.$.status_login": 'finish'}})
    return JSONResponse(status_code=200, content={"detail": 'successes'})


@router.post('/load_question/{stu_id}', response_model=list[QuestionsR])
@router.post('/load_question', response_model=list[QuestionsR])
def load_question(request: LoadQuestions, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends(),
                  db_cash: redis = Depends(get_db_cash),
                  stu_id: str | int = 0):
    Authorize.jwt_required()
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    exam_id = request.exam_id
    exams = db['exam']
    exam = exams.aggregate(
        [
            {"$match": {"_id": ObjectId(exam_id)}},
            {"$lookup": {'from': "questions", 'localField': "_id", 'foreignField': "exam_id", 'as': "questions"}},
            {"$project": {'_id': 1, 'name': 1, 'start_time': 1, 'end_time': 1, 'random_answer': 1, 'random_question': 1,
                          'uni_name': 1, 'one_page': 1, 'uid': 1, 'master_id': 1,
                          'questions.choices': 1, 'questions.exam_id': 1, 'questions.file_address': 1, 'questions'
                                                                                                       '.file_name': 1,
                          'questions.question': 1, 'questions.type': 1, 'questions._id': 1}},

        ])
    exam = list(exam)[0]
    questions = exam['questions']
    if stu_id:
        try:
            Exam.validate_date(exam)
            exams.update_one({'_id': ObjectId(exam_id), 'stu_in_exam.user': ObjectId(stu_id)},
                             {"$set": {"stu_in_exam.$.status_login": 'login'}})
        except ValueError as e:
            return JSONResponse(status_code=400, content={"detail": str(e)})
    else:
        if user_id != exam['master_id']:
            return JSONResponse(status_code=401, content={"detail": 'unauthorized'})

    if exam['random_question']:
        questions = Question.random(questions)

    return questions


@router.get('/show_stu_answer/{stu_id}/{exam_id}', response_model=StuAnswers)
def show_stu_answer(stu_id, exam_id, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends(),
                  db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    user_id = db_cash.get(Authorize.get_raw_jwt()['jti']).decode()
    global flag
    exams = db['exam']
    exam = exams.aggregate(
        [
            {"$match": {"_id": ObjectId(exam_id)}},
            {"$match": {'master_id':ObjectId(user_id)}},
            {"$lookup": {'from': "questions", 'localField': "_id", 'foreignField': "exam_id", 'as': "questions"}},
            {"$project": {
                'questions': {"$map": {"input": "$questions", "as": "q",
                                "in": {"type": "$$q.type", "question": "$$q.question", "_id": "$$q._id",
                                       "file_address": "$$q.file_address", "file_name": "$$q.file_name",
                                       "exam_id": "$$q.exam_id", "options":"$$q.options","answer": {"$filter": {"input": "$$q.answers",
                                                                                         "cond": {"$eq": ['$$this.user',
                                                                                                          ObjectId(
                                                                                                              stu_id)]}}}}}}
            }},

        ])
    exam = list(exam)
    if not exam:
        return JSONResponse(status_code=401, content={"detail": 'unauthorized'})
    questions = exam[0]['questions']
    true_ans = 0
    wrong_ans = 0
    dont_ans = 0
    for i in questions:
        if i['answer']:
            i['answer'] = i['answer'][0]
        if i['type'] == 'test' and i['answer']:
            print(i)
            for choice in i['options']:
                flag = True
                if (choice['text'] == i['answer']['answer']) and choice['correct']:
                    true_ans += 1
                    flag = False
                    break
            if flag:
                wrong_ans += 1
        elif i['type'] == 'test' and not i['answer']:
            dont_ans += 1
    print(true_ans,wrong_ans,dont_ans)
    # questions = exam['questions']
    # if stu_id:
    #     try:
    #         Exam.validate_date(exam)
    #         exams.update_one({'_id': ObjectId(exam_id), 'stu_in_exam.user': ObjectId(stu_id)},
    #                          {"$set": {"stu_in_exam.$.status_login": 'login'}})
    #     except ValueError as e:
    #         return JSONResponse(status_code=400, content={"detail": str(e)})
    # else:
    #     if user_id != exam['master_id']:
    #         return JSONResponse(status_code=401, content={"detail": 'unauthorized'})
    #
    # if exam['random_question']:
    #     questions = Question.random(questions)

    return {'a_list':questions,'dont_ans':dont_ans,'true_ans':true_ans,'wrong_ans':wrong_ans}
