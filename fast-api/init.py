from fastapi import FastAPI, Request
from aiomysql import create_pool
from contextlib import asynccontextmanager
from config import *
from pydantic import BaseModel
import asyncio, hashlib, hmac, time

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mysql_pool = await create_pool(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DB,
        charset=MYSQL_CHARSET,
        autocommit=True
    )
    yield
    app.state.mysql_pool.close()
    await app.state.mysql_pool.wait_closed()

app = FastAPI(lifespan=lifespan, docs_url="/docs", redoc_url="/redoc", debug=True, title="AstralNet API", description="API for AstralNet services", version="1.0.0")
