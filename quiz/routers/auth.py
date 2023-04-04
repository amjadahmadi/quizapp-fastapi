import redis
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from uuid import uuid4
from starlette import status
from starlette.responses import JSONResponse
from models.user import User
from core.database import get_db, get_db_cash
from pymongo import MongoClient
from JWT import AuthJWT
from schemas.authenticate import Login, UserResponse, User as User_schema
from core.utils import verify_password

router = APIRouter(
    tags=['authenticate'],
    prefix='/auth'
)


@router.post('/register', status_code=201)
def register(request: User_schema, db: MongoClient = Depends(get_db)):
    users = db['users']
    try:
        print(request)
        user = User(**request.__dict__)
        users.insert_one(user.return_dict())
        return 'successes'
    except ValueError as e:
        return JSONResponse(status_code=406, content={"detail": str(e)})


@router.post('/login')
def login(request: Login, db: MongoClient = Depends(get_db), Authorize: AuthJWT = Depends(),
          db_cash: redis = Depends(get_db_cash)):
    user = db['users']
    user = user.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no')
    if not verify_password(request.password, user['password']):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='wrong pass')
    uid_access = uuid4()
    uid_refresh = uuid4()

    access_token = Authorize.create_access_token(subject=user['email'], expires_time=timedelta(hours=2),
                                                 user_claims={'jti': uid_access.__str__()})
    refresh_token = Authorize.create_refresh_token(subject=user['email'], expires_time=timedelta(days=1),
                                                   user_claims={'jti': uid_refresh.__str__()})

    db_cash.set(name=uid_access.__str__(), value=str(user['_id']), ex=timedelta(hours=2))
    db_cash.set(name=uid_refresh.__str__(), value=str(user['_id']), ex=timedelta(days=1))
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get('/userinfo', response_model=UserResponse)
def user_info(Authorize: AuthJWT = Depends(), db: MongoClient = Depends(get_db)):
    Authorize.jwt_required()
    users = db['users']
    current_user = Authorize.get_jwt_subject()
    return users.find_one({'email':current_user})
