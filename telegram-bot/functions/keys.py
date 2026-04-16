from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from asyncio import sleep
from random import uniform
from config import SALAMANDER_OBFS, SNI_HYSTERIA, HOST_HYSTERIA, HOST_VLESS, SNI_VLESS, PUBLIC_KEY
import aiomysql
rutkey = Router()

@rutkey.callback_query(lambda c: c.data == "get_key")
async def get_key_callback_handler(callback_query: CallbackQuery, is_user: bool):
    if is_user:
        await callback_query.message.answer("@RFNed")
        await callback_query.answer()

@rutkey.callback_query(lambda c: c.data == "take_my_key")
async def take_my_key_callback_handler(callback_query: CallbackQuery, is_user: bool, pool: aiomysql.Pool):
    await callback_query.answer()
    if is_user:
        loading_msg = await callback_query.message.answer("⏳")
        values = ""
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
select users.tg_id, protocols.name, details_key.value1, details_key.value2 
from details_key 
join protocols on protocols.id = details_key.id_protocol 
join _keys on _keys.id = details_key.id_key 
join users on users.id = _keys.user_id 
where users.tg_id = %s
                                     """, (callback_query.from_user.id,))
                result = await cursor.fetchall()
                for item in result:
                    link = ""
                    if item[1] == "Hysteria":
                        link += f"<code>hysteria2://{item[2]}@{HOST_HYSTERIA}?obfs=salamander&obfs-password={SALAMANDER_OBFS}&sni={SNI_HYSTERIA}#AstralHysteria</code>"
                    elif item[1] == "VLESS":
                        link += f"<code>vless://{item[2]}@{HOST_VLESS}/?type=tcp&encryption=none&flow=xtls-rprx-vision&sni={SNI_VLESS}&fp=chrome&security=reality&pbk={PUBLIC_KEY}&sid={item[3]}#AstralVLESS</code>"
                    values += f"\n🔑 <b>{item[1]}</b> → {link}"
                    await sleep(uniform(1.3, 2.6))
                await loading_msg.edit_text(f"💁‍♂️ <b>Ваши ключи доступа</b>:\n{values}")
        
    


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