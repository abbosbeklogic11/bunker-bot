"""
Bunker configurations data module for BUNKER game.
Contains 8 distinct bunker types with specific resources, amenities, and traits.
"""
from typing import Dict, Any, List
import random

BUNKER_CONFIGS: List[Dict[str, Any]] = [
    {
        "name": "Harbiy Yerosti Bazasi (K-12)",
        "emoji": "🛡️",
        "capacity": 4,
        "food_days": 200,
        "water_days": 180,
        "power_days": 120,
        "has_farm": False,
        "has_medical": True,
        "has_workshop": True,
        "has_radio": True,
        "has_laboratory": False,
        "has_greenhouse": False,
        "special_features": ["Bronlangan avtomatik kirish eshigi", "Mustaqil dizel generator", "Harbiy qurolsiz xavfsizlik kameralari"],
        "description": "Mustahkam temir-betonli harbiy bunker. Tibbiyot xonasi va ta'mirlash ustaxonasi mavjud, biroq qishloq xo'jaligi yo'q."
    },
    {
        "name": "Ilmiy-Tadqiqot Eko-Bunkeri (Biosfera-3)",
        "emoji": "🌱",
        "capacity": 4,
        "food_days": 150,
        "water_days": 200,
        "power_days": 90,
        "has_farm": True,
        "has_medical": True,
        "has_workshop": False,
        "has_radio": True,
        "has_laboratory": True,
        "has_greenhouse": True,
        "special_features": ["Avtomatlashtirilgan gidroponika issiqxonasi", "Kimyoviy-biologik laboratoriya", "Suvni 100% tozalash tizimi"],
        "description": "Uzoq muddat o'simlik va ozuqa yetishtirishga mo'ljallangan zamonaviy ilmiy majmua."
    },
    {
        "name": "Tog' Bag'ridagi Shaxta Bunkeri (Granit)",
        "emoji": "⛰️",
        "capacity": 4,
        "food_days": 180,
        "water_days": 150,
        "power_days": 100,
        "has_farm": False,
        "has_medical": False,
        "has_workshop": True,
        "has_radio": False,
        "has_laboratory": False,
        "has_greenhouse": False,
        "special_features": ["300 metr granit qatlami ostida", "Katta metallga ishlov ustaxonasi", "Tabiiy yerosti bulog'i"],
        "description": "Eng kuchli zilzila va zarbalarga chidamli, biroq aloqa vositalari va tibbiy jihozlar cheklangan."
    },
    {
        "name": "VIP Elita Boshpanasi (Oasis)",
        "emoji": "💎",
        "capacity": 4,
        "food_days": 240,
        "water_days": 180,
        "power_days": 150,
        "has_farm": True,
        "has_medical": True,
        "has_workshop": False,
        "has_radio": True,
        "has_laboratory": False,
        "has_greenhouse": True,
        "special_features": ["Yuqori qulaylikdagi dam olish xonalari", "Delikates konservalar zaxirasi", "Quyosh va geotermal energiya"],
        "description": "Maksimal oziq-ovqat va qulaylikka ega lyuks bunker, lekin og'ir ta'mirlash uskunalari yetishmaydi."
    },
    {
        "name": "Qadimiy Sovet Fuqaro Himoyasi Bunkeri (GO-42)",
        "emoji": "📻",
        "capacity": 4,
        "food_days": 160,
        "water_days": 140,
        "power_days": 80,
        "has_farm": False,
        "has_medical": True,
        "has_workshop": True,
        "has_radio": True,
        "has_laboratory": False,
        "has_greenhouse": False,
        "special_features": ["Katta mexanik filtr-ventilyatsiya agregati", "Qadimgi radioeshittirish stansiyasi", "Ko'p miqdorda ehtiyot qismlar"],
        "description": "Oddiy, ishonchli, ammo eski uskunalar. Vaqti-vaqti bilan mexanik ta'mirlash talab qiladi."
    },
    {
        "name": "Tibbiy Reabilitatsiya Bunkeri (Vita)",
        "emoji": "🏥",
        "capacity": 4,
        "food_days": 170,
        "water_days": 160,
        "power_days": 110,
        "has_farm": False,
        "has_medical": True,
        "has_workshop": False,
        "has_radio": True,
        "has_laboratory": True,
        "has_greenhouse": False,
        "special_features": ["To'liq jihozlangan jarrohlik xonasi", "Katta dori-darmon zaxirasi", "Sterilizatsiya kameralari"],
        "description": "Virus va biologik ofatlarga qarshi ideal himoyalangan tibbiy markaz."
    },
    {
        "name": "Sanoat Zavodi Yerosti Ombori",
        "emoji": "🏭",
        "capacity": 4,
        "food_days": 140,
        "water_days": 130,
        "power_days": 140,
        "has_farm": False,
        "has_medical": False,
        "has_workshop": True,
        "has_radio": True,
        "has_laboratory": False,
        "has_greenhouse": False,
        "special_features": ["Sanoat tok stanoklari", "Katta dizel yoqilg'isi sisternasi", "Payvandlash va metall xomashyosi"],
        "description": "Muhandis va ustalar uchun ajoyib ustaxona, ammo oziq-ovqat zaxirasi kamroq."
    },
    {
        "name": "Agrar-Fermerlik Yerosti Majmuasi (Zamin)",
        "emoji": "🌾",
        "capacity": 4,
        "food_days": 210,
        "water_days": 190,
        "power_days": 90,
        "has_farm": True,
        "has_medical": False,
        "has_workshop": True,
        "has_radio": False,
        "has_laboratory": False,
        "has_greenhouse": True,
        "special_features": ["Katta yerosti dalasi va urug'lar banki", "Qo'ziqorin va o'simlik parvarish xonalari", "Ozuqani qayta ishlash sexi"],
        "description": "Yillar davomida mustaqil oziq-ovqat bilan ta'minlay oluvchi yopiq agrar majmua."
    }
]

def get_random_bunker_config() -> Dict[str, Any]:
    return random.choice(BUNKER_CONFIGS)
