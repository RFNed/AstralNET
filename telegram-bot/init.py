from config import *
from typing import Any, Awaitable, Callable, Dict
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.filters import CommandStart, Command
from aiogram.types import TelegramObject, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from .functions.keys import rutkey
import json, aiofiles, aiomysql, asyncio, logging
import redis.asyncio as Redis
logging.basicConfig(level=logging.DEBUG)


class AdminMiddleware(BaseMiddleware):
    def __init__(self, db_pool: aiomysql.Pool):
        self.db_pool = db_pool
        super().__init__()
    
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = getattr(event, 'from_user', None)
        if user:
            user_id = user.id
            async with self.db_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT access FROM users WHERE tg_id = %s", (user_id,))
                    result = await cur.fetchone()
                    data['is_user'] = True if result else False
                    data['is_admin'] = True if result and result[0] == 3 else False
        else:
            data["is_admin"] = False
            data["is_user"] = False
        return await handler(event, data)

redis = Redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD, username=REDIS_USERNAME)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=RedisStorage(redis))

@dp.message(CommandStart())
async def command_start_handler(message: Message, is_user: bool):
    if is_user:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔑 Доступ", callback_data="keys")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
        ])
        await message.answer(f"""
👋 Привет, <b>{message.from_user.full_name}</b>
Выбери опцию из меню ниже, чтобы начать работу с ботом!
                             """, reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu_callback_handler(callback_query, is_user: bool):
    if is_user:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔑 Доступ", callback_data="keys")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
        ])
        await callback_query.message.edit_text(f"""👋 Привет, <b>{callback_query.from_user.full_name}</b>
Выбери опцию из меню ниже, чтобы начать работу с ботом!""", reply_markup=keyboard)



async def main():
    pool = await aiomysql.create_pool(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB, charset=MYSQL_CHARSET, autocommit=True)
    dp.message.middleware(AdminMiddleware(pool))
    dp.callback_query.middleware(AdminMiddleware(pool))
    try:
        dp.include_router(rutkey)
        dp.workflow_data['pool'] = pool
        await dp.start_polling(bot, pool=pool)
    finally:
        pool.close()
        await pool.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())