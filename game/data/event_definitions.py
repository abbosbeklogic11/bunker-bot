"""
Event definitions data module for BUNKER game.
Contains 25+ dynamic bunker crisis and opportunity events.
"""
from typing import Dict, Any, List
import random

EVENT_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Bunkerda elektr uzildi!",
        "emoji": "⚡",
        "description": "Asosiy generator nosozlikka uchradi. Chiroqlar o'chdi, ventilyatsiya quvvati pasaydi.",
        "required_professions": ["Elektrik", "Energetik", "Muhandis", "Mexanik"],
        "required_knowledge": ["Energetika", "Texnika va Mexanika"],
        "required_items": ["Universal kalitlar va master-otvyortkalar to'plami", "Portativ benzin generatori (Kichik)"],
        "if_resolved_description": "Mutaxassislar generatorni o'z vaqtida sozlashdi. Elektr ta'minoti tiklandi!",
        "if_not_resolved_description": "Elektr tizimi qisman ishdan chiqdi. Bunker elektr energiyasi 30% ga kamaydi.",
        "effect_type": "RESOURCE_LOSS",
        "effect_data": {"power_loss": 30},
        "probability": 0.45,
        "min_round": 2
    },
    {
        "id": 2,
        "name": "Ichki virus infeksiyasi tarqaldi!",
        "emoji": "🦠",
        "description": "Bunker ichida kimdir yo'talib, yuqumli infeksiya alomatlari paydo bo'ldi.",
        "required_professions": ["Shifokor", "Jarroh", "Biolog", "Feldsher"],
        "required_knowledge": ["Tibbiyot", "Biologiya va Genetika"],
        "required_items": ["Antibiotiklar zaxirasi (Keng spektrli, 6 oylik)", "Tibbiy sumka (To'liq to'plam)", "Dezinfeksiya vositasi (5 litr spirt + xlor eritmasi)"],
        "if_resolved_description": "Shifokorlar zudlik bilan karantin joriy etib bemorlarni davolashdi.",
        "if_not_resolved_description": "Epidemiya avj oldi. Eng zaif o'yinchilarning omon qolish ballari pasaydi.",
        "effect_type": "PLAYER_EFFECT",
        "effect_data": {"health_penalty": 20},
        "probability": 0.4,
        "min_round": 2
    },
    {
        "id": 3,
        "name": "Asosiy suv filtri buzildi!",
        "emoji": "💧",
        "description": "Yerosti suvini tozalovchi asosiy membrana qum bilan tiqilib qoldi.",
        "required_professions": ["Santexnik", "Gidrogeolog", "Muhandis", "Suvchi (dalg'ich)"],
        "required_knowledge": ["Gidrologiya va Suv ta'minoti", "Texnika va Mexanika"],
        "required_items": ["Portativ suv filtri (Keramika)", "Yelim va germetik (Suyuq rezina - 5 balon)"],
        "if_resolved_description": "Filtr tozalab o'rnatildi, ichimlik suvi oqimi tiklandi.",
        "if_not_resolved_description": "Suv zaxirasi 40 kunga qisqardi. Kunlik suv me'yori cheklandi.",
        "effect_type": "RESOURCE_LOSS",
        "effect_data": {"water_loss": 40},
        "probability": 0.4,
        "min_round": 2
    },
    {
        "id": 4,
        "name": "Oziq-ovqat omborida mog'or bosdi!",
        "emoji": "🥫",
        "description": "Namlik oshishi natijasida konservalar va quritilgan oziq-ovqat qutilari zararlanish xavfida.",
        "required_professions": ["Oshpaz", "Biolog", "Agronom", "Kimyogar"],
        "required_knowledge": ["Oziq-ovqat texnologiyasi", "Kimyo va Toksikologiya"],
        "required_items": ["Dezinfeksiya vositasi (5 litr spirt + xlor eritmasi)", "Bino ichidagi harorat va namlik o'lchagich (Gigrometr)"],
        "if_resolved_description": "Oziq-ovqat ombori tozalandi va quruq xonaga ko'chirildi.",
        "if_not_resolved_description": "Oziq-ovqat zaxirasining 25% qismi yaroqsiz holga keldi.",
        "effect_type": "RESOURCE_LOSS",
        "effect_data": {"food_loss": 35},
        "probability": 0.35,
        "min_round": 2
    },
    {
        "id": 5,
        "name": "Bunkerda jiddiy nizo va janjal!",
        "emoji": "😡",
        "description": "Resurslar taqsimoti bo'yicha o'yinchilar o'rtasida ziddiyat kelib chiqdi.",
        "required_professions": ["Psixolog", "Psixiatr", "Diplomat", "O'qituvchi", "Yurist"],
        "required_knowledge": ["Psixologiya va Konfliktologiya"],
        "required_items": ["Gitara chalish", "Musiqa"],
        "if_resolved_description": "Psixologik suhbat orqali guruhda tinchlik o'rnatildi.",
        "if_not_resolved_description": "Kelishmovchilik kuchaydi, keyingi ovoz berishda hamma bir-biriga qarshi ovoz beradi.",
        "effect_type": "BOOST",
        "effect_data": {"tension": "HIGH"},
        "probability": 0.35,
        "min_round": 3
    },
    {
        "id": 6,
        "name": "Kichik yong'in chiqdi!",
        "emoji": "🧯",
        "description": "Oshxona simlarining qisqa tutashuvi oqibatida yong'in boshlandi.",
        "required_professions": ["O'tchidir", "Qutqaruvchi", "Elektrik", "Harbiy"],
        "required_knowledge": ["Harbiy taktika va Xavfsizlik", "Texnika va Mexanika"],
        "required_items": ["Yong'in o'chirgich (Uglerod kislotali, 2 dona)", "Gaz niqobi (Professional filtr bilan, 2 dona)"],
        "if_resolved_description": "Yong'in bir necha daqiqada to'liq o'chirildi, hech kim jabrlanmadi.",
        "if_not_resolved_description": "Yong'in oshxona uskunalarini shikastladi. Oziq-ovqat tayyorlash qiyinlashdi.",
        "effect_type": "RESOURCE_LOSS",
        "effect_data": {"food_loss": 20},
        "probability": 0.3,
        "min_round": 2
    },
    {
        "id": 7,
        "name": "Ventilyatsiyadan zaharli havo kirdi!",
        "emoji": "💨",
        "description": "Tashqaridagi bosim o'zgarishi tufayli zaharli moddalar kirish filtrlari tomon kela boshladi.",
        "required_professions": ["Kimyogar", "Ekolog", "Santexnik", "Fizik"],
        "required_knowledge": ["Kimyo va Toksikologiya", "Ekologiya"],
        "required_items": ["Gaz niqobi (Professional filtr bilan, 2 dona)", "Kimyoviy himoya kombinezoni (OZK)"],
        "if_resolved_description": "Zudlik bilan havo klapanlari yopildi va yangi filtrlar ishga tushirildi.",
        "if_not_resolved_description": "Bir necha o'yinchi yengil zaharlanib immunitetini yo'qotdi.",
        "effect_type": "PLAYER_EFFECT",
        "effect_data": {"health_penalty": 15},
        "probability": 0.3,
        "min_round": 3
    },
    {
        "id": 8,
        "name": "Radiodan tashqi signal tutildi!",
        "emoji": "📡",
        "description": "Eski harbiy to'lqinda boshqa bir omon qolganlar guruhi signali qabul qilindi.",
        "required_professions": ["Radioaloqa ustasi", "IT mutaxassisi", "Dasturchi", "Meteorolog"],
        "required_knowledge": ["Radioaloqa va Telekommunikatsiya", "Axborot texnologiyalari (IT)"],
        "required_items": ["Qisqa to'lqinli Walkie-Talkie (Ratsiya jufti)", "Quyoshli batareyada ishlovchi noutbuk"],
        "if_resolved_description": "Aloqa o'rnatildi! Qo'shni bazadan oziq-ovqat va koordinatalar bo'yicha qimmatli ma'lumot olindi.",
        "if_not_resolved_description": "Signal yo'qoldi. Imkoniyat qo'ldan boy berildi.",
        "effect_type": "BOOST",
        "effect_data": {"survival_bonus": 25},
        "probability": 0.4,
        "min_round": 3
    },
    {
        "id": 9,
        "name": "Zaxira ombor xonasi topildi!",
        "emoji": "📦",
        "description": "Eski bunker chizmasidan ilgari noma'lum bo'lgan yopiq zaxira xonasi aniqlandi.",
        "required_professions": ["Arxitektor", "Quruvchi", "Geolog", "Universal usta"],
        "required_knowledge": ["Qurilish va Arxitektura", "Geologiya va Mineralogiya"],
        "required_items": ["Gidravlik domkrat (10 tonnalik)", "Qulflarni ochish (Lockpicking)"],
        "if_resolved_description": "Eshik ochildi! Xonadan 60 kunlik yangi konservalar va dori-darmonlar topildi!",
        "if_not_resolved_description": "Zanglagan og'ir eshikni ochishning iloji bo'lmadi.",
        "effect_type": "BOOST",
        "effect_data": {"food_bonus": 60, "water_bonus": 40},
        "probability": 0.35,
        "min_round": 3
    },
    {
        "id": 10,
        "name": "Bunker eshigi qattiq taqillatildi!",
        "emoji": "🚪",
        "description": "Tashqaridan kimdir qutqaruv so'rab eshikni urmoqda. Bu tuzoq yoki haqiqiy qutqaruvchi bo'lishi mumkin.",
        "required_professions": ["Harbiy", "Razvedkachi", "Psixolog", "Shifokor"],
        "required_knowledge": ["Harbiy taktika va Xavfsizlik", "Psixologiya va Konfliktologiya"],
        "required_items": ["Dozimetr / Radiometr (Raqamli)", "Gaz niqobi (Professional filtr bilan, 2 dona)"],
        "if_resolved_description": "Harbiylar vaziyatni nazorat ostida tekshirishdi va foydali tibbiy buyumlarni qabul qilishdi.",
        "if_not_resolved_description": "Eshik ochilmadi. Hech qanday xavf tug'ilmadi, lekin resurs ham olinmadi.",
        "effect_type": "BOOST",
        "effect_data": {"item_bonus": 1},
        "probability": 0.3,
        "min_round": 4
    },
    {
        "id": 11,
        "name": "Zilzila yer osti siljishini keltirib chiqardi!",
        "emoji": "🌋",
        "description": "Bunker shiftida yoriqlar paydo bo'ldi, tayanch ustunlar kuchli bosim ostida qoldi.",
        "required_professions": ["Quruvchi", "Arxitektor", "Geolog", "Muhandis"],
        "required_knowledge": ["Qurilish va Arxitektura", "Geologiya va Mineralogiya"],
        "required_items": ["Gidravlik domkrat (10 tonnalik)", "Universal kalitlar va master-otvyortkalar to'plami"],
        "if_resolved_description": "Tayanch ustunlar mustahkamlandi, bunker strukturasi saqlab qolindi.",
        "if_not_resolved_description": "Xonalardan biri qulab tushdi. Bunker qulayligi pasaydi.",
        "effect_type": "RESOURCE_LOSS",
        "effect_data": {"capacity_risk": 1},
        "probability": 0.25,
        "min_round": 4
    },
    {
        "id": 12,
        "name": "Suv zaxirasida bakteriyalar aniqlandi!",
        "emoji": "🧫",
        "description": "Suv tahlili laboratoriyasida noma'lum ichak tayoqchasi bakteriyasi topildi.",
        "required_professions": ["Biolog", "Kimyogar", "Shifokor", "Feldsher"],
        "required_knowledge": ["Biologiya va Genetika", "Kimyo va Toksikologiya"],
        "required_items": ["Mikroskop (Portativ laboratoriya linzasi bilan)", "Dezinfeksiya vositasi (5 litr spirt + xlor eritmasi)"],
        "if_resolved_description": "Suv xlorlanib va distillanib to'liq zararsizlantirildi.",
        "if_not_resolved_description": "Barcha o'yinchilarning oshqozoni og'rib quvvatdan qolishdi.",
        "effect_type": "PLAYER_EFFECT",
        "effect_data": {"health_penalty": 15},
        "probability": 0.35,
        "min_round": 3
    },
    {
        "id": 13,
        "name": "Dasturiy xatolik (Kiber-nosozlik)!",
        "emoji": "💻",
        "description": "Bunkerni boshqaruvchi kompyuter tizimida nosozlik yuz berib barcha eshiklar avtomatik yopilib qoldi.",
        "required_professions": ["Dasturchi", "IT mutaxassisi", "Elektrik", "Matematik"],
        "required_knowledge": ["Axborot texnologiyalari (IT)", "Texnika va Mexanika"],
        "required_items": ["Quyoshli batareyada ishlovchi noutbuk (Ensiklopediyalar bilan)"],
        "if_resolved_description": "Dasturchi kodni qayta yukladi va tizimni tikladi.",
        "if_not_resolved_description": "Avtomatika qo'lda boshqaruvga o'tdi, ko'p energiya sarflana boshladi.",
        "effect_type": "RESOURCE_LOSS",
        "effect_data": {"power_loss": 20},
        "probability": 0.3,
        "min_round": 3
    },
    {
        "id": 14,
        "name": "Bunker issiqxonasida mo'l hosil!",
        "emoji": "🍅",
        "description": "O'simliklar o'z vaqtida parvarish qilingani sababli ko'p miqdorda sabzavot hosili yetildi.",
        "required_professions": ["Agronom", "Fermer", "Botanik", "Bog'bon"],
        "required_knowledge": ["Qishloq xo'jaligi", "Biologiya va Genetika"],
        "required_items": ["O'simliklar uchun maxsus LED fitolampa", "Urug'lar to'plami (Sabzavot va don)"],
        "if_resolved_description": "Yangi sabzavotlar yig'ib olindi. Oziq-ovqat zaxirasi 40 kunga uzaytirildi!",
        "if_not_resolved_description": "Hosil yetarli darajada parvarishlanmadi, oddiy hosil olindi.",
        "effect_type": "BOOST",
        "effect_data": {"food_bonus": 40},
        "probability": 0.35,
        "min_round": 3
    },
    {
        "id": 15,
        "name": "Ichki sabotaj shubhasi!",
        "emoji": "🕵️",
        "description": "Suv quvurlaridan birining klapani qasddan bo'shatib qo'yilganligi aniqlandi.",
        "required_professions": ["Detektiv", "Politsiyachi", "Razvedkachi", "Psixolog"],
        "required_knowledge": ["Harbiy taktika va Xavfsizlik", "Psixologiya va Konfliktologiya"],
        "required_items": ["Kuzatuv"],
        "if_resolved_description": "Detektiv tezkor tergov o'tkazib aybdor sabablarini aniqladi va xavfni bartaraf etdi.",
        "if_not_resolved_description": "Guruhda o'zaro ishonchsizlik va shubha maksimal darajaga chiqdi.",
        "effect_type": "BOOST",
        "effect_data": {"tension": "CRITICAL"},
        "probability": 0.3,
        "min_round": 4
    }
]

def get_random_event(current_round: int = 1) -> Dict[str, Any]:
    valid_events = [e for e in EVENT_DEFINITIONS if e.get("min_round", 1) <= current_round]
    if not valid_events:
        valid_events = EVENT_DEFINITIONS
    return random.choice(valid_events)

def get_event_by_id(event_id: int) -> Dict[str, Any]:
    for e in EVENT_DEFINITIONS:
        if e["id"] == event_id:
            return e
    return EVENT_DEFINITIONS[0]
