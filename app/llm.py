import logging
import os

import aiohttp

log = logging.getLogger(__name__)


async def ask(system: str, history: list[dict]) -> str:
    provider = os.getenv("LLM_PROVIDER", "anthropic")
    key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "")
    if not key:
        return "Модель пока не подключена."
    async with aiohttp.ClientSession() as s:
        if provider == "anthropic":
            r = await s.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                json={"model": model or "claude-sonnet-5-5", "max_tokens": 700,
                      "system": system, "messages": history},
            )
            data = await r.json()
            if r.status != 200:
                log.error("LLM error %s: %s", r.status, data)
                return "Не получилось ответить, попробуйте ещё раз."
            return data["content"][0]["text"]
        r = await s.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "max_tokens": 700,
                  "messages": [{"role": "system", "content": system}] + history},
        )
        data = await r.json()
        if r.status != 200:
            log.error("LLM error %s: %s", r.status, data)
            return "Не получилось ответить, попробуйте ещё раз."
        return data["choices"][0]["message"]["content"]
