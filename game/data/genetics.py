"""
Genetics traits data module for BUNKER game.
"""
from typing import Dict, Any, List
import random

GENETICS_TRAITS: List[Dict[str, Any]] = [
    {"name": "Kuchli immunitet", "emoji": "🛡️", "description": "Har qanday mavjud infeksiya va viruslarga tabiiy chidamli.", "value_score": 95, "effect_type": "positive", "apocalypse_bonus": {"virus": 40, "biological": 40}},
    {"name": "Tez tiklanish (Regeneratsiya)", "emoji": "⚡", "description": "Yaralar va sinishlar oddiy odamlardan 2 barobar tez bitadi.", "value_score": 90, "effect_type": "positive", "apocalypse_bonus": {"nuclear": 25, "flood": 20}},
    {"name": "Yuqori jismoniy kuch geni", "emoji": "💪", "description": "Mushak tolalari zichligi yuqori, kam mashq bilan ham baquvvat.", "value_score": 85, "effect_type": "positive", "apocalypse_bonus": {}},
    {"name": "Sovuqqa chidamlilik geni", "emoji": "❄️", "description": "Tana harorati pasayishiga juda chidamli, qon aylanishi a'lo.", "value_score": 80, "effect_type": "positive", "apocalypse_bonus": {"ice_age": 50}},
    {"name": "Issiqqa va chanqoqqa chidamlilik", "emoji": "☀️", "description": "Kam suv bilan uzoq yashay oladi, suvsizlanishga bardoshli.", "value_score": 85, "effect_type": "positive", "apocalypse_bonus": {"volcano": 40, "solar_flare": 30}},
    {"name": "Zaif immunitet", "emoji": "🤒", "description": "Har qanday chang yoki mikrobdan tez kasal bo'ladi.", "value_score": 30, "effect_type": "negative", "apocalypse_bonus": {"virus": -40, "biological": -40}},
    {"name": "Chang va mog'orga allergiya", "emoji": "🤧", "description": "Bunkerdagi yopiq va chang havo sharoitida nafas qisishi mumkin.", "value_score": 40, "effect_type": "negative", "apocalypse_bonus": {}},
    {"name": "Oziq-ovqat allergiyasi (Glyuten/Laktaza)", "emoji": "🥛", "description": "Maxsus parhez talab qiladi, standart konservalar mos kelmasligi mumkin.", "value_score": 45, "effect_type": "negative", "apocalypse_bonus": {}},
    {"name": "Irsiy qandli diabet ehtimoli", "emoji": "🩸", "description": "Stress va noo'rin ovqatlanishdan qand miqdori o'ynab turadi.", "value_score": 35, "effect_type": "negative", "apocalypse_bonus": {}},
    {"name": "Yuqori intellekt (Genetik mutatsiya)", "emoji": "🧠", "description": "Ma'lumotlarni tez o'zlashtiradi, aql darajasi juda yuqori.", "value_score": 90, "effect_type": "positive", "apocalypse_bonus": {"ai_takeover": 30}},
    {"name": "Tez charchash sindromi", "emoji": "🥱", "description": "Mitoxondriyalar faoliyati sust, uzoq jismoniy ishga chidamsiz.", "value_score": 35, "effect_type": "negative", "apocalypse_bonus": {}},
    {"name": "Uzoq umr ko'rish geni", "emoji": "⏳", "description": "Qarish jarayoni sekin kechadi, hujayralar uzoq yosh saqlanadi.", "value_score": 85, "effect_type": "positive", "apocalypse_bonus": {}},
    {"name": "Antibiotiklarga chidamli flora", "emoji": "💊", "description": "Oddiy antibiotiklar ta'sir qilmaydi, davolash qiyin.", "value_score": 40, "effect_type": "negative", "apocalypse_bonus": {"virus": -20}},
    {"name": "Qorong'uda ko'rish qobiliyati (Tungi ko'rish)", "emoji": "👁️", "description": "Ko'z to'r pardasida tayoqchalar ko'p, chiroqsiz ham yaxshi ko'radi.", "value_score": 85, "effect_type": "positive", "apocalypse_bonus": {"solar_flare": 30}},
    {"name": "O'tkir eshitish qobiliyati", "emoji": "👂", "description": "Eng past tovush va yer qimirlashlarini oldindan sezadi.", "value_score": 75, "effect_type": "positive", "apocalypse_bonus": {}},
    {"name": "O'tkir hid sezish qobiliyati", "emoji": "👃", "description": "Zaharli gazlar va buzilgan ovqat hidini bir zumda aniqlaydi.", "value_score": 80, "effect_type": "positive", "apocalypse_bonus": {"biological": 30}},
    {"name": "Qon ivishining sekinligi (Gemofiliya xavfi)", "emoji": "🩸", "description": "Kichik jarohatda ham qon to'xtashi qiyin kechadi.", "value_score": 30, "effect_type": "negative", "apocalypse_bonus": {}},
    {"name": "Yuqori energiya va kam uyqu talabi", "emoji": "🔋", "description": "Kuniga 4 soat uxlab ham to'liq kuch bilan ishlay oladi.", "value_score": 90, "effect_type": "positive", "apocalypse_bonus": {}},
    {"name": "Radiatsiyaga tabiiy bardoshlilik", "emoji": "☢️", "description": "DNK reparatsiya tizimi yuqori, radiatsiya nurlariga chidamli.", "value_score": 95, "effect_type": "positive", "apocalypse_bonus": {"nuclear": 60}},
    {"name": "Mukammal tish va suyak tizimi", "emoji": "🦷", "description": "Kalsiy almashinuvi a'lo, uzoq yillar tish va suyak kasalliklariga chalinmaydi.", "value_score": 75, "effect_type": "positive", "apocalypse_bonus": {}}
]

def get_random_genetics() -> Dict[str, Any]:
    return random.choice(GENETICS_TRAITS)
