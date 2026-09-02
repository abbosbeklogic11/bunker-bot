"""
Hobbies data module for BUNKER game.
Contains 50+ hobbies with value scores and bunker practical benefits.
"""
from typing import Dict, Any, List
import random

HOBBIES: List[Dict[str, Any]] = [
    {"name": "Ovchilik", "emoji": "🏹", "value_score": 75, "special_skill": "Tashqaridan ozuqa topish va pistirma qilish"},
    {"name": "Baliqchilik", "emoji": "🎣", "value_score": 60, "special_skill": "Suv havzalaridan ozuqa manbai topish"},
    {"name": "Alpinizm", "emoji": "🧗", "value_score": 65, "special_skill": "Balandliklarda ishlash, arqon va tugunlar mahorati"},
    {"name": "Bog'dorchilik", "emoji": "🌱", "value_score": 85, "special_skill": "Bunker issiqxonasida o'simlik yetishtirish"},
    {"name": "Hayvon parvarishi", "emoji": "🐕", "value_score": 70, "special_skill": "Qo'riqchi va foydali hayvonlarni boqish"},
    {"name": "Futbol", "emoji": "⚽", "value_score": 45, "special_skill": "Jamoaviy jismoniy chidamlilik va tezlik"},
    {"name": "Kurash", "emoji": "🤼", "value_score": 65, "special_skill": "Yaqin masofadagi o'zini himoya qilish mahorati"},
    {"name": "Karate / Taekwondo", "emoji": "🥋", "value_score": 65, "special_skill": "Jismoniy intizom va jang san'ati"},
    {"name": "Suzish", "emoji": "🏊", "value_score": 55, "special_skill": "Suvda uzoq vaqt harakatlanish va nafasni ushlash"},
    {"name": "Yugurish (Marafon)", "emoji": "🏃", "value_score": 50, "special_skill": "Yuqori yurak-qon tomir chidamliligi"},
    {"name": "Og'ir atletika", "emoji": "🏋️", "value_score": 60, "special_skill": "Og'ir yuklarni ko'tarish va buzish ishlari"},
    {"name": "Tikuvchilik", "emoji": "🧵", "value_score": 80, "special_skill": "Kiyim-kechak, chodir va matolarni ta'mirlash"},
    {"name": "Kulolchilik", "emoji": "🏺", "value_score": 60, "special_skill": "Loydan idish va suv saqlash vositalari yasash"},
    {"name": "Duradgorlik", "emoji": "🪚", "value_score": 85, "special_skill": "Yog'ochdan mebel va bunker konstruksiyalari yasash"},
    {"name": "Elektrotexnika", "emoji": "🔌", "value_score": 90, "special_skill": "Kichik elektr jihozlarini ta'mirlash"},
    {"name": "Dasturlash", "emoji": "💻", "value_score": 70, "special_skill": "Bunker avtomatika va xavfsizlik tizimlarini sozlash"},
    {"name": "Radio aloqa (Radiohavaskor)", "emoji": "📻", "value_score": 90, "special_skill": "Tashqi dunyo bilan qisqa to'lqinli aloqa o'rnatish"},
    {"name": "Fotosurat", "emoji": "📷", "value_score": 35, "special_skill": "Voqealarni hujjatlashtirish va kuzatish"},
    {"name": "Rasm chizish", "emoji": "🎨", "value_score": 40, "special_skill": "Psixologik yengillik va bunker devorlariga xarita chizish"},
    {"name": "Gitara chalish", "emoji": "🎸", "value_score": 55, "special_skill": "Guruh kayfiyatini ko'tarish va stressni kamaytirish"},
    {"name": "Pianino / Musiqa", "emoji": "🎹", "value_score": 45, "special_skill": "Psixologik yengillik"},
    {"name": "Qo'shiq aytish", "emoji": "🎤", "value_score": 40, "special_skill": "Ijtimoiy kayfiyatni ko'tarish"},
    {"name": "Kitobxonlik", "emoji": "📚", "value_score": 60, "special_skill": "Keng ensiklopedik bilimlar zaxirasi"},
    {"name": "Tarix o'rganish", "emoji": "📜", "value_score": 50, "special_skill": "O'tmish inqirozlaridan xulosa chiqarish"},
    {"name": "Geografiya va Xaritalar", "emoji": "🗺️", "value_score": 75, "special_skill": "Yo'nalishni aniqlash va xarita o'qish"},
    {"name": "Astronomiya", "emoji": "🔭", "value_score": 60, "special_skill": "Yulduzlar bo'yicha vaqt va faslni aniqlash"},
    {"name": "Birinchi tibbiy yordam", "emoji": "🩹", "value_score": 95, "special_skill": "Jarohatlarni bog'lash va jonlantirish"},
    {"name": "Oshpazlik", "emoji": "🍳", "value_score": 85, "special_skill": "Cheklangan oziq-ovqatdan to'yimli taomlar tayyorlash"},
    {"name": "Non yopish", "emoji": "🍞", "value_score": 80, "special_skill": "Un va dondan uzoq saqlanuvchi non tayyorlash"},
    {"name": "Fermerlik", "emoji": "🚜", "value_score": 85, "special_skill": "Don va sabzavot yetishtirish metodikasi"},
    {"name": "Universal usta", "emoji": "🔧", "value_score": 90, "special_skill": "Har qanday buzilgan mexanizmni sozlash"},
    {"name": "Yog'och o'ymakorligi", "emoji": "🪵", "value_score": 55, "special_skill": "Foydali yog'och buyumlar tayyorlash"},
    {"name": "Metallga ishlov berish", "emoji": "🔨", "value_score": 85, "special_skill": "Temirdan zaruriy vositalar yasash"},
    {"name": "Kashtachilik", "emoji": "🪡", "value_score": 45, "special_skill": "Nozik qo'l mehnati va sabr"},
    {"name": "Asalarichilik", "emoji": "🐝", "value_score": 70, "special_skill": "Asal va propolis orqali dorivor moddalar olish"},
    {"name": "Parrandachilik", "emoji": "🐔", "value_score": 75, "special_skill": "Tuxum va go'sht manbaini ko'paytirish"},
    {"name": "Chorvachilik", "emoji": "🐄", "value_score": 80, "special_skill": "Sut va go'sht yetishtirish"},
    {"name": "Shaxmat", "emoji": "♟️", "value_score": 65, "special_skill": "Strategik fikrlash va sabr"},
    {"name": "Mantiqiy boshqotirmalar", "emoji": "🧩", "value_score": 60, "special_skill": "Tezkor tahlil va mantiqiy yechimlar"},
    {"name": "Meditatsiya va Yoga", "emoji": "🧘", "value_score": 65, "special_skill": "Nafas nazorati va aqliy barqarorlik"},
    {"name": "Boks", "emoji": "🥊", "value_score": 65, "special_skill": "Reaksiya tezligi va o'zini himoya qilish"},
    {"name": "Kamondan otish", "emoji": "🎯", "value_score": 75, "special_skill": "Ovozsiz va masofadan nishonga urish"},
    {"name": "Akrobatika", "emoji": "🤸", "value_score": 55, "special_skill": "Tor joylarda epchillik va egiluvchanlik"},
    {"name": "Velosiped sporti", "emoji": "🚴", "value_score": 50, "special_skill": "Oyoq mushaklari kuchi va velotransport bilimi"},
    {"name": "Qayiq haydash", "emoji": "🚣", "value_score": 60, "special_skill": "Suv yo'llarida harakatlanish"},
    {"name": "Choychilik va Gerbariy", "emoji": "🍵", "value_score": 75, "special_skill": "Dorivor o'tlarni tanish va qaynatmalar tayyorlash"},
    {"name": "Qulflarni ochish (Lockpicking)", "emoji": "🔐", "value_score": 80, "special_skill": "Yopiq bunker eshiklari va omborlarni ochish"},
    {"name": "Trikotaj va to'qish", "emoji": "🧶", "value_score": 70, "special_skill": "Issiq paypoq, qo'lqop va kiyimlar to'qish"},
    {"name": "Kimyoviy tajribalar", "emoji": "🧪", "value_score": 80, "special_skill": "Oddiy moddalardan sovun, spirt va eritmalar olish"},
    {"name": "Yozuvchilik va Kundalik", "emoji": "✍️", "value_score": 40, "special_skill": "Bunker tarixini saqlab qolish"}
]

def get_random_hobby() -> Dict[str, Any]:
    return random.choice(HOBBIES)

def get_hobby_by_name(name: str) -> Dict[str, Any]:
    for h in HOBBIES:
        if h["name"].lower() == name.lower():
            return h
    return HOBBIES[0]
