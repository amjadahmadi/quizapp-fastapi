from decouple import config
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from core.database import get_db_cash

with open('public.pem', 'rb') as f:
    public_key = f.read().decode()

with open('private.pem', 'rb') as f:
    private_key = f.read().decode()

denylist = set()


class Settings(BaseModel):
    authjwt_algorithm: str = "RS512"
    authjwt_public_key: str = public_key
    authjwt_private_key: str = private_key
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}


# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return Settings()


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token['jti']
    db_cash = get_db_cash()
    val = db_cash.get(jti)
    return val is None
