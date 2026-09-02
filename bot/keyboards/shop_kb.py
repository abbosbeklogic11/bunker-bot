"""
Shop keyboards for BUNKER game matching official in-game store designs.
"""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

SHOP_ITEMS = [
    {
        "code": "shield",
        "name": "Haydashdan himoya",
        "icon": "🛡️",
        "price": 300,
        "description": "Bunkerdan bir marta ovoz berishda chiqarib yuborilishdan 100% himoya qiladi."
    },
    {
        "code": "double_vote",
        "name": "2x ovoz",
        "icon": "⚖️",
        "price": 200,
        "description": "Ovoz berish raundida siz bergan ovoz 2 barobar (2 ta ovoz) bo'lib hisoblanadi."
    },
    {
        "code": "spy",
        "name": "Josus",
        "icon": "🕵️",
        "price": 200,
        "description": "Ixtiyoriy bitta o'yinchining hali ochilmagan maxfiy xususiyatini xufyona ko'rish imkonini beradi."
    },
    {
        "code": "reveal_other",
        "name": "Fosh qilish",
        "icon": "📜",
        "price": 200,
        "description": "Tanlangan o'yinchini bitta maxfiy xususiyatini hammaga darhol oshkor qilishga majbur qiladi."
    },
    {
        "code": "reroll_card",
        "name": "Yangi karta",
        "icon": "♻️",
        "price": 200,
        "description": "O'zingizdagi foydasiz buyum/inventar kartasini yangi tasodifiy buyumga almashtirib beradi."
    },
    {
        "code": "reroll_prof",
        "name": "Yangi kasb",
        "icon": "🎴",
        "price": 200,
        "description": "O'yindagi kasbingizni yangi tasodifiy boshqa kasbga o'zgartiradi."
    },
    {
        "code": "swap_attr",
        "name": "Almashtirish",
        "icon": "🔄",
        "price": 200,
        "description": "O'zingizning bitta xususiyatingizni boshqa o'yinchining xususiyati bilan almashtiradi."
    }
]


def get_shop_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for item in SHOP_ITEMS:
        btn_text = f"{item['icon']} {item['name']} — {item['price']}"
        builder.button(text=btn_text, callback_data=f"shop_view:{item['code']}")

    builder.button(text="📊 Profil", callback_data="show_my_profile")
    builder.button(text="🏠 Asosiy menyu", callback_data="back_to_start")

    # 1 column for items, 1 column for navigation
    builder.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1)
    return builder.as_markup()


def get_shop_item_buy_keyboard(item_code: str, price: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=f"🛒 Sotib olish ({price} tanga)", callback_data=f"shop_buy:{item_code}")
    builder.button(text="⬅️ Do'konga qaytish", callback_data="open_shop")
    builder.adjust(1, 1)
    return builder.as_markup()
