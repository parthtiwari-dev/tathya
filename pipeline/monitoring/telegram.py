"""Optional Telegram alert delivery for source-health failures."""

import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv


def send_alert(message: str) -> bool:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    payload = urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
    request = Request(f"https://api.telegram.org/bot{token}/sendMessage", data=payload, method="POST")
    with urlopen(request, timeout=20) as response:  # noqa: S310 -- Telegram URL is fixed.
        return response.status == 200
