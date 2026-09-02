"""
Inventory items data module for BUNKER game.
Contains 50+ survival items (NO weapons, purely practical survival gear).
"""
from typing import Dict, Any, List
import random

INVENTORY_ITEMS: List[Dict[str, Any]] = [
    {"name": "Tibbiy sumka (To'liq to'plam)", "emoji": "🧰", "description": "Barcha asosiy dori-darmon, bint va shpritslar bor.", "value_score": 95, "rarity": "LEGENDARY", "uses": "Jarohat va kasalliklarni to'liq davolash", "weight": 4},
    {"name": "Portativ suv filtri (Keramika)", "emoji": "🧪", "description": "10,000 litr ifloslangan suvni 99.9% tozalaydi.", "value_score": 95, "rarity": "LEGENDARY", "uses": "Suv tanqisligini bartaraf etish", "weight": 2},
    {"name": "Dozimetr / Radiometr (Raqamli)", "emoji": "☢️", "description": "Radiatsiya va rentgen nurlari miqdorini aniq o'lchaydi.", "value_score": 90, "rarity": "EPIC", "uses": "Radiatsiya xavfini oldindan bilish", "weight": 1},
    {"name": "Ko'p funksiyali asbob (Leatherman)", "emoji": "🛠️", "description": "Pichoq, ombir, arra, otvyortka bitta asbobda.", "value_score": 85, "rarity": "RARE", "uses": "Mayda ta'mirlash ishlari", "weight": 2},
    {"name": "Quyosh paneli + Powerbank (50,000 mAh)", "emoji": "☀️", "description": "Quyosh nuridan elektr energiyasi to'playdi.", "value_score": 85, "rarity": "RARE", "uses": "Kichik asboblarni zaryadlash", "weight": 3},
    {"name": "Portativ benzin generatori (Kichik)", "emoji": "⚡", "description": "1 kVt quvvatga ega, zaxira elektr manbai.", "value_score": 95, "rarity": "LEGENDARY", "uses": "Favqulodda elektr ta'minoti", "weight": 8},
    {"name": "Urug'lar to'plami (Sabzavot va don)", "emoji": "🌱", "description": "Pomidor, bodring, bug'doy va ko'katlar urug'i (1 kg).", "value_score": 90, "rarity": "EPIC", "uses": "Bunker issiqxonasida oziq-ovqat yetishtirish", "weight": 2},
    {"name": "Antibiotiklar zaxirasi (Keng spektrli, 6 oylik)", "emoji": "💊", "description": "Bakterial infeksiyalarga qarshi kuchli dorilar.", "value_score": 90, "rarity": "EPIC", "uses": "Epidemiyaning oldini olish", "weight": 1},
    {"name": "Konservalangan oziq-ovqat qutisi (30 kunlik)", "emoji": "🥫", "description": "Go'sht, baliq va bo'tqa konservalari to'plami.", "value_score": 85, "rarity": "RARE", "uses": "Oziq-ovqat zaxirasini oshirish", "weight": 7},
    {"name": "Gaz niqobi (Professional filtr bilan, 2 dona)", "emoji": "🎭", "description": "Zaharli gazlar va biologik changdan himoya qiladi.", "value_score": 85, "rarity": "RARE", "uses": "Tashqariga xavfsiz chiqish", "weight": 2},
    {"name": "Qisqa to'lqinli Walkie-Talkie (Ratsiya jufti)", "emoji": "📻", "description": "5 km masofada aloqa o'rnatish imkoniyati.", "value_score": 80, "rarity": "RARE", "uses": "Guruh a'zolari o'rtasida ichki aloqa", "weight": 2},
    {"name": "Kimyoviy himoya kombinezoni (OZK)", "emoji": "🦺", "description": "Kislota, zahar va radiatsion changdan to'liq izolyatsiya.", "value_score": 80, "rarity": "RARE", "uses": "Xavfli zonalarda ishlash", "weight": 4},
    {"name": "Taktik fonar (Dinamoli + Akkumulyatorli)", "emoji": "🔦", "description": "Batareyasiz, qo'l bilan buraladigan kuchli yoritgich.", "value_score": 75, "rarity": "UNCOMMON", "uses": "Elektr o'chganda yorug'lik manbai", "weight": 1},
    {"name": "Statik arqon (Mustahkam kapron, 50 metr)", "emoji": "🪢", "description": "500 kg og'irlikka bardosh beruvchi alpinist arqoni.", "value_score": 75, "rarity": "UNCOMMON", "uses": "Balandlikka chiqish va yuk tortish", "weight": 3},
    {"name": "Chaqmoqtosh va magnitli olov yoqqich", "emoji": "🔥", "description": "Suvda ho'l bo'lsa ham uchqun chiqaruvchi vosita.", "value_score": 70, "rarity": "UNCOMMON", "uses": "Olov yoqish", "weight": 1},
    {"name": "Vitaminlar kompleksi (1 yillik)", "emoji": "🍊", "description": "Quyoshsiz muhitda C, D3, B12 vitaminlari tanqisligini oldini oladi.", "value_score": 75, "rarity": "UNCOMMON", "uses": "Immunitetni quvvatlash", "weight": 1},
    {"name": "Suv saqlash idishi (20 litrli buklanuvchi)", "emoji": "🪣", "description": "Oziq-ovqat plastikidan tayyorlangan sig'imli idish.", "value_score": 70, "rarity": "UNCOMMON", "uses": "Suv zaxirasini tashish", "weight": 1},
    {"name": "Universal kalitlar va master-otvyortkalar to'plami", "emoji": "🔩", "description": "Har xil o'lchamdagi bolt va gaykalarni burash uchun.", "value_score": 80, "rarity": "RARE", "uses": "Bunker quvurlari va mexanizmlari ta'miri", "weight": 5},
    {"name": "Shamol o'tkazmaydigan issiq termoko'rpa (4 dona)", "emoji": "🛋️", "description": "Tana haroratini 90% saqlab qoluvchi kosmik folga ko'rpa.", "value_score": 75, "rarity": "UNCOMMON", "uses": "Muzlik davrida isinish", "weight": 1},
    {"name": "Katta zaxira shamlar to'plami (50 dona)", "emoji": "🕯️", "description": "Uzoq yonuvchi kerosin-parafinli shamlar.", "value_score": 60, "rarity": "COMMON", "uses": "Oddiy yorug'lik", "weight": 3},
    {"name": "Dezinfeksiya vositasi (5 litr spirt + xlor eritmasi)", "emoji": "🧴", "description": "Mikroblarni o'ldirish va sirtlarni zararsizlantirish.", "value_score": 80, "rarity": "RARE", "uses": "Antiseptika va tozalik", "weight": 5},
    {"name": "Og'riq qoldiruvchi kuchli vositalar (Promedol/Morfin analogi)", "emoji": "💉", "description": "Shok holatida og'riqni bir zumda bosuvchi ampulalar.", "value_score": 85, "rarity": "EPIC", "uses": "Og'ir jarohatlarda birinchi yordam", "weight": 1},
    {"name": "Quritilgan meva va yong'oqlar to'plami (10 kg)", "emoji": "🥜", "description": "Yuqori kaloriyali, uzoq saqlanuvchi energiya manbai.", "value_score": 70, "rarity": "UNCOMMON", "uses": "Tezkor to'yimli ozuqa", "weight": 10},
    {"name": "Bunker va mintaqa batafsil topografik xaritasi", "emoji": "🗺️", "description": "Yer osti yo'llari, suv manbalari va bunker joylashuvi ko'rsatilgan.", "value_score": 85, "rarity": "RARE", "uses": "Taktik yo'nalish tanlash", "weight": 1},
    {"name": "Quyoshli batareyada ishlovchi noutbuk (Ensiklopediyalar bilan)", "emoji": "💻", "description": "Vikipediya, tibbiy qo'llanmalar va muhandislik chizmalari yuklangan.", "value_score": 95, "rarity": "LEGENDARY", "uses": "Har qanday fandan to'liq bilimlar bazasi", "weight": 3},
    {"name": "Kichik qo'l payvandlash uskunasi (Invertor)", "emoji": "⚡", "description": "Temir konstruksiyalarni payvandlash va mustahkamlash.", "value_score": 85, "rarity": "RARE", "uses": "Bunker eshiklarini mustahkamlash", "weight": 6},
    {"name": "Gidravlik domkrat (10 tonnalik)", "emoji": "🏗️", "description": "Qulagan beton bloklar va og'ir eshiklarni ko'tarish.", "value_score": 80, "rarity": "RARE", "uses": "Vayronalar ostidan chiqish", "weight": 7},
    {"name": "O'simliklar uchun maxsus LED fitolampa", "emoji": "💡", "description": "Quyosh nuri o'rnini bosuvchi ultrabinafsha chiroq.", "value_score": 80, "rarity": "RARE", "uses": "Yer osti hosildorligini 2 barobar oshirish", "weight": 2},
    {"name": "Suvni distillash uskunasi (Kichik laboratoriya)", "emoji": "⚗️", "description": "Sho'r va zaharli suvdan sof distillangan suv olish.", "value_score": 85, "rarity": "RARE", "uses": "Mukammal toza suv olish", "weight": 4},
    {"name": "Insulin zaxirasi va glyukometr (Sovutgichli sumkada)", "emoji": "💉", "description": "Qandli diabeti bor insonni saqlab qolish vositasi.", "value_score": 75, "rarity": "RARE", "uses": "Diabetik bemorni davolash", "weight": 2},
    {"name": "Og'ir harbiy belkurak va cho'kich (Saper)", "emoji": "⛏️", "description": "Qazish va yer osti yo'llarini tozalash uchun mustahkam po'lat vosita.", "value_score": 75, "rarity": "UNCOMMON", "uses": "Qazish ishlari", "weight": 3},
    {"name": "Bino ichidagi harorat va namlik o'lchagich (Gigrometr)", "emoji": "🌡️", "description": "Bunkerdagi iqlim va mog'or xavfini kuzatish.", "value_score": 60, "rarity": "COMMON", "uses": "Bunker muhiti monitoringi", "weight": 1},
    {"name": "Quloq tiqinlari va himoya ko'zoynagi (10 to'plam)", "emoji": "🥽", "description": "Portlash shovqini va changdan ko'z-quloqni himoyalash.", "value_score": 55, "rarity": "COMMON", "uses": "Shaxsiy xavfsizlik", "weight": 1},
    {"name": "Universal batareyalar to'plami (AA / AAA - 100 dona)", "emoji": "🔋", "description": "Asboblar va radio uchun uzoq muddatli quvvat.", "value_score": 70, "rarity": "UNCOMMON", "uses": "Barcha portativ vositalarni ishlatish", "weight": 2},
    {"name": "Daraxt va metall kesuvchi qo'l arra (Buklanuvchi)", "emoji": "🪚", "description": "O'tkir tishli qattiq po'lat arra.", "value_score": 70, "rarity": "UNCOMMON", "uses": "Yog'och va quvur kesish", "weight": 1},
    {"name": "Qo'lda buraladigan kiyim yuvish mashinasi (Portativ)", "emoji": "🧺", "description": "Suvni tejab kiyimlarni yuvish va gigiyenani saqlash.", "value_score": 65, "rarity": "COMMON", "uses": "Gigiyena", "weight": 4},
    {"name": "Shoxobcha oshxona anjomlari (Qozon, choynak, metall kosa)", "emoji": "🍳", "description": "Zanglamas po'latdan uzoq muddatli idishlar.", "value_score": 65, "rarity": "COMMON", "uses": "Ovqat pishirish", "weight": 3},
    {"name": "Shifobaxsh o'simliklar quritilgan to'plami (Moychechak, na'matak)", "emoji": "🍵", "description": "Shamollash va oshqozon kasalliklariga qarshi tabiiy damlamalar.", "value_score": 65, "rarity": "COMMON", "uses": "Tabiiy davolash", "weight": 1},
    {"name": "Tug'ruq qabul qilish maxsus steril to'plami", "emoji": "👶", "description": "Steril qisqichlar, skalpel va bog'lov vositalari.", "value_score": 80, "rarity": "RARE", "uses": "Favqulodda vaziyatda tug'ruq qabul qilish", "weight": 2},
    {"name": "Yong'in o'chirgich (Uglerod kislotali, 2 dona)", "emoji": "🧯", "description": "Elektr simlari va qattiq moddalar yong'inini o'chirish.", "value_score": 85, "rarity": "RARE", "uses": "Yong'in xavfsizligi", "weight": 8},
    {"name": "Mikroskop (Portativ laboratoriya linzasi bilan)", "emoji": "🔬", "description": "Suv va qondagi parazitlarni aniqlash.", "value_score": 80, "rarity": "RARE", "uses": "Laboratoriya tahlillari", "weight": 2},
    {"name": "Tish davolash va sug'urish kichik to'plami", "emoji": "🦷", "description": "Tish og'rig'ida vaqtincha plomba va sug'urish ombiri.", "value_score": 75, "rarity": "UNCOMMON", "uses": "Stomatologik yordam", "weight": 1},
    {"name": "Germetik yopiluvchi suv o'tkazmas sumka (Draybeg 60L)", "emoji": "🎒", "description": "Hujjatlar va nozik elektronikani suvdan asrash.", "value_score": 65, "rarity": "COMMON", "uses": "Asboblarni quruq saqlash", "weight": 1},
    {"name": "O'zi zaryadlanuvchi soat (Mexanik, kompasli)", "emoji": "⌚", "description": "Vaqt va yo'nalishni aniq bilish vositasi.", "value_score": 60, "rarity": "COMMON", "uses": "Vaqt nazorati", "weight": 1},
    {"name": "Signal beruvchi raketa to'plami (5 dona)", "emoji": "🎆", "description": "Uzoq masofadagi qutqaruvchilarga signal berish.", "value_score": 70, "rarity": "UNCOMMON", "uses": "Qutqaruv signali", "weight": 2},
    {"name": "Qalin charmdan ishlangan ishchi etiklar (3 juft)", "emoji": "🥾", "description": "Mix va shishadan oyoqni himoyalovchi mustahkam poyabzal.", "value_score": 65, "rarity": "COMMON", "uses": "Oyoq himoyasi", "weight": 3},
    {"name": "Bog'lovchi matolar va elastik bintlar (100 metr)", "emoji": "🩹", "description": "Chiqish va sinishlarda mustahkamlovchi vosita.", "value_score": 65, "rarity": "COMMON", "uses": "Jarohatlarni bog'lash", "weight": 2},
    {"name": "Qo'rg'oshin plastina (Radiatsiyadan himoya ekrani)", "emoji": "🧱", "description": "Kichik joyni radiatsiyadan to'liq to'suvchi og'ir qatlam.", "value_score": 85, "rarity": "RARE", "uses": "Radiatsiya ekrani", "weight": 12},
    {"name": "Yelim va germetik (Suyuq rezina - 5 balon)", "emoji": "🧴", "description": "Suv quvurlari va yoriqlarni darhol yamash vositasi.", "value_score": 75, "rarity": "UNCOMMON", "uses": "Teshik va yoriqlarni berkitish", "weight": 2}
]

def get_random_item() -> Dict[str, Any]:
    return random.choice(INVENTORY_ITEMS)

def get_item_by_name(name: str) -> Dict[str, Any]:
    for it in INVENTORY_ITEMS:
        if it["name"].lower() == name.lower():
            return it
    return INVENTORY_ITEMS[0]
