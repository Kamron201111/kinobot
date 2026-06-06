# 🎬 Kino Bot

aiogram 3.x da yozilgan, Railway'ga deploy qilinadigan to'liq kino boti.
Rangli tugmalar (Bot API 9.4) va premium emoji bilan.

## ✨ Imkoniyatlar

**Foydalanuvchi uchun:**
- 🎬 Kino ko'rish (kod orqali) + kinolar to'plami kanali
- 📢 Asosiy kanal havolasi
- 💎 Premium tarif sotib olish (1/10/30 kun)
  - To'lov: **Humo**, **Uzcard** (chek orqali), **Telegram Stars** (avtomatik)
- 📣 Reklama bo'limi (admin bilan bog'lanish)

**Admin uchun (`/admin`):**
- ➕ Qo'lda kino qo'shish (kod + nom + tavsif + video)
- 📊 Statistika (jami / bugun qo'shilgan / bugun tark etgan)
- 🔒 Majburiy obuna (ommaviy + zayavkali kanallar)
- 💰 Narxlar va karta raqamlarini sozlash
- 🔗 Kanal havolalarini sozlash
- 👥 Admin qo'shish / o'chirish
- 📤 Xabar yuborish (hammaga yoki faqat premiumga)
- ✅ To'lov cheklarini tasdiqlash

**Premium afzalliklari:**
- 🔔 Yangi kinolardan **birinchi** bo'lib xabardor bo'lish
- 🚀 Majburiy obunasiz foydalanish

---

## 🚀 Railway'ga deploy qilish

### 1. Loyihani yuklang
Bu papkadagi barcha fayllarni GitHub repozitoriyangizga yuklang
(yoki Railway'da "Deploy from local" dan foydalaning).

### 2. Railway'da loyiha yarating
1. [railway.app](https://railway.app) ga kiring
2. **New Project** → **Deploy from GitHub repo** → repozitoriyani tanlang

### 3. PostgreSQL qo'shing
1. Loyiha ichida **+ New** → **Database** → **Add PostgreSQL**
2. Tayyor! `DATABASE_URL` avtomatik ulanadi (qo'lda yozish shart emas)

### 4. Environment Variables qo'shing
Loyiha → **Variables** bo'limiga kiring va qo'shing:

| O'zgaruvchi | Qiymat | Izoh |
|---|---|---|
| `BOT_TOKEN` | `123:AAxxx...` | @BotFather'dan olingan token |
| `ADMIN_IDS` | `123456789` | Sizning Telegram ID'ingiz (@userinfobot) |
| `PREMIUM_EMOJI` | `1` | Premium emoji (1=yoq, 0=oddiy) |

> 💡 Bir nechta admin: `ADMIN_IDS=111,222,333`

### 5. Deploy!
Railway avtomatik build qiladi va botni ishga tushiradi.
Loglarda `Bot ishga tushdi: @sizning_bot` ko'rinsa — tayyor! 🎉

---

## ⚙️ Muhim eslatmalar

### Premium emoji haqida
Premium (custom) emoji'lar **faqat bot egasida Telegram Premium bo'lsa**
yoki bot Fragment'da username sotib olgan bo'lsa ko'rinadi.
Aks holda Telegram avtomatik oddiy emojini ko'rsatadi — bot baribir ishlaydi.

**Tugma ranglari** (yashil/qizil/ko'k) esa hamma uchun ishlaydi.

### Emoji ID'larni tekshirish
Men emoji nomlarini mantiqan tanladim, lekin haqiqiy ko'rinishini
faqat siz ko'ra olasiz. Botda admin uchun maxsus buyruq bor:

```
/emoji                          → barcha emoji nomlari ro'yxati
/emoji 5767199127775481841      → o'sha ID emojisini ko'rsatadi
```

Agar biror emoji noto'g'ri bo'lsa, `emoji.py` faylida o'sha qatorni
o'zgartiring (ID'ni almashtiring).

### Majburiy obuna kanallari
Kanal qo'shishda **bot o'sha kanalda admin bo'lishi shart!**
- **Ommaviy** kanal: foydalanuvchi obuna bo'lishi kerak
- **Zayavkali** kanal: so'rov yuborsa bot avtomatik tasdiqlaydi

### Karta to'lovlari
Humo/Uzcard to'lovida foydalanuvchi chek (skrinshot) yuboradi →
chek admin lichkasiga keladi → admin **Tasdiqlash** tugmasini bosadi →
premium avtomatik faollashadi.

---

## 📂 Fayllar tuzilishi

```
kinobot/
├── main.py          # asosiy bot + barcha handlerlar
├── config.py        # sozlamalar (.env / Railway variables)
├── db.py            # PostgreSQL (asyncpg)
├── keyboards.py     # inline tugmalar (ranglar + emoji)
├── texts.py         # xabar matnlari
├── emoji.py         # premium emoji ID'lari
├── states.py        # FSM holatlari
├── requirements.txt # kerakli kutubxonalar
├── Procfile         # Railway uchun
├── railway.json     # Railway konfiguratsiyasi
└── .env.example     # namuna environment variables
```

---

## 🛠 Mahalliy (local) ishga tushirish

```bash
pip install -r requirements.txt

# .env fayl yarating (.env.example dan nusxa oling)
export BOT_TOKEN="123:AAxxx"
export ADMIN_IDS="123456789"
export DATABASE_URL="postgresql://user:pass@localhost:5432/kinobot"

python main.py
```

Bot **polling** rejimida ishlaydi (webhook shart emas).
