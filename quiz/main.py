import uvicorn
from fastapi import FastAPI, Request
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.responses import JSONResponse

import models

from routers import auth,tokens,exam

app = FastAPI()


app.include_router(auth.router)
app.include_router(tokens.router)
app.include_router(exam.router)




@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello")
async def say_hello(name: str = 'alo'):
    return {"message": f"Hello {name}"}

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )





if __name__ == "__main__":
    uvicorn.run(app)
