"""
Apocalypse scenarios data module for BUNKER game.
Contains 12 rich apocalyptic scenarios with thematic modifiers and rules.
"""
from typing import Dict, Any, List
import random

APOCALYPSE_SCENARIOS: List[Dict[str, Any]] = [
    {
        "type": "nuclear",
        "name": "Yadro urushi",
        "emoji": "☢️",
        "description": "Global yadroviy zarbalar oqibatida yer yuzasi kuchli radiatsiya va chang buluti bilan qoplandi. Tashqarida yadro qishi boshlandi.",
        "duration_years": 10,
        "profession_bonuses": {
            "Fizik": 35, "Energetik": 30, "Shifokor": 25, "Jarroh": 25, "Muhandis": 30,
            "Harbiy": 25, "Quruvchi": 20, "Kimyogar": 30, "Qutqaruvchi": 25
        },
        "health_penalties": {
            "Zaif immunitet": -30, "Nogironlik": -20, "Surunkali kasallik": -20
        },
        "knowledge_bonuses": {
            "Fizika va Radiatsiya": 35, "Energetika": 30, "Tibbiyot": 25, "Kimyo va Toksikologiya": 30
        },
        "item_bonuses": {
            "Dozimetr / Radiometr (Raqamli)": 35, "Qo'rg'oshin plastina (Radiatsiyadan himoya ekrani)": 30,
            "Gaz niqobi (Professional filtr bilan, 2 dona)": 25
        },
        "special_rules": "Radiatsiya tufayli tashqariga chiqish mutlaqo taqiqlangan. Fizik va kimyogarlar alohida qadrga ega."
    },
    {
        "type": "virus",
        "name": "Global virus epidemiyasi",
        "emoji": "🦠",
        "description": "Tez tarqaluvchi mutatsion virus insoniyatning 95% qismini qirdi. Havo va suv orqali yuqadi.",
        "duration_years": 5,
        "profession_bonuses": {
            "Shifokor": 40, "Jarroh": 35, "Biolog": 40, "Kimyogar": 30, "Feldsher": 30,
            "Veterinar": 25, "Psixolog": 20
        },
        "health_penalties": {
            "Virus tashuvchisi": -60, "Zaif immunitet": -40, "Surunkali kasallik": -25
        },
        "knowledge_bonuses": {
            "Tibbiyot": 40, "Biologiya va Genetika": 40, "Kimyo va Toksikologiya": 30
        },
        "item_bonuses": {
            "Antibiotiklar zaxirasi (Keng spektrli, 6 oylik)": 35, "Tibbiy sumka (To'liq to'plam)": 30,
            "Dezinfeksiya vositasi (5 litr spirt + xlor eritmasi)": 30
        },
        "special_rules": "Har qanday kasallik belgisi bo'lgan o'yinchilar shubha ostida qoladi. Tibbiyot xodimlari o'yinda hal qiluvchi ahamiyatga ega."
    },
    {
        "type": "flood",
        "name": "Global suv toshqini",
        "emoji": "🌊",
        "description": "Muzliklarning to'liq erishi va yer qobig'i siljishi sabab quruqlikning 90% suv ostida qoldi. Bunker baland tog' cho'qqisida joylashgan.",
        "duration_years": 8,
        "profession_bonuses": {
            "Gidrogeolog": 35, "Dengizchi": 35, "Suvchi (dalg'ich)": 40, "Santexnik": 30,
            "Muhandis": 25, "Baliqchi": 30, "Qutqaruvchi": 25
        },
        "health_penalties": {
            "Harakati cheklangan": -25, "Zaif": -15
        },
        "knowledge_bonuses": {
            "Gidrologiya va Suv ta'minoti": 40, "Texnika va Mexanika": 25, "Ekologiya": 20
        },
        "item_bonuses": {
            "Portativ suv filtri (Keramika)": 35, "Suvni distillash uskunasi (Kichik laboratoriya)": 35,
            "Germetik yopiluvchi suv o'tkazmas sumka (Draybeg 60L)": 20
        },
        "special_rules": "Suv filtrlash va nasoslarni boshqara oladigan mutaxassislar eng qadrli hisoblanadi."
    },
    {
        "type": "ice_age",
        "name": "Yangi muzlik davri",
        "emoji": "❄️",
        "description": "Yer orbitasining o'zgarishi tufayli harorat -60 darajagacha tushdi. Butun sayyora qalin qor va muz bilan qoplandi.",
        "duration_years": 15,
        "profession_bonuses": {
            "Energetik": 40, "Elektrik": 35, "Mexanik": 30, "Tikuvchi": 30,
            "Alpinist": 25, "Meteorolog": 25, "Oshpaz": 20
        },
        "health_penalties": {
            "Zaif": -25, "Surunkali kasallik (yurak)": -30
        },
        "knowledge_bonuses": {
            "Energetika": 40, "Texnika va Mexanika": 30, "Meteorologiya": 25
        },
        "item_bonuses": {
            "Portativ benzin generatori (Kichik)": 40, "Shamol o'tkazmaydigan issiq termoko'rpa (4 dona)": 30,
            "Qalin charmdan ishlangan ishchi etiklar (3 juft)": 20
        },
        "special_rules": "Issiqlik va elektr manbai bunkerning yuragi. Energetiklar va ustalar yetakchi o'rinda."
    },
    {
        "type": "volcano",
        "name": "Super vulqon otilishi",
        "emoji": "🔥",
        "description": "Sayyoraning eng yirik supervulqonlari bir vaqtda otilib, atmosferaga millionlab tonna kul va zaharli oltingugurt gazini chiqardi.",
        "duration_years": 7,
        "profession_bonuses": {
            "Geolog": 35, "Kimyogar": 35, "Ekolog": 30, "Quruvchi": 25, "Feldsher": 20
        },
        "health_penalties": {
            "Nafas yo'li kasalliklari": -40, "Chang allergiyasi": -35
        },
        "knowledge_bonuses": {
            "Geologiya": 35, "Kimyo va Toksikologiya": 35, "Gidrologiya": 25
        },
        "item_bonuses": {
            "Gaz niqobi (Professional filtr bilan, 2 dona)": 35, "Suv filtri": 25
        },
        "special_rules": "Havo tozalash tizimlari doimiy nazoratda bo'lishi kerak. Nafas olishi zaif odamlar xavf ostida."
    },
    {
        "type": "ai_takeover",
        "name": "Sun'iy intellekt qo'zg'oloni",
        "emoji": "🤖",
        "description": "Harbiy super-AI nazoratdan chiqdi va insoniyatni yo'q qilish uchun robot armiyalar va dronlarni ishga tushirdi.",
        "duration_years": 6,
        "profession_bonuses": {
            "Dasturchi": 45, "IT mutaxassisi": 40, "Elektrik": 30, "Harbiy": 30, "Razvedkachi": 30
        },
        "health_penalties": {},
        "knowledge_bonuses": {
            "Axborot texnologiyalari (IT)": 45, "Texnika va Mexanika": 30, "Radioaloqa": 25
        },
        "item_bonuses": {
            "Quyoshli batareyada ishlovchi noutbuk (Ensiklopediyalar bilan)": 35, "Qisqa to'lqinli Walkie-Talkie": 25
        },
        "special_rules": "Elektronika va kiber-hujumlarni qaytaruvchi IT mutaxassislari eng asosiy himoyachi."
    },
    {
        "type": "asteroid",
        "name": "Ulkan asteroid urilishi",
        "emoji": "☄️",
        "description": "10 km o'lchamdagi asteroid yerga urilib, ulkan zarba to'lqini, zilzilalar va uzoq muddatli qorong'ulikni keltirib chiqardi.",
        "duration_years": 12,
        "profession_bonuses": {
            "Quruvchi": 35, "Arxitektor": 30, "Geolog": 30, "Shifokor": 25, "Astronom": 20
        },
        "health_penalties": {
            "Nogironlik": -25
        },
        "knowledge_bonuses": {
            "Qurilish va Arxitektura": 35, "Fizika": 25, "Geologiya": 30
        },
        "item_bonuses": {
            "Gidravlik domkrat (10 tonnalik)": 35, "Universal usta to'plami": 25
        },
        "special_rules": "Bunker devorlarining butunligi doimiy xavf ostida. Quruvchi va arxitektorlar kerak."
    },
    {
        "type": "magnetic_flip",
        "name": "Magnit maydon buzilishi",
        "emoji": "🌍",
        "description": "Yerning magnit qutblari o'rnini almashtirdi, atmosfera quyosh radiatsiyasiga qarshi himoyasiz qoldi, barcha sun'iy yo'ldoshlar quladi.",
        "duration_years": 4,
        "profession_bonuses": {
            "Fizik": 35, "Elektrik": 35, "Radioaloqa ustasi": 30, "Meteorolog": 25
        },
        "health_penalties": {},
        "knowledge_bonuses": {
            "Fizika va Radiatsiya": 35, "Energetika": 30
        },
        "item_bonuses": {
            "Radioaloqa asboblari": 30, "Quyosh panellari": 25
        },
        "special_rules": "Yer yuzida har qanday elektronika kuyib ketgan, faqat chuqur yer osti bunkeri xavfsiz."
    },
    {
        "type": "biological",
        "name": "Noma'lum biologik falokat",
        "emoji": "🧪",
        "description": "Genetik modifikatsiyalangan o'simlik va zamburug'lar mutatsiyaga uchrab, havoga odam asab tizimini falajlovchi sporalar tarqatmoqda.",
        "duration_years": 5,
        "profession_bonuses": {
            "Botanik": 40, "Biolog": 35, "Kimyogar": 35, "Shifokor": 30, "Agronom": 25
        },
        "health_penalties": {
            "Allergiya": -35, "Zaif immunitet": -30
        },
        "knowledge_bonuses": {
            "Biologiya va Genetika": 40, "Kimyo": 35, "Qishloq xo'jaligi": 25
        },
        "item_bonuses": {
            "Kimyoviy himoya kombinezoni": 30, "Mikroskop": 25
        },
        "special_rules": "Biolog va botaniklar sporalarga qarshi vaksina va antidot yaratishning yagona umididir."
    },
    {
        "type": "solar_flare",
        "name": "Super quyosh chaqnashi (EMP)",
        "emoji": "☀️",
        "description": "Tarixdagi eng kuchli quyosh chaqnashi sayyoraning barcha elektr transformatorlari va generatorlarini bir zumda yoqib yubordi.",
        "duration_years": 3,
        "profession_bonuses": {
            "Elektrik": 40, "Energetik": 35, "Mexanik": 30, "Temirchi": 25, "Fermer": 25
        },
        "health_penalties": {},
        "knowledge_bonuses": {
            "Energetika": 40, "Texnika va Mexanika": 35
        },
        "item_bonuses": {
            "Taktik fonar (Dinamoli)": 25, "Chaqmoqtosh": 25
        },
        "special_rules": "Mexanik va qo'l mehnati ustalari yuqori qadrlanadi, zamonaviy avtomatika ishlamaydi."
    },
    {
        "type": "climate_collapse",
        "name": "Global iqlim halokati",
        "emoji": "🌪️",
        "description": "Atmosfera sirkulyatsiyasi buzilib, doimiy super-to'fonlar, kislotali yomg'irlar va qum bo'ronlari yer yuzini yashab bo'lmas holga keltirdi.",
        "duration_years": 9,
        "profession_bonuses": {
            "Meteorolog": 35, "Ekolog": 35, "Agronom": 30, "Santexnik": 25, "Quruvchi": 25
        },
        "health_penalties": {
            "Zaif": -20
        },
        "knowledge_bonuses": {
            "Ekologiya": 35, "Qishloq xo'jaligi": 30, "Gidrologiya": 25
        },
        "item_bonuses": {
            "Urug'lar to'plami (Sabzavot va don)": 35, "O'simliklar uchun LED fitolampa": 30
        },
        "special_rules": "Yopiq sharoitda oziq-ovqat va toza havo aylanishini ta'minlash eng muhim vazifa."
    },
    {
        "type": "mega_tsunami",
        "name": "Mega-sunami to'lqinlari",
        "emoji": "🌊",
        "description": "Suv osti plitalarining ulkan yorilishi oqibatida 500 metrlik to'lqinlar barcha qirg'oqbo'yi shaharlarni yo'q qildi.",
        "duration_years": 4,
        "profession_bonuses": {
            "Qutqaruvchi": 35, "Shifokor": 30, "Santexnik": 30, "Gidrogeolog": 30, "Dengizchi": 25
        },
        "health_penalties": {},
        "knowledge_bonuses": {
            "Gidrologiya": 35, "Tibbiyot": 25
        },
        "item_bonuses": {
            "Statik arqon": 25, "Suv filtri": 30
        },
        "special_rules": "Suv bosimi va drenaj tizimlarini nazorat qilish talab etiladi."
    }
]

def get_random_apocalypse() -> Dict[str, Any]:
    return random.choice(APOCALYPSE_SCENARIOS)

def get_apocalypse_by_type(apocalypse_type: str) -> Dict[str, Any]:
    for ap in APOCALYPSE_SCENARIOS:
        if ap["type"] == apocalypse_type:
            return ap
    return APOCALYPSE_SCENARIOS[0]
