import redis
from datetime import timedelta
from fastapi import APIRouter, Depends
from uuid import uuid4
from starlette import status
from core.database import get_db_cash
from JWT import AuthJWT


router = APIRouter(
    tags=['token'],
    prefix='/token'
)


@router.get('/blacklist', status_code=status.HTTP_200_OK)
def logout(Authorize: AuthJWT = Depends(), db_cash: redis = Depends(get_db_cash)):
    Authorize.jwt_required()
    jti = Authorize.get_raw_jwt()['jti']
    db_cash.delete(jti)
    return {"detail": "Access token has been revoke"}


@router.post('/refresh')
def refresh(Authorize: AuthJWT = Depends(), db_cash: redis = Depends(get_db_cash)):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    Authorize.jwt_refresh_token_required()
    jti = Authorize.get_raw_jwt()['jti']
    current_user = Authorize.get_jwt_subject()
    uid_access = uuid4()
    new_access_token = Authorize.create_access_token(subject=current_user, expires_time=timedelta(seconds=60),
                                                     user_claims={'jti': uid_access.__str__()})
    db_cash.set(name=uid_access.__str__(), value=db_cash.get(jti), ex=timedelta(seconds=60))
    return {"access_token": new_access_token}