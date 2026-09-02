"""
Health states data module for the BUNKER game.
"""

from __future__ import annotations
import random
from typing import Any

HEALTH_STATES: list[dict[str, Any]] = [
    {
        "name": "Alo",
        "emoji": "💪",
        "value_score": 100,
        "description": "Mutlaqo soghlom, hech qanday kasalligi yoq. Jismoniy va ruhiy holati mukammal.",
        "special_effect": "Har bir raundda +5 resurs ishlash qobiliyati",
        "apocalypse_penalty": {"virus": 0, "nuclear": 0, "biological": 0, "flood": 0, "ice_age": 0},
    },
    {
        "name": "Yaxshi",
        "emoji": "😊",
        "value_score": 85,
        "description": "Umuman soghlom, kichik muammolari bolishi mumkin lekin faoliyatiga tasir qilmaydi.",
        "special_effect": None,
        "apocalypse_penalty": {"virus": 0, "nuclear": 0, "biological": 0, "flood": 0, "ice_age": 0},
    },
    {
        "name": "Ortacha",
        "emoji": "😐",
        "value_score": 65,
        "description": "Qisman soghlom, bazi cheklovlar bor. Ogir ishlarni bajarish qiyin.",
        "special_effect": "Ogir vazifalar uchun -10 samaradorlik",
        "apocalypse_penalty": {"virus": 5, "nuclear": 5, "biological": 5, "flood": 5, "ice_age": 10},
    },
    {
        "name": "Zaif",
        "emoji": "😔",
        "value_score": 40,
        "description": "Soghligi yaxshi emas, koplab cheklovlar mavjud. Doimiy tibbiy nazorat talab etiladi.",
        "special_effect": "Barcha vazifalar uchun -20 samaradorlik",
        "apocalypse_penalty": {"virus": 15, "nuclear": 10, "biological": 20, "flood": 15, "ice_age": 20},
    },
    {
        "name": "Surunkali kasallik (qand kasalligi)",
        "emoji": "🩸",
        "value_score": 45,
        "description": "Qand kasalligi bor, muntazam insulin yoki dori kerak. Resurslarni koprok sarflaydi.",
        "special_effect": "Insulin zaxirasi tugasa, har raundda -15 HP",
        "apocalypse_penalty": {"virus": 10, "nuclear": 10, "biological": 15, "flood": 10, "ice_age": 15},
    },
    {
        "name": "Surunkali kasallik (yurak)",
        "emoji": "❤️‍🩹",
        "value_score": 40,
        "description": "Yurak kasalligi bor. Stressli vaziyatlarda holati yomonlashishi mumkin.",
        "special_effect": "Stress hodisalarida 30% elimlash xavfi oshadi",
        "apocalypse_penalty": {"virus": 10, "nuclear": 15, "biological": 10, "flood": 20, "ice_age": 20},
    },
    {
        "name": "Nogironlik",
        "emoji": "♿",
        "value_score": 30,
        "description": "Jismoniy nogironlik. Harakat cheklangan, lekin intellektual salohiyat toliq saqlanadi.",
        "special_effect": "Jismoniy vazifalar uchun -40 samaradorlik, aqliy vazifalar uchun +10",
        "apocalypse_penalty": {"virus": 5, "nuclear": 15, "biological": 5, "flood": 30, "ice_age": 25},
    },
    {
        "name": "Immuniteti kuchli",
        "emoji": "🛡️",
        "value_score": 92,
        "description": "Gayrioddiy kuchli immunitet tizimi. Viruslar va infeksiyalarga qarshi barqaror.",
        "special_effect": "Virus va biologik falokatlarda -50% kasallik xavfi",
        "apocalypse_penalty": {"virus": -20, "nuclear": 0, "biological": -25, "flood": 0, "ice_age": 0},
    },
    {
        "name": "Immuniteti zaif",
        "emoji": "🤒",
        "value_score": 35,
        "description": "Immunitet tizimi juda zaif. Har qanday infeksiyaga tez chalinadi.",
        "special_effect": "Barcha infeksion hodisalarda +50% kasallik xavfi",
        "apocalypse_penalty": {"virus": 30, "nuclear": 10, "biological": 35, "flood": 15, "ice_age": 20},
    },
    {
        "name": "Noomalum kasallik",
        "emoji": "❓",
        "value_score": 25,
        "description": "Aniqlanmagan kasallik. Hech kim uning nima ekanini bilmaydi, bu oyin ichida sir bolib qolishi mumkin.",
        "special_effect": "Har raundda 10% holati yomonlashuv ehtimoli",
        "apocalypse_penalty": {"virus": 20, "nuclear": 20, "biological": 25, "flood": 20, "ice_age": 25},
    },
    {
        "name": "Virus tashuvchisi",
        "emoji": "🦠",
        "value_score": 15,
        "description": "Virusni tashiydi lekin ozi kasal emas. Atrofdagilarga xavf tugdiradi.",
        "special_effect": "Virus falokati raundida har raundda 20% boshqa oyinchini yuqtirish ehtimoli",
        "apocalypse_penalty": {"virus": 40, "nuclear": 0, "biological": 45, "flood": 0, "ice_age": 0},
    },
    {
        "name": "Soghlom sportchi",
        "emoji": "🏃",
        "value_score": 96,
        "description": "Professional sportchi darajasida jismoniy holat. Chidamlilik va kuch yuqori darajada.",
        "special_effect": "Jismoniy vazifalar uchun +20 samaradorlik, Jismoniy chidamlilik +30%",
        "apocalypse_penalty": {"virus": 0, "nuclear": -5, "biological": 0, "flood": -10, "ice_age": -10},
    },
    {
        "name": "Ruhiy buzilish",
        "emoji": "🌀",
        "value_score": 30,
        "description": "Ruhiy salomatlik muammolari bor. Stress ostida kutilmagan xatti-harakatlar qilishi mumkin.",
        "special_effect": "Har 3 raundda bir marta tasodifiy harakat qilish ehtimoli 25%",
        "apocalypse_penalty": {"virus": 10, "nuclear": 20, "biological": 10, "flood": 15, "ice_age": 25},
    },
    {
        "name": "Tiklanish jarayonida",
        "emoji": "🩹",
        "value_score": 55,
        "description": "Ogir kasallik yoki jarohatdan tuzalmoqda. Asta-sekin yaxshilanmoqda.",
        "special_effect": "Har 2 raundda value_score +5 oshadi (maksimum 80 gacha)",
        "apocalypse_penalty": {"virus": 10, "nuclear": 5, "biological": 15, "flood": 10, "ice_age": 10},
    },
    {
        "name": "Allergik reaktsiya",
        "emoji": "🤧",
        "value_score": 60,
        "description": "Kuchli allergiya. Bazi muhitlarda holati keskin yomonlashishi mumkin.",
        "special_effect": "Tog yoki osimlik kop bolgan muhitda -15 samaradorlik",
        "apocalypse_penalty": {"virus": 10, "nuclear": 5, "biological": 15, "flood": 0, "ice_age": 5},
    },
]


def get_random_health_state() -> dict[str, Any]:
    """Return a random health state from the list."""
    return random.choice(HEALTH_STATES)


def get_health_state_by_name(name: str) -> dict[str, Any] | None:
    """Return a health state dict by name, or None if not found."""
    for state in HEALTH_STATES:
        if state["name"].lower() == name.lower():
            return state
    return None


def get_states_by_effect_type(positive: bool = True) -> list[dict[str, Any]]:
    """Return health states filtered by whether they are broadly positive or negative."""
    threshold = 70
    if positive:
        return [s for s in HEALTH_STATES if s["value_score"] >= threshold]
    return [s for s in HEALTH_STATES if s["value_score"] < threshold]
