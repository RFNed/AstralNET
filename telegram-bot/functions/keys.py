from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
import aiomysql
rutkey = Router()

@rutkey.callback_query(lambda c: c.data == "get_key")
async def get_key_callback_handler(callback_query: CallbackQuery, is_user: bool):
    if is_user:
        await callback_query.message.answer("@RFNed")
        await callback_query.answer()

@rutkey.callback_query(lambda c: c.data == "take_my_key")
async def take_my_key_callback_handler(callback_query: CallbackQuery, is_user: bool, pool: aiomysql.Pool):
    if is_user:
        loading_msg = await callback_query.message.answer("⏳")
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT uuid_key, key_hash FROM _keys WHERE user_id = (SELECT id FROM users WHERE tg_id = %s)", (callback_query.from_user.id,))
                result = await cur.fetchone()
                await loading_msg.delete()
                key = f"vless:"
                if result:
                    await callback_query.message.answer(f"🔑 Ваш ключ доступа: <code>{result[0]}</code>")
        
    await callback_query.answer()


@rutkey.callback_query(lambda c: c.data == "keys")
async def keys_callback_handler(callback_query: CallbackQuery, is_user: bool, pool: aiomysql.Pool):
    if is_user:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("select expires_at, access_level.name from _keys join users on users.id = _keys.user_id join access_level on access_level.id = users.access where users.tg_id = %s", (callback_query.from_user.id,))
                result = await cur.fetchone()
                if result and result[0]:
                    expires_at = result[0]
                    access_level = result[1]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔐 Скопировать токен", callback_data="take_my_key")],
                        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
                    ])
                    await callback_query.message.edit_text(f"🔑 Ваш ключ доступа действителен до: <code>{expires_at}</code>\n📊 Уровень доступа: <code>{access_level}</code>\n\nЛокация: 🇫🇮", reply_markup=keyboard)
                else:
                     keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="➕ Получить ключ доступа", callback_data="get_key")],
                        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
                     ])
                     await callback_query.message.edit_text("У вас нет активного ключа доступа.", reply_markup=keyboard)
    await callback_query.answer()