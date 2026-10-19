import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from dotenv import load_dotenv

from app.card import format_card
from app.llm import ask

load_dotenv()
logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
KNOWLEDGE = Path("knowledge")
histories: dict[int, list[dict]] = {}


def build_system() -> str:
    prompt = (KNOWLEDGE / "system_prompt.md").read_text(encoding="utf-8")
    base = (KNOWLEDGE / "price.md").read_text(encoding="utf-8")
    return f"{prompt}\n\nБАЗА ЗНАНИЙ:\n{base}"


@dp.message(CommandStart())
async def start(message: types.Message):
    histories[message.chat.id] = []
    await message.answer(
        "Здравствуйте! Подскажу по материалам и срокам и помогу оформить заявку. "
        "Что нужно изготовить?"
    )


@dp.message(Command("id"))
async def my_id(message: types.Message):
    await message.answer(f"Ваш chat id: {message.chat.id}")


@dp.message(Command("demo"))
async def demo_card(message: types.Message):
    sample = {
        "name": "Алексей",
        "phone": "+7 900 000-00-00",
        "product": "Световой короб",
        "size": "2000 x 500 мм",
        "material": "акрил, LED-подсветка",
        "urgency": "в течение 7 дней",
        "files": "2 (CDR, PDF)",
        "notes": "нужен монтаж",
    }
    card = format_card(sample, message.from_user.username)
    await message.bot.send_message(int(os.environ["MANAGER_CHAT_ID"]), card)
    await message.answer("Тестовая карточка отправлена менеджеру.")


@dp.message(F.document | F.photo)
async def files(message: types.Message):
    manager = int(os.environ["MANAGER_CHAT_ID"])
    user = message.from_user
    who = f"{user.full_name} (@{user.username})" if user.username else user.full_name
    await message.bot.send_message(manager, f"Макет от клиента {who}, чат {message.chat.id}:")
    await message.forward(manager)
    if message.photo:
        await message.answer(
            "Получил, передал менеджеру. Telegram сжимает фото: для печати пришлите, "
            "пожалуйста, макет как файл (скрепка, затем «Файл»)."
        )
    else:
        await message.answer("Файл получен и передан менеджеру в исходном виде.")


@dp.message()
async def dialog(message: types.Message):
    if not message.text:
        await message.answer("Пока я понимаю текст и файлы с макетами.")
        return
    h = histories.setdefault(message.chat.id, [])
    h.append({"role": "user", "content": message.text})
    del h[:-20]
    while h and h[0]["role"] != "user":
        h.pop(0)
    reply = await ask(build_system(), h)
    h.append({"role": "assistant", "content": reply})
    await message.answer(reply)


async def main():
    bot = Bot(token=os.environ["BOT_TOKEN"])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
