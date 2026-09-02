"""
utils/crypto.py
BUNKER o'yini uchun kriptografik yordamchi funksiyalar.
HMAC-SHA256 imzolash, callback ma'lumotlarini kodlash va dekodlash.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from typing import Any

from redis.asyncio import Redis


def sign_data(data: str, secret: str) -> str:
    """HMAC-SHA256 imzosi qaytaradi.

    Args:
        data: Imzolanadigan ma'lumot string.
        secret: Maxfiy kalit.

    Returns:
        Hex-encoded HMAC-SHA256 imzosi.
    """
    return hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256,
    ).hexdigest()


def verify_signature(
    data: str,
    signature: str,
    secret: str,
    max_age_seconds: int = 300,
) -> bool:
    """Imzoni va vaqt yangiligini tekshiradi.

    Args:
        data: Tekshiriladigan ma'lumot (timestamp|payload formatida).
        signature: Kutilgan imzo.
        secret: Maxfiy kalit.
        max_age_seconds: Ruxsat etilgan maksimal yosh (soniyalarda).

    Returns:
        Imzo to'g'ri va vaqt yangi bo'lsa True.
    """
    expected = sign_data(data, secret)
    if not hmac.compare_digest(expected, signature):
        return False
    try:
        timestamp_str, _ = data.split("|", 1)
        timestamp = int(timestamp_str)
    except (ValueError, IndexError):
        return False
    return (int(time.time()) - timestamp) <= max_age_seconds


def encode_callback_data(
    action: str,
    game_id: int,
    user_id: int,
    extra: dict[str, Any] | None = None,
) -> str:
    """Callback ma'lumotlarini kompakt formatda kodlaydi.

    Telegram callback_data uchun 64 baytdan oshmasligi kerak.
    To'liq ma'lumot Redis'da saqlanadi, callback'da faqat kalit yuboriladi.

    Args:
        action: Amal nomi.
        game_id: O'yin identifikatori.
        user_id: Foydalanuvchi identifikatori.
        extra: Qo'shimcha ma'lumotlar (ixtiyoriy).

    Returns:
        Kompakt callback string (UUID asosida kalit).
    """
    short_key = uuid.uuid4().hex[:12]
    payload = {
        "action": action,
        "game_id": game_id,
        "user_id": user_id,
        "extra": extra or {},
        "ts": int(time.time()),
    }
    # Returns the short key; full payload stored separately via store_callback_payload
    return f"cb:{short_key}"


async def store_callback_payload(
    key: str,
    payload: dict[str, Any],
    redis_client: Redis,
    ttl_seconds: int = 3600,
) -> None:
    """Callback payload'ni Redis'da saqlaydi.

    Args:
        key: encode_callback_data tomonidan qaytarilgan kalit.
        payload: Saqlanadigan to'liq ma'lumot.
        redis_client: Async Redis ulanishi.
        ttl_seconds: Yaroqlilik muddati soniyalarda.
    """
    await redis_client.setex(key, ttl_seconds, json.dumps(payload))


async def decode_callback_data(
    encoded: str,
    redis_client: Redis,
) -> dict[str, Any] | None:
    """Callback ma'lumotlarini dekodlaydi va tekshiradi.

    Args:
        encoded: encode_callback_data tomonidan qaytarilgan string.
        redis_client: Async Redis ulanishi.

    Returns:
        Dekodlangan payload dict yoki None (yaroqsiz bo'lsa).
    """
    if not encoded.startswith("cb:"):
        return None
    raw = await redis_client.get(encoded)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
