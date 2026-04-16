from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from asyncio import sleep
from random import uniform
from config import SALAMANDER_OBFS, SNI_HYSTERIA, HOST_HYSTERIA, HOST_VLESS, SNI_VLESS, PUBLIC_KEY
from uuid import uuid4
from secrets import token_hex, token_urlsafe
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
                        link += f"<code>vless://{item[3]}@{HOST_VLESS}/?type=tcp&encryption=none&flow=xtls-rprx-vision&sni={SNI_VLESS}&fp=chrome&security=reality&pbk={PUBLIC_KEY}&sid={item[2]}#AstralVLESS</code>"
                    values += f"\n🔑 <b>{item[1]}</b> → {link}"
                    await sleep(uniform(1.3, 2.6))
                await loading_msg.edit_text(f"💁‍♂️ <b>Ваши ключи доступа</b>:\n{values}")
        

@rutkey.message(Command("addkey"))
async def generate_key(message: Message, is_admin: bool, pool: aiomysql.Pool):
    if is_admin:
        arguments = message.text.split()
        if len(arguments) != 3:
            await message.answer("Использование: /addkey [tg_id] [duration_in_days]")
            return
        tg_id = arguments[1]
        message_load = await message.answer("💌")
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("select id from users where tg_id = %s", (tg_id,))
                user = await cursor.fetchone()
                if user:
                    await cursor.execute("select * from details_key join _keys on _keys.id = details_key.id_key join users on users.id = _keys.user_id where user_id = %s", (user[0],))
                    temp_result = await cursor.fetchone()
                    if not temp_result:
                        try:
                            await cursor.execute("INSERT INTO `_keys` (`id`, `user_id`, `expires_at`) VALUES (NULL, %s, DATE_ADD(NOW(), INTERVAL %s DAY))", (user[0], arguments[2]))
                            await cursor.execute("select id from _keys where user_id = %s", (user[0],))
                            id_key = await cursor.fetchone()
                            await cursor.execute("select id, name from protocols")
                            protocols = await cursor.fetchall()
                            for protocol in protocols:
                                if protocol[1] == "Hysteria":
                                    await cursor.execute("INSERT INTO `details_key` (`id`, `id_key`, `id_protocol`, `value1`, `value2`) VALUES (NULL, %s, %s, %s, NULL)", (id_key[0], protocol[0], token_urlsafe(12)))
                                elif protocol[1] == "VLESS":
                                    hex_token = token_hex(16)
                                    uuid_token = uuid4()
                                    await cursor.execute("INSERT INTO `details_key` (`id`, `id_key`, `id_protocol`, `value1`, `value2`) VALUES (NULL, %s, %s, %s, %s)", (id_key[0], protocol[0], str(hex_token), str(uuid_token)))
                        except:
                            await message_load.edit_text("⚠️ Произошла ошибка при генерации ключа доступа!")
                            return
                    else:
                        await message_load.edit_text("⚠️ Ключ доступа уже есть!")
                        return
        await sleep(uniform(3.3, 4.0))
        await message_load.edit_text("✅ Ключ доступа успешно сгенерирован!")
        await message.bot.send_message(tg_id, "👋 Привет! У тебя зарегистрирован ключ доступа! Узнай его через /start")

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