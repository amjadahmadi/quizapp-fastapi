from pymongo import MongoClient
import redis

r = redis.Redis()
client = MongoClient('mongodb://localhost:27017/')
db = client['exam_creator']


def get_db():
    return db


def get_db_cash():
    return r
