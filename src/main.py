from contextlib import asynccontextmanager
from typing import AsyncGenerator

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.auth.router import router as auth_router
from src.receipts.router import router as receipts_router
from src.database import database
from src.config import Settings


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator:
    await database.connect()

    yield

    await database.disconnect()


app = FastAPI(
    lifespan=lifespan,
    redoc_url=None,
)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(auth_router, prefix="/auth")
app.include_router(receipts_router, prefix="/receipts")
