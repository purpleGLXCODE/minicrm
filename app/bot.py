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
    users[message.from_user.id] = {"step": "name"}
    await send_welcome(message)


@dp.callback_query(F.data == "begin")
async def begin(callback: types.CallbackQuery):
    users[callback.from_user.id] = {"step": "name"}

    await callback.message.answer(
        "Как вас зовут?"
    )
    await callback.answer()


async def create_lead(user_id, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{CRM_API_URL}/leads",
            json={
                "name": data["name"],
                "contact": data["contact"],
                "request": data["request"],
                "source": "telegram",
            },
        ) as response:
            if response.status != 200:
                return False
            return True


@dp.message(F.text)
async def message(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = {"step": "name"}
        await message.answer("Как вас зовут?")
        return

    user = users[user_id]
    text = message.text.strip()

    if user["step"] == "name":
        user["name"] = text
        user["step"] = "contact"
        await message.answer(
            "Отлично!\n\n"
            "Как с вами связаться?\n"
            "Telegram, телефон или email."
        )
        return

    if user["step"] == "contact":
        user["contact"] = text
        user["step"] = "request"
        await message.answer(
            "И последний вопрос 👇\n\n"
            "Что вас интересует?\n"
            "Коротко опишите ваш запрос."
        )
        return

    if user["step"] == "request":
        user["request"] = text

        if await create_lead(user_id, user):
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
