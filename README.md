# 🏢 BUNKER — Telegram Multiplayer Game Platform

> **20 kishigacha real-time o'ynaladigan, strategik va psixologik "BUNKER" multiplayer o'yin platformasi.**
> Texnologiyalar: **Python 3.12 + aiogram 3.x + PostgreSQL + Redis + APScheduler**

---

## 🌟 Asosiy Xususiyatlar

- 👥 **5 dan 20 nafargacha o'yinchi:** Guruhda 1 ta o'yinda 20 kishigacha ishtirok etish imkoniyati.
- 🏆 **4 ta G'olib mexanikasi:** Oxirida faqat eng munosib 4 ta o'yinchi bunkerga kiradi va omon qoladi.
- 🤫 **Server Authoritative & Maxfiylik:** Barcha maxfiy kartalar va xususiyatlar faqat botning Private chatiga yuboriladi, guruhga faqat ruxsat etilgan ma'lumotlar ko'rsatiladi.
- 👨‍💼 **60+ Kasb, 50+ Hobbi, 12 ta Apokalipsis:** Har safar mutlaqo yangi va takrorlanmas ssenariy.
- ⚡ **20+ Maxsus Qobiliyatlar & 30+ Maxfiy Kartalar:** Shifokor, Detektiv, Himoyachi, Qutqaruv, Qasos va boshqalar.
- ⚠️ **Dinamik Favqulodda Eventlar:** Elektr uzilishi, suv filtri buzilishi, ichki epidemiya va h.k.
- ⏱ **Avtomatlashtirilgan Real-Time Timerlar:** Redis va APScheduler orqali server restart bo'lsa ham timerlar yo'qolmaydi.
- ⚔️ **Durang va Duel mexanikasi:** Ovozlar teng kelganda 60 soniyalik bahs va duel ovozi.
- 📊 **Profil, Iqtisodiyot va Yutuqlar (Achievements):** Coins, Diamonds, Win Rate, Level, MVP.
- 🛡 **Anti-Cheat & Callback Security:** Barcha harakatlar server tomonidan tekshiriladi, takroriy ovoz va ruxsatsiz bosishlardan to'liq himoyalangan.

---

## 📂 Loyiha Strukturasi

```
bunker_game/
├── bot/
│   ├── main.py                    # Ilovaning asosiy kirish nuqtasi
│   ├── config/
│   │   ├── settings.py            # Pydantic environment sozlamalari
│   │   └── game_config.py         # O'yin parametr va konfiguratsiyalari
│   ├── handlers/
│   │   ├── group/                 # Guruh chat handlerlari (/bunker, /admin, /stop_game)
│   │   └── private/               # Shaxsiy chat handlerlari (/start, /profile)
│   ├── keyboards/                 # Inline tugmalar (Lobby, Dashboard, Ovoz berish, Kartalar)
│   ├── callbacks/                 # Callback query routerlari
│   ├── middlewares/               # Auth, DB user upsert va Throttling
│   └── filters/                   # Admin va Chat Type filtrlari
├── game/
│   ├── engine.py                  # Asosiy Game Engine (Pure Business Logic)
│   ├── state_machine.py           # Game State Machine (FSM)
│   ├── engine_events.py           # Event-Driven EventBus
│   ├── data/                      # Kasblar, Sog'liq, Hobbi, Kartalar, Apokalipsis ma'lumotlari
│   ├── randomizer/                # Tasodifiy generatsiya va balans tekshiruvchisi
│   ├── systems/                   # Ovoz berish, Qobiliyatlar, Kartalar, Eventlar, Mukofotlar
│   └── timers/                    # Redis Timer Engine va APScheduler
├── database/
│   ├── connection.py              # asyncpg Connection Pool
│   ├── migrations/                # PostgreSQL SQL migratsiyalari
│   └── repositories/              # Repozitoriylar (Users, Games, Players, Votes, Events)
├── models/                        # Pydantic v2 ma'lumot modellari
├── services/                      # Telegram xabar va Dashboard boshqaruv servislari
├── utils/                         # Matn formatlovchilar, validatorlar va kriptografiya
├── tests/                         # Unit va integratsion testlar
├── docker-compose.yml             # Docker orqali Postgres + Redis + Bot ishga tushirish
├── Dockerfile                     # Bot Dockerfile
├── requirements.txt               # Python bog'liqliklari
└── .env.example                   # Muhit o'zgaruvchilari namunasi
```

---

## 🚀 Ishga Tushirish Yo'riqnomasi

### 1. Talablar
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### 2. O'rnatish

```bash
# 1. Virtual muhit yaratish va faollashtirish
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/MacOS:
source venv/bin/activate

# 2. Bog'liqliklarni o'rnatish
pip install -r requirements.txt
```

### 3. Konfiguratsiya (.env)

`.env.example` faylidan nusxa olib `.env` faylini yarating:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bunker_db
REDIS_URL=redis://localhost:6379/0
ADMIN_IDS=123456789,987654321
DEBUG=True
LOG_LEVEL=INFO
```

### 4. Ma'lumotlar Bazasini Sozlash

PostgreSQL bazangizda SQL migratsiyalarni ishga tushiring:

```bash
psql -U postgres -d bunker_db -f database/migrations/001_initial.sql
psql -U postgres -d bunker_db -f database/migrations/002_seed_achievements.sql
```

### 5. Botni Ishga Tushirish

```bash
python -m bot.main
```

---

## 🐳 Docker orqali ishga tushirish (Tavsiya etiladi)

Barcha kerakli xizmatlarni (Postgres, Redis va Bot) bir buyruq bilan ishga tushirish mumkin:

```bash
docker-compose up -d --build
```

---

## 🎮 O'yin Jarayoni (Game Loop)

1. **Guruhda boshlash:** `/bunker` buyrug'i beriladi.
2. **Qo'shilish:** O'yinchilar `[➕ O'yinga qo'shilish]` tugmasini bosadi (avval botga `/start` yuborilgan bo'lishi shart).
3. **Boshlanish:** 20 kishi to'lganda avtomatik yoki yaratuvchi tomonidan boshlanadi.
4. **Maxfiy kartalar:** Har bir o'yinchiga shaxsiy chatida maxfiy kartalari, kasbi va parametrlari beriladi.
5. **Raundlar (1-5):**
   - 🔓 Xususiyat ochiladi (1-raund: Kasb; 2-raund: Yosh va Sog'liq; va h.k.)
   - ⏱ **3 daqiqa Muhokama:** O'yinchilar guruhda o'zlarini himoya qiladi.
   - ⚡ **Qobiliyatlar bosqichi:** Private chat orqali qobiliyat/kartalar ishlatiladi.
   - 🗳 **Ovoz berish:** Bunkerdan kim chiqarilishi ovozga qo'yiladi.
   - 🚨 **Chiqarilish:** Eng ko'p ovoz olgan o'yinchi o'yindan chiqariladi.
   - ⚠️ **Event:** Tasodifiy inqiroz yuz beradi (masalan, suv filtri buzilishi).
6. **Final:** Bunker sig'imi 4 kishiga yetganda 4 ta g'olib e'lon qilinadi va ularga Coins & Diamonds mukofotlari beriladi.

---

## 🧪 Testlarni Ishga Tushirish

```bash
pytest tests/ -v
```
