"""
Physical states data module for BUNKER game.
"""
from typing import Dict, Any, List
import random

PHYSICAL_STATES: List[Dict[str, Any]] = [
    {
        "name": "Juda kuchli (Professional atlet)",
        "emoji": "🏋️‍♂️",
        "value_score": 95,
        "endurance_modifier": 1.5,
        "work_capacity": "Maksimal og'ir ishlarni bajara oladi, charchamaydi."
    },
    {
        "name": "Kuchli va baquvvat",
        "emoji": "💪",
        "value_score": 85,
        "endurance_modifier": 1.2,
        "work_capacity": "Barcha jismoniy mehnat turlariga to'liq layoqatli."
    },
    {
        "name": "O'rtacha sog'lom",
        "emoji": "🏃",
        "value_score": 70,
        "endurance_modifier": 1.0,
        "work_capacity": "Standart kundalik ishlarni normal bajara oladi."
    },
    {
        "name": "Zaif (Kamharakat)",
        "emoji": "🚶",
        "value_score": 45,
        "endurance_modifier": 0.7,
        "work_capacity": "Tez charchaydi, og'ir yuk ko'tara olmaydi."
    },
    {
        "name": "Juda zaif (Holsiz)",
        "emoji": "🛌",
        "value_score": 25,
        "endurance_modifier": 0.4,
        "work_capacity": "Faqat o'tirib bajariladigan yengil ishlarga layoqatli."
    },
    {
        "name": "Nogironligi bor (Harakati cheklangan)",
        "emoji": "🦽",
        "value_score": 35,
        "endurance_modifier": 0.5,
        "work_capacity": "Aqliy yoki maxsus o'tirgan joydagi ishlarni bajaradi."
    },
    {
        "name": "Chidamli marafonchi",
        "emoji": "🫀",
        "value_score": 90,
        "endurance_modifier": 1.4,
        "work_capacity": "Uzoq davom etadigan bir xil ishlarda charchamaydi."
    },
    {
        "name": "Epchil va egiluvchan",
        "emoji": "🤸",
        "value_score": 80,
        "endurance_modifier": 1.1,
        "work_capacity": "Tor lyuklar va ventilyatsiya quvurlariga kira oladi."
    }
]

def get_random_physical_state() -> Dict[str, Any]:
    return random.choice(PHYSICAL_STATES)
