"""
Knowledge domains data module for BUNKER game.
"""
from typing import Dict, Any, List
import random

KNOWLEDGE_DOMAINS: List[Dict[str, Any]] = [
    {"name": "Tibbiyot", "emoji": "🩺", "value_score": 95, "bunker_use": "Kasalliklarni davolash, jarrohlik va dori dozalash."},
    {"name": "Texnika va Mexanika", "emoji": "⚙️", "value_score": 90, "bunker_use": "Bunker generatorlari, motorlari va nasoslarini ta'mirlash."},
    {"name": "Qishloq xo'jaligi", "emoji": "🌾", "value_score": 90, "bunker_use": "Gidroponika, tuproq unumdorligi va urug'chilik."},
    {"name": "Harbiy taktika va Xavfsizlik", "emoji": "🛡️", "value_score": 85, "bunker_use": "Bunkerni tashqi hujumlardan himoyalash va patrul."},
    {"name": "Axborot texnologiyalari (IT)", "emoji": "💻", "value_score": 75, "bunker_use": "Kiberxavfsizlik, dasturiy ta'minot va ma'lumotlar bazasi."},
    {"name": "Biologiya va Genetika", "emoji": "🧬", "value_score": 85, "bunker_use": "Mikroorganizmlar, viruslar va o'simlik mutatsiyalarini o'rganish."},
    {"name": "Kimyo va Toksikologiya", "emoji": "🧪", "value_score": 90, "bunker_use": "Havo va suvni zararsizlantirish, reagentlar tayyorlash."},
    {"name": "Qurilish va Arxitektura", "emoji": "🏗️", "value_score": 85, "bunker_use": "Bunker devorlari mustahkamligi va yangi xonalar kengaytirish."},
    {"name": "Psixologiya va Konfliktologiya", "emoji": "🧠", "value_score": 80, "bunker_use": "Tor muhitdagi stress, depressiya va nizolarni bartaraf etish."},
    {"name": "Energetika (Yadro va Quyosh)", "emoji": "⚡", "value_score": 95, "bunker_use": "Elektr tarmoqlari, reaktor va akkumulyatorlarni boshqarish."},
    {"name": "Fizika va Radiatsiya", "emoji": "⚛️", "value_score": 85, "bunker_use": "Radiatsiya darajasini o'lchash va himoya ekranlari hisobi."},
    {"name": "Matematika va Ehtimollar nazariyasi", "emoji": "📐", "value_score": 70, "bunker_use": "Resurslar sarfi va logistika hisob-kitoblari."},
    {"name": "Ekologiya va Tabiatni asrash", "emoji": "🌍", "value_score": 75, "bunker_use": "Yopiq ekotizim aylanishini saqlash."},
    {"name": "Oziq-ovqat texnologiyasi", "emoji": "🥫", "value_score": 90, "bunker_use": "Konservalash, quritish va oziq-ovqatni uzoq saqlash."},
    {"name": "Radioaloqa va Telekommunikatsiya", "emoji": "📡", "value_score": 85, "bunker_use": "Sun'iy yo'ldosh va yer usti signallarini tutish."},
    {"name": "Gidrologiya va Suv ta'minoti", "emoji": "💧", "value_score": 95, "bunker_use": "Yer osti suv manbalarini topish va tozalash tizimlari."},
    {"name": "Geologiya va Mineralogiya", "emoji": "⛏️", "value_score": 75, "bunker_use": "Yer qatlamlari siljishi va zilzila xavfini baholash."},
    {"name": "Meteorologiya va Iqlim", "emoji": "🌪️", "value_score": 70, "bunker_use": "Tashqi atmosfera sharoiti va radiatsion bulutlarni kuzatish."}
]

def get_random_knowledge() -> Dict[str, Any]:
    return random.choice(KNOWLEDGE_DOMAINS)

def get_knowledge_by_name(name: str) -> Dict[str, Any]:
    for k in KNOWLEDGE_DOMAINS:
        if k["name"].lower() == name.lower():
            return k
    return KNOWLEDGE_DOMAINS[0]
