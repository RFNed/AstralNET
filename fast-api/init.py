from fastapi import FastAPI, Request
from aiomysql import create_pool
from contextlib import asynccontextmanager
from config import *
from pydantic import BaseModel
from redis.asyncio import Redis
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
    app.state.redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD, username=REDIS_USERNAME)
    yield
    app.state.mysql_pool.close()
    await app.state.mysql_pool.wait_closed()

app = FastAPI(lifespan=lifespan, docs_url="/docs", redoc_url="/redoc", debug=True, title="AstralNet API", description="API for AstralNet services", version="1.0.0")

class AuthRequest(BaseModel):
    addr: str
    auth: str
    tx: int

@app.post("/auth")
async def authenticate(auth_request: AuthRequest):
    async with app.state.mysql_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT users.tg_id, protocols.name FROM `details_key` JOIN _keys ON _keys.id = details_key.id_key JOIN users on users.id = _keys.user_id JOIN protocols on protocols.id = details_key.id_protocol WHERE details_key.value1 = %s", (auth_request.auth,))
            result = await cursor.fetchone()
            count = await app.state.redis.incr(f"key:{auth_request.addr}")
            if count == 1:
                await app.state.redis.expire(f"key:{auth_request.addr}", 60)
            if count > 3:
                return {"ok": False, "error": "429"}
            if result:
                return {"ok": True, "id": str(result[0])}
            else:
                return {"ok": False, "error": "404"}