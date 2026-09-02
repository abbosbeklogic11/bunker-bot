"""
Characters data module for BUNKER game.
Contains 35+ character traits with descriptions and social dynamics.
"""
from typing import Dict, Any, List
import random

CHARACTERS: List[Dict[str, Any]] = [
    {
        "name": "Lider",
        "emoji": "👑",
        "description": "Boshqalarni boshqara oladi, qat'iyatli va javobgarlikni o'z zimmasiga oladi.",
        "social_bonus": 25,
        "ability_affinity": ["Lider", "Diplomat", "Himoyachi"]
    },
    {
        "name": "Sokin",
        "emoji": "🧘",
        "description": "Stressli vaziyatlarda ham sovuqqon va bosiq, guruhda nizolarni pasaytiradi.",
        "social_bonus": 15,
        "ability_affinity": ["Kuzatuvchi", "Psixolog"]
    },
    {
        "name": "Tajovuzkor",
        "emoji": "😤",
        "description": "Tez asabiylashadi, o'z manfaatini qattiq himoya qiladi, boshqalar bilan ziddiyatga kirishi mumkin.",
        "social_bonus": -20,
        "ability_affinity": ["Bloker", "Qasoskor"]
    },
    {
        "name": "Manipulyator",
        "emoji": "🎭",
        "description": "Boshqalarning hissiyotlaridan foydalanib o'z maqsadiga erishadi, yashirin o'yinchi.",
        "social_bonus": -10,
        "ability_affinity": ["Detektiv", "Almashtiruvchi", "Soxtachi"]
    },
    {
        "name": "Optimist",
        "emoji": "🌟",
        "description": "Eng og'ir vaziyatda ham ijobiy kayfiyatni saqlaydi, jamoa ruhini ko'taradi.",
        "social_bonus": 20,
        "ability_affinity": ["Himoyachi", "Tibbiyotchi"]
    },
    {
        "name": "Pessimist",
        "emoji": "🌧️",
        "description": "Hamma narsaning yomon tomonini ko'radi, ammo xavflarni oldindan sezadi.",
        "social_bonus": -5,
        "ability_affinity": ["Tekshiruvchi", "Ehtiyotkor"]
    },
    {
        "name": "Jamoaviy",
        "emoji": "🤝",
        "description": "O'zidan ko'ra jamoa manfaatini ustun qo'yadi, ishonchli o'rtoq.",
        "social_bonus": 30,
        "ability_affinity": ["Himoyachi", "Diplomat"]
    },
    {
        "name": "Egoist",
        "emoji": "🤑",
        "description": "Faqat o'z omon qolishini o'ylaydi, zarur bo'lsa boshqalarni qurbon qiladi.",
        "social_bonus": -25,
        "ability_affinity": ["Riskchi", "Qutqaruvchi"]
    },
    {
        "name": "Halol",
        "emoji": "⚖️",
        "description": "Hech qachon aldamaydi, adolat tarafdori, lekin hiylakorlarga oson aldanadi.",
        "social_bonus": 25,
        "ability_affinity": ["Diplomat", "Sudya"]
    },
    {
        "name": "Yolg'onchi",
        "emoji": "🤥",
        "description": "Mohirlik bilan aldaydi, o'z xususiyatlarini yashirishga usta.",
        "social_bonus": -15,
        "ability_affinity": ["Manipulyator", "Soxtachi"]
    },
    {
        "name": "Strateg",
        "emoji": "♟️",
        "description": "Har bir harakatni 5 qadam oldindan hisoblaydi, o'yin taktikasini boshqaradi.",
        "social_bonus": 20,
        "ability_affinity": ["Detektiv", "Lider", "Tahlilchi"]
    },
    {
        "name": "Qo'rqoq",
        "emoji": "😨",
        "description": "Xavf paytida vahimaga tushadi, ko'pchilik ketidan ergashadi.",
        "social_bonus": -15,
        "ability_affinity": ["Himoyalanuvchi"]
    },
    {
        "name": "Jasur",
        "emoji": "🦁",
        "description": "Xavf-xatarga to'g'ri qaraydi, jamoani himoya qilish uchun o'zini xavfga qo'yadi.",
        "social_bonus": 25,
        "ability_affinity": ["Himoyachi", "Qutqaruvchi"]
    },
    {
        "name": "Shubhali",
        "emoji": "🧐",
        "description": "Hech kimga ishonmaydi, har bir ma'lumotni qayta tekshirishni xohlaydi.",
        "social_bonus": -5,
        "ability_affinity": ["Tekshiruvchi", "Detektiv"]
    },
    {
        "name": "Ishonuvchan",
        "emoji": "🥺",
        "description": "Hamma odamlarni yaxshi deb o'ylaydi, manipulyatsiyaga tez tushadi.",
        "social_bonus": 10,
        "ability_affinity": ["Hamkor"]
    },
    {
        "name": "Mehribon",
        "emoji": "❤️",
        "description": "Boshqalarning dardiga sherik bo'ladi, muhtojlarga yordam berishga tayyor.",
        "social_bonus": 25,
        "ability_affinity": ["Shifokor", "Himoyachi"]
    },
    {
        "name": "Zukko",
        "emoji": "💡",
        "description": "Murakkab muammolarga tezda nostandart yechim topa oladi.",
        "social_bonus": 20,
        "ability_affinity": ["Tahlilchi", "Ixtirochi"]
    },
    {
        "name": "Hissiyotli",
        "emoji": "😭",
        "description": "Tuyg'ular bilan harakat qiladi, hissiy qarorlar qabul qiladi.",
        "social_bonus": 0,
        "ability_affinity": ["Diplomat"]
    },
    {
        "name": "Sovuqqon",
        "emoji": "🧊",
        "description": "Tuyg'ularni bir chetga surib faqat quruq mantiq bilan hisob-kitob qiladi.",
        "social_bonus": 10,
        "ability_affinity": ["Strateg", "Bloker"]
    },
    {
        "name": "Gapdon",
        "emoji": "🗣️",
        "description": "O'z nutqi bilan istalgan odamni ishontira oladi, bahslarda yengilmas.",
        "social_bonus": 20,
        "ability_affinity": ["Diplomat", "Lider"]
    },
    {
        "name": "Kamgap",
        "emoji": "🤐",
        "description": "Kam gapiradi, faqat ish qiladi, keraksiz bahslarga kirmaydi.",
        "social_bonus": 5,
        "ability_affinity": ["Kuzatuvchi"]
    },
    {
        "name": "Hazilkash",
        "emoji": "😄",
        "description": "Og'ir vaziyatda ham hazil qilib kayfiyatni ko'taradi, ammo ba'zida noo'rin hazil qilishi mumkin.",
        "social_bonus": 15,
        "ability_affinity": ["Riskchi"]
    },
    {
        "name": "Jiddiy",
        "emoji": "😐",
        "description": "Har bir qoidaga qat'iy rioya qiladi, intizom talab qiladi.",
        "social_bonus": 10,
        "ability_affinity": ["Bloker", "Lider"]
    },
    {
        "name": "Qayshar",
        "emoji": "🦬",
        "description": "O'z fikridan aslo qaytmaydi, o'jarlik bilan o'z pozitsiyasini himoya qiladi.",
        "social_bonus": -10,
        "ability_affinity": ["Himoyachi"]
    },
    {
        "name": "Moslashuvchan",
        "emoji": "🦎",
        "description": "Har qanday vaziyatga va har qanday odamga tezda moslashadi.",
        "social_bonus": 20,
        "ability_affinity": ["Almashtiruvchi", "Riskchi"]
    },
    {
        "name": "Qo'rqmas",
        "emoji": "🦾",
        "description": "O'lim va xavfdan qo'rqmaydi, bunkerning eng og'ir ishlariga boradi.",
        "social_bonus": 20,
        "ability_affinity": ["Himoyachi"]
    },
    {
        "name": "Ehtiyotkor",
        "emoji": "🛡️",
        "description": "Yetti o'lchab bir kesadi, xavfli takliflarni darhol rad etadi.",
        "social_bonus": 15,
        "ability_affinity": ["Tekshiruvchi", "Himoyachi"]
    },
    {
        "name": "Intizomli",
        "emoji": "📐",
        "description": "Resurslarni tejash va qat'iy jadval asosida yashash tarafdori.",
        "social_bonus": 15,
        "ability_affinity": ["Lider"]
    },
    {
        "name": "Erkin ruhli",
        "emoji": "🕊️",
        "description": "Cheklovlarga toqat qilolmaydi, mustaqil fikrlaydi.",
        "social_bonus": 5,
        "ability_affinity": ["Riskchi"]
    },
    {
        "name": "Buyruqsevar",
        "emoji": "📣",
        "description": "Hammaga buyruq berishni yaxshi ko'radi, itoatkorlik talab qiladi.",
        "social_bonus": -15,
        "ability_affinity": ["Bloker", "Lider"]
    },
    {
        "name": "Kamtarin",
        "emoji": "🌱",
        "description": "O'z yutuqlarini ko'z-ko'z qilmaydi, xolis va sokin ishlaydi.",
        "social_bonus": 15,
        "ability_affinity": ["Kuzatuvchi"]
    },
    {
        "name": "Faylasuf",
        "emoji": "📜",
        "description": "Hayotning ma'nosi va axloq haqida ko'p o'ylaydi, qarorlari chuqur mantiqqa asoslangan.",
        "social_bonus": 10,
        "ability_affinity": ["Diplomat"]
    },
    {
        "name": "Romantik",
        "emoji": "🌹",
        "description": "Insoniylik va muhabbatga ishonadi, shafqatsiz qarorlarni qabul qilolmaydi.",
        "social_bonus": 5,
        "ability_affinity": ["Himoyachi"]
    },
    {
        "name": "Pragmatik",
        "emoji": "📊",
        "description": "Faqat aniq natija va amaliy foydani hisoblaydi, quruq gaplarni yoqtirmaydi.",
        "social_bonus": 20,
        "ability_affinity": ["Strateg", "Detektiv"]
    },
    {
        "name": "Raqobatchi",
        "emoji": "🏆",
        "description": "Har narsada birinchi bo'lishni xohlaydi, yutqazishni yoqtirmaydi.",
        "social_bonus": 0,
        "ability_affinity": ["Lider", "Riskchi"]
    }
]

def get_random_character() -> Dict[str, Any]:
    return random.choice(CHARACTERS)

def get_character_by_name(name: str) -> Dict[str, Any]:
    for char in CHARACTERS:
        if char["name"].lower() == name.lower():
            return char
    return CHARACTERS[0]
