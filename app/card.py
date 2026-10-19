import os
from datetime import datetime
from zoneinfo import ZoneInfo

FIELDS = [
    ("name", "Имя"),
    ("phone", "Телефон"),
    ("product", "Тип изделия"),
    ("size", "Размеры"),
    ("material", "Материал"),
    ("urgency", "Срочность"),
    ("files", "Макеты"),
    ("notes", "Примечания"),
]


def format_card(data: dict, username: str | None = None) -> str:
    tz = ZoneInfo(os.getenv("TIMEZONE", "Europe/Moscow"))
    lines = [f"Новая заявка, {datetime.now(tz):%d.%m.%Y %H:%M}"]
    for key, title in FIELDS:
        lines.append(f"{title}: {data.get(key) or 'не указано'}")
    if username:
        lines.append(f"Telegram: @{username}")
    return "\n".join(lines)
