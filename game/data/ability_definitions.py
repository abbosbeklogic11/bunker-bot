"""
Ability definitions data module for BUNKER game.
Contains 20+ specialized player abilities with clear triggers, targets, and profession affinities.
"""
from typing import Dict, Any, List
import random

ABILITY_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Shifokor (Davolash)",
        "emoji": "🩺",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 90,
        "uses_per_game": 1,
        "effect_type": "HEAL",
        "target": "ANY_ALIVE",
        "profession_affinity": ["Shifokor", "Jarroh", "Feldsher", "Pediatr"],
        "description": "Bir o'yinchini joriy raundda ovoz berish orqali chiqarilishdan to'liq himoya qila oladi.",
        "description_private": "O'zingizni yoki ittifoqdoshingizni o'limdan saqlab qoluvchi tibbiy himoya."
    },
    {
        "id": 2,
        "name": "Detektiv (Tergov)",
        "emoji": "🕵️",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 80,
        "uses_per_game": 2,
        "effect_type": "DETECT",
        "target": "ANY_PLAYER",
        "profession_affinity": ["Politsiyachi", "Razvedkachi", "Yurist", "Jurnalist"],
        "description": "Tanlangan o'yinchining yashirin xususiyatlaridan bittasini tekshiradi va sizga ochib beradi.",
        "description_private": "Raqibning eng maxfiy kartasini fosh qilasiz."
    },
    {
        "id": 3,
        "name": "Lider (Yetakchi ovozi)",
        "emoji": "👑",
        "ability_type": "ACTIVE",
        "trigger": "ON_VOTE",
        "power": 85,
        "uses_per_game": 1,
        "effect_type": "DOUBLE_VOTE",
        "target": "SELF",
        "profession_affinity": ["Harbiy", "Direktor", "Arxitektor", "O'qituvchi"],
        "description": "Bir marta o'z ovozini 2 ta ovoz sifatida hisoblatadi.",
        "description_private": "Ovoz berishda o'zingiz xohlagan nomzodni chiqarish uchun ikki barobar kuch."
    },
    {
        "id": 4,
        "name": "Diplomat (Sulh)",
        "emoji": "🗣️",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 85,
        "uses_per_game": 1,
        "effect_type": "CANCEL_VOTE",
        "target": "NONE",
        "profession_affinity": ["Diplomat", "Yurist", "Psixolog", "Sotuvchi"],
        "description": "Joriy raunddagi ovoz berishni bir marta to'xtatib, barchani omon saqlab qoladi.",
        "description_private": "Barcha o'yinchilar hayotini bitta raundga saqlab qoluvchi diplomatik sulh."
    },
    {
        "id": 5,
        "name": "Tekshiruvchi (Inspeksiya)",
        "emoji": "🔍",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 70,
        "uses_per_game": 2,
        "effect_type": "RANDOM_REVEAL",
        "target": "NONE",
        "profession_affinity": ["Buxgalter", "Tahlilchi", "Inspektor", "Olim"],
        "description": "Tasodifiy bitta o'yinchining hali ochilmagan xususiyatini guruh oldida fosh qiladi.",
        "description_private": "Guruhga yangi faktlar olib kirasiz."
    },
    {
        "id": 6,
        "name": "Himoyachi (Qo'riqchi)",
        "emoji": "🛡️",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 80,
        "uses_per_game": 1,
        "effect_type": "PROTECT",
        "target": "ANY_ALIVE",
        "profession_affinity": ["Harbiy", "Sapyor", "Qutqaruvchi", "Sportchi"],
        "description": "Tanlangan o'yinchiga keyingi chiqarilishdan himoya beradi.",
        "description_private": "Ittifoqchingizga xavfsizlik kafolati berasiz."
    },
    {
        "id": 7,
        "name": "Riskchi (Tavakkal)",
        "emoji": "🎲",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 75,
        "uses_per_game": 1,
        "effect_type": "RANDOM_ABILITY",
        "target": "SELF",
        "profession_affinity": ["Savdogar", "Pilot", "Alpinist", "Dasturchi"],
        "description": "Bazada mavjud qobiliyatlardan butunlay tasodifiy yangi kuchli qobiliyat oladi.",
        "description_private": "Omadingizni sinab kutilmagan qobiliyatga ega bo'lasiz."
    },
    {
        "id": 8,
        "name": "Almashtiruvchi (Barter)",
        "emoji": "🔄",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 85,
        "uses_per_game": 1,
        "effect_type": "SWAP_ATTRIBUTE",
        "target": "ANY_PLAYER",
        "profession_affinity": ["Savdogar", "Diplomat", "Hunarmand"],
        "description": "O'zining bitta xususiyatini boshqa o'yinchi xususiyati bilan almashtiradi.",
        "description_private": "Yaxshi xususiyatni o'zingizga o'zlashtirib, zaif xususiyatingizni unga berasiz."
    },
    {
        "id": 9,
        "name": "Bloker (To'siq)",
        "emoji": "🔒",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 70,
        "uses_per_game": 2,
        "effect_type": "BLOCK",
        "target": "ANY_PLAYER",
        "profession_affinity": ["Politsiyachi", "Psixiatr", "IT mutaxassisi"],
        "description": "Boshqa o'yinchining qobiliyatini bir raundga bloklaydi.",
        "description_private": "Xavfli raqibni qobiliyatsiz qoldirasiz."
    },
    {
        "id": 10,
        "name": "Kuzatuvchi (Ko'z)",
        "emoji": "👁️",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 65,
        "uses_per_game": 2,
        "effect_type": "OBSERVE",
        "target": "NONE",
        "profession_affinity": ["Psixolog", "Kamera operatori", "Kuzatuvchi"],
        "description": "Bu raundda kimlar qobiliyat ishlatganini maxfiy ravishda bilib oladi.",
        "description_private": "Parda ortidagi barcha harakatlarni ko'rasiz."
    },
    {
        "id": 11,
        "name": "Muhandis (Texnik ta'mir)",
        "emoji": "🔧",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 80,
        "uses_per_game": 2,
        "effect_type": "RESOLVE_EVENT",
        "target": "NONE",
        "profession_affinity": ["Muhandis", "Mexanik", "Elektrik", "Santexnik"],
        "description": "Bunkerdagi har qanday texnik nosozlikni avtomatik bartaraf etadi va resursni tejaydi.",
        "description_private": "Bunker barqarorligini ta'minlab o'z obro'yingizni oshirasiz."
    },
    {
        "id": 12,
        "name": "Psixolog (Kayfiyat nazorati)",
        "emoji": "🧠",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 75,
        "uses_per_game": 1,
        "effect_type": "CALM_GROUP",
        "target": "NONE",
        "profession_affinity": ["Psixolog", "Psixiatr", "O'qituvchi"],
        "description": "Guruhdagi agressiyani pasaytiradi va duel raundlarini bekor qilishi mumkin.",
        "description_private": "Guruh nizolarini to'xtatasiz."
    },
    {
        "id": 13,
        "name": "Agronom (Hosildorlik)",
        "emoji": "🌾",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 70,
        "uses_per_game": 1,
        "effect_type": "BOOST_FOOD",
        "target": "NONE",
        "profession_affinity": ["Agronom", "Fermer", "Biolog", "Botanik"],
        "description": "Bunker oziq-ovqat zaxirasini 50 kunga ko'paytiradi.",
        "description_private": "Bunkerni uzoq muddat oziq-ovqat bilan ta'minlaysiz."
    },
    {
        "id": 14,
        "name": "Radiotexnik (Aloqa)",
        "emoji": "📡",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 75,
        "uses_per_game": 1,
        "effect_type": "OUTSIDE_CONTACT",
        "target": "NONE",
        "profession_affinity": ["Radio mutaxassisi", "IT mutaxassisi", "Meteorolog"],
        "description": "Tashqi dunyodan qutqaruv signali oladi va guruhga foydali ma'lumot beradi.",
        "description_private": "Tashqaridagi vaziyat bo'yicha ma'lumotga ega bo'lasiz."
    },
    {
        "id": 15,
        "name": "Energetik (Zaryad)",
        "emoji": "⚡",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 85,
        "uses_per_game": 1,
        "effect_type": "BOOST_POWER",
        "target": "NONE",
        "profession_affinity": ["Energetik", "Elektrik", "Fizik"],
        "description": "Bunker elektr energiyasini to'liq quvvatlantiradi, elektr uzilishlarini bartaraf etadi.",
        "description_private": "Bunkerni yorug'lik va energiya bilan ta'minlaysiz."
    },
    {
        "id": 16,
        "name": "Provokator (Shubha)",
        "emoji": "😈",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 70,
        "uses_per_game": 1,
        "effect_type": "FORCE_VOTE_TARGET",
        "target": "ANY_PLAYER",
        "profession_affinity": ["Jurnalist", "Yolg'onchi", "Manipulyator"],
        "description": "Tanlangan o'yinchiga nisbatan sun'iy shubha uyg'otib, unga qo'shimcha 1 ta ovoz yuklaydi.",
        "description_private": "Raqibingizga qarshi ovoz yukini oshirasiz."
    },
    {
        "id": 17,
        "name": "Mutaxassis (Ekstra bilim)",
        "emoji": "🎓",
        "ability_type": "PASSIVE",
        "trigger": "ON_EVENT",
        "power": 80,
        "uses_per_game": 1,
        "effect_type": "AUTO_RESOLVE_KNOWLEDGE",
        "target": "SELF",
        "profession_affinity": ["Olim", "Fizik", "Kimyogar", "Biolog", "Matematik"],
        "description": "O'z sohasidagi barcha kutilmagan eventlarni avtomatik ravishda hal qiladi.",
        "description_private": "Ilmiy eventlarda mutlaq ustunlik."
    },
    {
        "id": 18,
        "name": "Fidoyi (Qurbonlik)",
        "emoji": "❤️‍🔥",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 90,
        "uses_per_game": 1,
        "effect_type": "SACRIFICE_SAVE",
        "target": "ANY_PLAYER",
        "profession_affinity": ["Harbiy", "Qutqaruvchi", "O'tchidir"],
        "description": "Chiqarilayotgan o'yinchining o'rniga o'zini qurbon qiladi yoki uni qutqaradi.",
        "description_private": "Boshqa o'yinchini saqlab qolish imkoniyati."
    },
    {
        "id": 19,
        "name": "Sudya (Hal qiluvchi ovoz)",
        "emoji": "⚖️",
        "ability_type": "ACTIVE",
        "trigger": "ON_VOTE",
        "power": 85,
        "uses_per_game": 1,
        "effect_type": "BREAK_TIE",
        "target": "NONE",
        "profession_affinity": ["Yurist", "Sudya", "Advokat"],
        "description": "Durang yuz berganda kim chiqishini yakka o'zi hal qilish huquqiga ega bo'ladi.",
        "description_private": "Durang holatida hakamlik qilasiz."
    },
    {
        "id": 20,
        "name": "Soxtachi (Niqob)",
        "emoji": "🎭",
        "ability_type": "ACTIVE",
        "trigger": "MANUAL",
        "power": 75,
        "uses_per_game": 1,
        "effect_type": "FAKE_PROFILE",
        "target": "SELF",
        "profession_affinity": ["Aktyor", "Razvedkachi", "Manipulyator"],
        "description": "O'zining bitta xususiyatini tekshiruvchilarga soxta yaxshi ko'rinishda ko'rsatadi.",
        "description_private": "Detektiv va tekshiruvchilarni aldash imkoni."
    }
]

def get_random_ability() -> Dict[str, Any]:
    return random.choice(ABILITY_DEFINITIONS)

def get_ability_by_id(ability_id: int) -> Dict[str, Any]:
    for a in ABILITY_DEFINITIONS:
        if a["id"] == ability_id:
            return a
    return ABILITY_DEFINITIONS[0]
