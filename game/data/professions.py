"""
Professions data module for the BUNKER game.

Contains all profession definitions and helper functions for
selecting and filtering professions based on apocalypse scenarios.
"""

from __future__ import annotations

import random
from typing import Any

PROFESSIONS: list[dict[str, Any]] = [
    {
        "name": "Shifokor",
        "emoji": "🏥",
        "value_score": 95,
        "skills": ["Kasalliklarni davolash", "Jarrohlik yordami", "Dori-darmon bilimi", "Birinchi yordam"],
        "apocalypse_bonus": {"virus": 40, "nuclear": 20, "biological": 45, "flood": 15, "ice_age": 15, "volcano": 20},
    },
    {
        "name": "Jarroh",
        "emoji": "🔪",
        "value_score": 93,
        "skills": ["Murakkab jarrohlik", "Qon tuxtatish", "Anesteziya", "Yuqori aniqlik"],
        "apocalypse_bonus": {"virus": 35, "nuclear": 25, "biological": 40, "flood": 20, "ice_age": 20, "volcano": 25},
    },
    {
        "name": "Feldsher",
        "emoji": "💊",
        "value_score": 80,
        "skills": ["Tibbiy yordam", "Diagnostika", "Dori berish", "Yaralarni boglash"],
        "apocalypse_bonus": {"virus": 30, "nuclear": 15, "biological": 35, "flood": 15, "ice_age": 10, "volcano": 15},
    },
    {
        "name": "Pediatr",
        "emoji": "👶",
        "value_score": 78,
        "skills": ["Bolalar salomatligi", "Vaksinatsiya", "Bolalar psixologiyasi", "Ovqatlanish nazorati"],
        "apocalypse_bonus": {"virus": 28, "nuclear": 12, "biological": 30, "flood": 10, "ice_age": 10, "volcano": 10},
    },
    {
        "name": "Psixiatr",
        "emoji": "🧠",
        "value_score": 82,
        "skills": ["Ruhiy kasalliklarni davolash", "Psixologik qollab-quvvatlash", "Konflikt hal qilish", "Sedatsiya"],
        "apocalypse_bonus": {"virus": 20, "nuclear": 30, "biological": 25, "flood": 25, "ice_age": 30, "ai": 35},
    },
    {
        "name": "Stomatolog",
        "emoji": "🦷",
        "value_score": 65,
        "skills": ["Tish davolash", "Ogrik qoldirish", "Jarrohlik konikmalari", "Dezinfeksiya"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 10, "biological": 20, "flood": 5, "ice_age": 10, "volcano": 10},
    },
    {
        "name": "Muhandis",
        "emoji": "⚙️",
        "value_score": 90,
        "skills": ["Qurilish loyihalashtirish", "Mexanik tizimlar", "Hisob-kitob", "Texnik muammolarni hal qilish"],
        "apocalypse_bonus": {"virus": 20, "nuclear": 35, "biological": 15, "flood": 40, "ice_age": 30, "volcano": 35},
    },
    {
        "name": "Elektrik",
        "emoji": "⚡",
        "value_score": 88,
        "skills": ["Elektr tarmoqlarini tuzish", "Generator xizmati", "Solar panel ornatish", "Elektr tamirlash"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 30, "biological": 15, "flood": 35, "ice_age": 40, "solar_flare": 50},
    },
    {
        "name": "Mexanik",
        "emoji": "🔧",
        "value_score": 85,
        "skills": ["Mashina tamirlash", "Mexanizm qurish", "Metal ishlash", "Dvigatel xizmati"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 25, "biological": 10, "flood": 30, "ice_age": 25, "volcano": 20},
    },
    {
        "name": "Dasturchi",
        "emoji": "💻",
        "value_score": 72,
        "skills": ["Dasturlash", "Tizim boshqaruvi", "Malumotlar xavfsizligi", "Avtomatlashtirish"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "ai": 50, "solar_flare": 20, "flood": 5, "ice_age": 10},
    },
    {
        "name": "IT mutaxassisi",
        "emoji": "🖥️",
        "value_score": 70,
        "skills": ["Tarmoq sozlash", "Uskunalar tamirlash", "Malumotlar saqlash", "Kiberxavfsizlik"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "ai": 45, "solar_flare": 25, "flood": 5, "ice_age": 10},
    },
    {
        "name": "Fermer",
        "emoji": "🌾",
        "value_score": 92,
        "skills": ["Ekinlarni parvarish", "Tuproq bilimi", "Hayvonchilik", "Urug saqlash"],
        "apocalypse_bonus": {"virus": 30, "nuclear": 20, "biological": 15, "flood": 10, "ice_age": 25, "volcano": 20},
    },
    {
        "name": "Agronom",
        "emoji": "🌱",
        "value_score": 88,
        "skills": ["Osimlik kasalliklari", "Tuproq tahlili", "Hosildorlik oshirish", "Organik dehqonchilik"],
        "apocalypse_bonus": {"virus": 25, "nuclear": 25, "biological": 20, "flood": 15, "ice_age": 30, "volcano": 25},
    },
    {
        "name": "Ovchi",
        "emoji": "🏹",
        "value_score": 80,
        "skills": ["Ovlash", "Hayvon izlash", "Moljal olish", "Teri tayyorlash"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 20, "biological": 10, "flood": 30, "ice_age": 35, "volcano": 25},
    },
    {
        "name": "Baliqchi",
        "emoji": "🎣",
        "value_score": 75,
        "skills": ["Baliq ovlash", "Suv havzalarini organish", "Baliq saqlash", "Tor toqish"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 15, "biological": 10, "flood": 40, "tsunami": 35, "ice_age": 20},
    },
    {
        "name": "Harbiy",
        "emoji": "🪖",
        "value_score": 83,
        "skills": ["Taktik fikrlash", "Jang texnikasi", "Guruh boshqarish", "Chegara himoyasi"],
        "apocalypse_bonus": {"virus": 20, "nuclear": 35, "biological": 20, "flood": 25, "ice_age": 30, "ai": 30},
    },
    {
        "name": "Razvedkachi",
        "emoji": "🕵️",
        "value_score": 80,
        "skills": ["Yashirin harakatlanish", "Malumot toplash", "Kodlash", "Kuzatuv"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 30, "biological": 20, "flood": 15, "ai": 40, "ice_age": 20},
    },
    {
        "name": "Sapyor",
        "emoji": "💣",
        "value_score": 77,
        "skills": ["Portlovchi moddalar", "Mina aniqlash", "Xavfli joy tozalash", "Qurilish portlatish"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 30, "biological": 5, "flood": 20, "asteroid": 35, "volcano": 15},
    },
    {
        "name": "Oshpaz",
        "emoji": "👨‍🍳",
        "value_score": 85,
        "skills": ["Oziq-ovqat tayyorlash", "Mahsulot saqlash", "Oziqlanish bilimi", "Zaxira boshqarish"],
        "apocalypse_bonus": {"virus": 20, "nuclear": 20, "biological": 15, "flood": 20, "ice_age": 25, "volcano": 20},
    },
    {
        "name": "Non yopuvchi",
        "emoji": "🍞",
        "value_score": 78,
        "skills": ["Don mahsulotlari", "Xamirturush ekish", "Oziq-ovqat saqlash", "Kaloriyli ovqat tayyorlash"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 15, "biological": 10, "flood": 15, "ice_age": 20, "volcano": 15},
    },
    {
        "name": "Oquvchi",
        "emoji": "📚",
        "value_score": 70,
        "skills": ["Bilim uzatish", "Bolalarni oqitish", "Tartib ornatish", "Psixologik qollab-quvvatlash"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "biological": 10, "flood": 10, "ice_age": 15, "ai": 20},
    },
    {
        "name": "Psixolog",
        "emoji": "🧘",
        "value_score": 75,
        "skills": ["Stress boshqarish", "Jamoa ruhiyatini mustahkamlash", "Mojarolarni hal qilish", "Terapiya"],
        "apocalypse_bonus": {"virus": 20, "nuclear": 25, "biological": 20, "flood": 25, "ice_age": 30, "ai": 30},
    },
    {
        "name": "Kimyogar",
        "emoji": "⚗️",
        "value_score": 87,
        "skills": ["Kimyoviy tahlil", "Dori sintezi", "Zaharli moddalar bilan ishlash", "Tozalash jarayonlari"],
        "apocalypse_bonus": {"virus": 35, "nuclear": 30, "biological": 40, "flood": 15, "volcano": 25, "chemical": 50},
    },
    {
        "name": "Biolog",
        "emoji": "🔬",
        "value_score": 85,
        "skills": ["Biologik tahlil", "Mikroorganizmlar", "Genetika", "Ekosistemalar"],
        "apocalypse_bonus": {"virus": 40, "nuclear": 20, "biological": 45, "flood": 20, "ice_age": 25, "volcano": 20},
    },
    {
        "name": "Botanik",
        "emoji": "🌿",
        "value_score": 82,
        "skills": ["Osimliklar bilimi", "Dorivor otlar", "Ovqatlik osimliklar", "Gidroponika"],
        "apocalypse_bonus": {"virus": 25, "nuclear": 20, "biological": 20, "flood": 20, "ice_age": 30, "volcano": 25},
    },
    {
        "name": "Geolog",
        "emoji": "🪨",
        "value_score": 78,
        "skills": ["Yer tuzilishini organish", "Qazilma boyliklar", "Suv manbalarini topish", "Vulqon tahlili"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 20, "biological": 5, "flood": 25, "volcano": 40, "asteroid": 30},
    },
    {
        "name": "Gidrogeolog",
        "emoji": "💧",
        "value_score": 83,
        "skills": ["Yer osti suvlari", "Quduq qazish", "Suv sifatini tekshirish", "Suv taminoti"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 25, "biological": 20, "flood": 35, "ice_age": 30, "tsunami": 20},
    },
    {
        "name": "Arxitektor",
        "emoji": "📐",
        "value_score": 80,
        "skills": ["Bino loyihalashtirish", "Binoni mustahkamlash", "Makon rejalashtirish", "Qurilish menorlari"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 30, "biological": 10, "flood": 35, "ice_age": 25, "volcano": 30},
    },
    {
        "name": "Quruvchi",
        "emoji": "🏗️",
        "value_score": 83,
        "skills": ["Qurilish ishlari", "Beton quyish", "Metal konstruksiya", "Tamirlash"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 30, "biological": 10, "flood": 40, "ice_age": 25, "volcano": 30},
    },
    {
        "name": "Santexnik",
        "emoji": "🚿",
        "value_score": 82,
        "skills": ["Suv quvurlarini tamirlash", "Kanalizatsiya", "Suv filtrlash tizimlari", "Sanitariya"],
        "apocalypse_bonus": {"virus": 25, "nuclear": 20, "biological": 25, "flood": 30, "ice_age": 20, "tsunami": 25},
    },
    {
        "name": "Energetik",
        "emoji": "🔋",
        "value_score": 85,
        "skills": ["Energiya tizimlari", "Alternativ energiya", "Energiya tejash", "Generator boshqarish"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 30, "biological": 10, "flood": 25, "ice_age": 35, "solar_flare": 50},
    },
    {
        "name": "Qutqaruvchi",
        "emoji": "🚑",
        "value_score": 84,
        "skills": ["Favqulodda qutqarish", "Birinchi yordam", "Evakuatsiya", "Jismoniy kuch"],
        "apocalypse_bonus": {"virus": 20, "nuclear": 25, "biological": 20, "flood": 40, "ice_age": 25, "volcano": 35},
    },
    {
        "name": "Otchidir",
        "emoji": "🧯",
        "value_score": 76,
        "skills": ["Yongni ochirish", "Himoya uskunalari", "Evakuatsiya yollari", "Havfli moddalar"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 20, "biological": 15, "flood": 15, "volcano": 40, "chemical": 30},
    },
    {
        "name": "Haydovchi",
        "emoji": "🚗",
        "value_score": 65,
        "skills": ["Transport boshqarish", "Yol haritasi", "Mashina tamirlash", "Yukni tashish"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "biological": 10, "flood": 15, "ice_age": 15, "volcano": 20},
    },
    {
        "name": "Pilot",
        "emoji": "✈️",
        "value_score": 72,
        "skills": ["Uchish texnikasi", "Navigatsiya", "Meteorologiya bilimi", "Tizimli fikrlash"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 20, "biological": 10, "flood": 25, "ice_age": 15, "asteroid": 20},
    },
    {
        "name": "Dengizchi",
        "emoji": "⚓",
        "value_score": 74,
        "skills": ["Kemani boshqarish", "Navigatsiya", "Baliq ovlash", "Suv ostida ishlash"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "biological": 10, "flood": 45, "tsunami": 40, "ice_age": 20},
    },
    {
        "name": "Veterinar",
        "emoji": "🐕",
        "value_score": 76,
        "skills": ["Hayvon davolash", "Zoonotik kasalliklar", "Chorvachilik", "Dori bilimi"],
        "apocalypse_bonus": {"virus": 30, "nuclear": 15, "biological": 35, "flood": 15, "ice_age": 20, "volcano": 15},
    },
    {
        "name": "Zoolog",
        "emoji": "🦁",
        "value_score": 70,
        "skills": ["Hayvonlar bilimi", "Ovlash strategiyasi", "Hayvonlardan foydalanish", "Ekosistema"],
        "apocalypse_bonus": {"virus": 20, "nuclear": 10, "biological": 25, "flood": 20, "ice_age": 25, "volcano": 10},
    },
    {
        "name": "Ekolog",
        "emoji": "🌍",
        "value_score": 73,
        "skills": ["Atrof-muhit tahlili", "Zaharli moddalar", "Ekosistema tiklanishi", "Suv sifati"],
        "apocalypse_bonus": {"virus": 20, "nuclear": 35, "biological": 25, "flood": 20, "ice_age": 20, "volcano": 20},
    },
    {
        "name": "Meteorolog",
        "emoji": "🌦️",
        "value_score": 74,
        "skills": ["Ob-havo bashorati", "Iqlim tahlili", "Tabiat hodisalari", "Atmosfera fizikasi"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "biological": 10, "flood": 30, "ice_age": 40, "volcano": 35},
    },
    {
        "name": "Fizik",
        "emoji": "⚛️",
        "value_score": 78,
        "skills": ["Fizik tahlil", "Yadroviy fizika", "Energiya tizimlari", "Ilmiy fikrlash"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 45, "biological": 10, "flood": 15, "asteroid": 30, "solar_flare": 30},
    },
    {
        "name": "Matematik",
        "emoji": "🔢",
        "value_score": 72,
        "skills": ["Hisob-kitob", "Resurs rejalashtirish", "Kriptografiya", "Tizimli tahlil"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "biological": 10, "flood": 15, "ai": 40, "asteroid": 20},
    },
    {
        "name": "Jurnalist",
        "emoji": "📰",
        "value_score": 58,
        "skills": ["Axborot yigish", "Muloqot", "Psixologik tasir", "Tarix yozish"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 10, "biological": 10, "flood": 10, "ice_age": 10, "ai": 15},
    },
    {
        "name": "Adib",
        "emoji": "✍️",
        "value_score": 55,
        "skills": ["Yozuvchilik", "Tarix saqlash", "Ijodiy fikrlash", "Muloqot"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 10, "biological": 5, "flood": 5, "ice_age": 10, "ai": 15},
    },
    {
        "name": "Rassam",
        "emoji": "🎨",
        "value_score": 52,
        "skills": ["Ijodiy fikrlash", "Xarita chizish", "Ranglar bilimi", "Jamoa ruhini kotarish"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 5, "biological": 5, "flood": 5, "ice_age": 10, "ai": 10},
    },
    {
        "name": "Musiqa ustasi",
        "emoji": "🎵",
        "value_score": 50,
        "skills": ["Ruhiy qollab-quvvatlash", "Jamoani birlashtirish", "Signal berish", "Xotira saqlash"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 10, "biological": 5, "flood": 5, "ice_age": 10, "ai": 10},
    },
    {
        "name": "Sport ustasi (bokser)",
        "emoji": "🥊",
        "value_score": 73,
        "skills": ["Jismoniy kuch", "Reaksiya tezligi", "Chidamlilik", "Himoya"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 25, "biological": 10, "flood": 20, "ice_age": 25, "volcano": 20},
    },
    {
        "name": "Sport ustasi (kurashchi)",
        "emoji": "🤼",
        "value_score": 72,
        "skills": ["Jismoniy kuch", "Texnikaviy kurash", "Chidamlilik", "Tartib ornatish"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 20, "biological": 10, "flood": 20, "ice_age": 25, "volcano": 20},
    },
    {
        "name": "Alpinist",
        "emoji": "🧗",
        "value_score": 76,
        "skills": ["Tog yollarini bilish", "Arqon ishlash", "Ekstremal sharoitda yashash", "Navigatsiya"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 20, "biological": 10, "flood": 20, "ice_age": 35, "volcano": 30},
    },
    {
        "name": "Suvchi (dalgich)",
        "emoji": "🤿",
        "value_score": 74,
        "skills": ["Suv osti ishlari", "Nafas boshqarish", "Suv tizimlarini tamirlash", "Suv osti kuzatuv"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "biological": 10, "flood": 45, "tsunami": 40, "ice_age": 15},
    },
    {
        "name": "Buxgalter",
        "emoji": "📊",
        "value_score": 60,
        "skills": ["Resurslarni hisoblash", "Iqtisodiy rejalashtirish", "Malumotlarni tahlil qilish", "Zaxirani boshqarish"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 10, "biological": 10, "flood": 10, "ice_age": 10, "ai": 15},
    },
    {
        "name": "Yurist",
        "emoji": "⚖️",
        "value_score": 58,
        "skills": ["Qonun bilimi", "Nizolarni hal qilish", "Muzokaralar", "Qoidalar ornatish"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 10, "biological": 5, "flood": 5, "ice_age": 5, "ai": 15},
    },
    {
        "name": "Diplomat",
        "emoji": "🤝",
        "value_score": 65,
        "skills": ["Muzokaralar", "Konflikt hal qilish", "Muloqot", "Ishontirish"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "biological": 10, "flood": 10, "ice_age": 10, "ai": 20},
    },
    {
        "name": "Sotuvchi",
        "emoji": "🛍️",
        "value_score": 55,
        "skills": ["Savdo muzokaralari", "Mahsulot baholash", "Muloqot", "Resurs almashinuvi"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 10, "biological": 5, "flood": 10, "ice_age": 10, "ai": 5},
    },
    {
        "name": "Savdogar",
        "emoji": "💰",
        "value_score": 60,
        "skills": ["Tijorat", "Resurs boshqarish", "Muzokaralar", "Tarqatish tizimi"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 10, "biological": 5, "flood": 10, "ice_age": 10, "ai": 10},
    },
    {
        "name": "Hunarmand",
        "emoji": "🛠️",
        "value_score": 80,
        "skills": ["Qol mehnat", "Uskuna yasash", "Moddiy resurslarni qayta ishlash", "Amaliy mahorat"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 20, "biological": 15, "flood": 25, "ice_age": 30, "volcano": 25},
    },
    {
        "name": "Temirchi",
        "emoji": "⚒️",
        "value_score": 82,
        "skills": ["Metal ishlash", "Asbob yasash", "Qizitish va shakllantirish", "Metall tamirlash"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 20, "biological": 10, "flood": 25, "ice_age": 30, "volcano": 25},
    },
    {
        "name": "Duradgor",
        "emoji": "🪚",
        "value_score": 78,
        "skills": ["Yogoch ishlash", "Mebel yasash", "Qurilish materiallari", "Oymakorlik"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 15, "biological": 10, "flood": 25, "ice_age": 25, "volcano": 20},
    },
    {
        "name": "Tikuvchi",
        "emoji": "🧵",
        "value_score": 68,
        "skills": ["Kiyim tikish", "Mato tamirlash", "Issiq kiyimlar yasash", "Material tejash"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 10, "biological": 10, "flood": 10, "ice_age": 30, "volcano": 15},
    },
    {
        "name": "Kosmetolog",
        "emoji": "💄",
        "value_score": 42,
        "skills": ["Teri parvarishi", "Sanitariya", "Dori osimliklar bilimi", "Psixologik tasir"],
        "apocalypse_bonus": {"virus": 10, "nuclear": 5, "biological": 10, "flood": 5, "ice_age": 5, "ai": 5},
    },
    {
        "name": "Politsiyachi",
        "emoji": "👮",
        "value_score": 74,
        "skills": ["Tartib saqlash", "Tahdidni aniqlash", "Tergov qilish", "Jismoniy tasir"],
        "apocalypse_bonus": {"virus": 15, "nuclear": 25, "biological": 15, "flood": 20, "ice_age": 20, "ai": 25},
    },
    {
        "name": "Astronom",
        "emoji": "🔭",
        "value_score": 65,
        "skills": ["Yulduzlar boyicha navigatsiya", "Asteroid xavfi bashorati", "Ilmiy tahlil", "Yonalish aniqlash"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 15, "biological": 5, "flood": 10, "asteroid": 45, "solar_flare": 35},
    },
    {
        "name": "Oziq-ovqat texnologi",
        "emoji": "🥫",
        "value_score": 82,
        "skills": ["Konservalash", "Oziq-ovqat saqlash", "Zaharlanishni aniqlash", "Oziqa qiymati tahlili"],
        "apocalypse_bonus": {"virus": 25, "nuclear": 20, "biological": 25, "flood": 25, "ice_age": 30, "volcano": 25},
    },
    {
        "name": "Yadro fizigi",
        "emoji": "☢️",
        "value_score": 85,
        "skills": ["Radiatsiya olchash", "Yadro reaktori", "Himoya usullari", "Radiatsion xavfsizlik"],
        "apocalypse_bonus": {"virus": 5, "nuclear": 60, "biological": 5, "flood": 5, "asteroid": 20, "solar_flare": 30},
    },
    {
        "name": "Suv taminoti mutaxassisi",
        "emoji": "🚰",
        "value_score": 86,
        "skills": ["Suv filtrlash", "Suv sifati nazorati", "Quduq qazish", "Suv zaxirasi boshqarish"],
        "apocalypse_bonus": {"virus": 30, "nuclear": 25, "biological": 30, "flood": 35, "ice_age": 25, "volcano": 20},
    },
]


def get_random_profession() -> dict[str, Any]:
    """Return a random profession from the list."""
    return random.choice(PROFESSIONS)


def get_profession_by_name(name: str) -> dict[str, Any] | None:
    """Return a profession dict by its name, or None if not found."""
    for profession in PROFESSIONS:
        if profession["name"].lower() == name.lower():
            return profession
    return None


def get_professions_for_apocalypse(apocalypse_type: str, top_n: int = 10) -> list[dict[str, Any]]:
    """
    Return professions sorted by their bonus score for a given apocalypse type.

    Args:
        apocalypse_type: The key of the apocalypse (e.g. 'virus', 'nuclear').
        top_n: How many top professions to return.

    Returns:
        Sorted list of profession dicts (most valuable first).
    """
    scored = [
        (p, p["apocalypse_bonus"].get(apocalypse_type, 0))
        for p in PROFESSIONS
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in scored[:top_n]]
