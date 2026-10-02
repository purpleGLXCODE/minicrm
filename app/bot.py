"""Telegram bot for collecting MiniCRM leads."""

import os

import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CRM_API_URL = os.getenv("CRM_API_URL", "http://127.0.0.1:8000/api")

dp = Dispatcher()
bot = Bot(token=TOKEN)

users = {}


def get_start_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🚀 Оставить заявку", callback_data="begin")
    return keyboard.as_markup()


def get_new_lead_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="➕ Новая заявка", callback_data="begin")
    return keyboard.as_markup()


async def send_welcome(message: types.Message):
    photo = FSInputFile("assets/bot_welcome.jpg")

    await message.answer_photo(
        photo=photo,
        caption=(
            "👋 <b>Добро пожаловать в Mini CRM!</b>\n\n"
            "Оставьте заявку прямо здесь — "
            "мы сохраним её в CRM и свяжемся с вами.\n\n"
            "Это займёт меньше минуты."
        ),
        reply_markup=get_start_keyboard(),
        parse_mode="HTML"
    )


@dp.message(Command("start"))
async def start(message: types.Message):
    users[message.from_user.id] = {"step": "request"}
    await send_welcome(message)


@dp.callback_query(F.data == "begin")
async def begin(callback: types.CallbackQuery):
    users[callback.from_user.id] = {"step": "request"}

    await callback.message.answer(
        "Что вас интересует?\n"
        "Коротко опишите ваш запрос 👇"
    )
    await callback.answer()


async def create_lead(user, request):
    username = user.username

    if username:
        contact = "@" + username
    else:
        contact = f"Telegram ID: {user.id}"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{CRM_API_URL}/leads",
            json={
                "name": user.full_name,
                "contact": contact,
                "request": request,
                "source": "telegram",
                "telegram_id": user.id,
            },
        ) as response:
            if response.status != 200:
                return False
            return True


@dp.message(F.text)
async def message(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = {"step": "request"}
        await message.answer(
            "Что вас интересует?\n"
            "Коротко опишите ваш запрос 👇"
        )
        return

    if users[user_id]["step"] == "request":
        request = message.text.strip()

        if await create_lead(message.from_user, request):
            del users[user_id]

            await message.answer(
                "✅ <b>Заявка принята!</b>\n\n"
                "Мы сохранили её в CRM и свяжемся с вами.",
                reply_markup=get_new_lead_keyboard(),
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "Не удалось сохранить заявку. "
                "Попробуйте отправить запрос ещё раз."
            )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
