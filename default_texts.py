"""
═══════════════════════════════════════════════════════════════════
 TAHRIRLANADIGAN MATNLAR
───────────────────────────────────────────────────────────────────
 Bu yerdagi har bir matn admin paneldan o'zgartirilishi mumkin.
 Bazaga "text_<key>" ko'rinishida saqlanadi.

 {...} ichidagi joylar — avtomatik to'ldiriladigan o'rinlar (placeholder).
 Ularni o'chirmang, aks holda ma'lumot ko'rinmaydi!
═══════════════════════════════════════════════════════════════════
"""

# Har bir matn: key -> (chiroyli_nom, standart_matn, [placeholderlar])
# Placeholder'lar foydalanuvchiga "bu joylarni saqlang" deb ko'rsatiladi.

TEXTS = {
    # ─── Bosh menyu / salomlashish ───
    "welcome": (
        "👋 Salomlashish (bosh menyu)",
        ("👋 Assalomu alaykum, <b>{name}</b>!\n\n"
         "🎬 <b>Kino botiga xush kelibsiz!</b>\n\n"
         "Bu yerda siz minglab kinolarni kod orqali topishingiz, "
         "premium a'zolikni rasmiylashtirishingiz va eng so'nggi "
         "yangiliklardan birinchilardan bo'lib xabardor bo'lishingiz mumkin.\n\n"
         "⬇️ Quyidagi tugmalardan birini tanlang:"),
        ["{name}"],
    ),
    "welcome_premium_badge": (
        "👑 Premium a'zo belgisi (salomga qo'shiladi)",
        "\n\n👑 <b>Siz Premium a'zosiz!</b>",
        [],
    ),

    # ─── Kino ko'rish ───
    "watch_intro": (
        "🎬 Kino ko'rish bo'limi",
        ("🎬 <b>Kino ko'rish</b>\n\n"
         "🔍 Kino kodini bilsangiz — «Kino kodini kiritish» tugmasini bosing.\n"
         "📁 Yoki barcha kinolar to'plamini ko'rib chiqing."),
        [],
    ),
    "ask_code": (
        "🔍 Kod so'rash matni",
        ("🔍 <b>Kino kodini yuboring</b>\n\n"
         "Masalan: <code>123</code>\n\n"
         "ℹ️ Kod kinoning tagida yoki kanalimizda ko'rsatilgan bo'ladi."),
        [],
    ),
    "code_not_found": (
        "❌ Kod topilmadi xabari",
        ("❌ <b>Kod topilmadi:</b> <code>{code}</code>\n\n"
         "Iltimos, kodni tekshirib qaytadan yuboring."),
        ["{code}"],
    ),

    # ─── Premium / tarif ───
    "premium_offer": (
        "💎 Premium taklif matni",
        ("💎 <b>Premium tarif</b>\n\n"
         "Premium a'zolik sizga quyidagilarni beradi:\n\n"
         "🔔 Yangi kinolardan birinchi bo'lib xabardor bo'lasiz\n"
         "🚀 Majburiy obunalarsiz tezkor foydalanish\n"
         "⭐️ Maxsus imkoniyatlar\n\n"
         "💰 <b>Narxlar:</b>\n"
         "• 1 kun — {price_1d} so'm / {stars_1d} ⭐\n"
         "• 10 kun — {price_10d} so'm / {stars_10d} ⭐\n"
         "• 30 kun — {price_30d} so'm / {stars_30d} ⭐\n\n"
         "⬇️ Muddatni tanlang:"),
        ["{price_1d}", "{price_10d}", "{price_30d}", "{stars_1d}", "{stars_10d}", "{stars_30d}"],
    ),
    "choose_method": (
        "🎟 To'lov usulini tanlash matni",
        ("🎟 <b>Tanlangan tarif:</b> {plan}\n\n"
         "💰 Narx: <b>{price} so'm</b> yoki <b>{stars} ⭐</b>\n\n"
         "💳 To'lov usulini tanlang:"),
        ["{plan}", "{price}", "{stars}"],
    ),
    "card_instructions": (
        "💳 Karta orqali to'lov ko'rsatmasi",
        ("💳 <b>{method} orqali to'lov</b>\n\n"
         "🎟 Tarif: {plan}\n"
         "💰 Summa: <b>{price} so'm</b>\n\n"
         "👛 Karta raqami:\n"
         "<code>{card}</code>\n"
         "👤 Egasi: <b>{name}</b>\n\n"
         "⚠️ To'lovni amalga oshirgach, <b>chek (skrinshot)</b>ni yuboring. "
         "Admin tekshirib, premium faollashtiradi.\n\n"
         "⬇️ To'lagandan so'ng tugmani bosing:"),
        ["{method}", "{plan}", "{price}", "{card}", "{name}"],
    ),
    "send_receipt": (
        "📤 Chek yuborishni so'rash",
        ("📤 <b>Chekni yuboring</b>\n\n"
         "To'lov chekining rasmini (skrinshot) shu yerga yuboring.\n"
         "⏰ Admin imkon qadar tez tekshiradi."),
        [],
    ),
    "receipt_received": (
        "✅ Chek qabul qilindi xabari",
        ("✅ <b>Chek qabul qilindi!</b>\n\n"
         "⏰ Admin tekshirmoqda. Tasdiqlangach, sizga xabar keladi."),
        [],
    ),
    "premium_activated": (
        "👑 Premium faollashtirildi xabari",
        ("👑 <b>Tabriklaymiz! Premium faollashtirildi!</b>\n\n"
         "⭐️ Muddat: <b>{days} kun</b>\n"
         "⏰ Amal qiladi: <b>{until}</b> gacha\n\n"
         "🔔 Endi siz yangi kinolardan birinchi bo'lib xabardor bo'lasiz!"),
        ["{days}", "{until}"],
    ),
    "payment_rejected": (
        "❌ To'lov rad etildi xabari",
        ("❌ <b>To'lov tasdiqlanmadi</b>\n\n"
         "Chek noto'g'ri yoki to'lov topilmadi. Iltimos, admin bilan bog'laning."),
        [],
    ),

    # ─── Asosiy kanal ───
    "main_channel": (
        "📢 Asosiy kanal matni",
        ("📢 <b>Asosiy kanalimiz</b>\n\n"
         "Barcha yangiliklar va e'lonlar shu yerda:\n{link}"),
        ["{link}"],
    ),

    # ─── Majburiy obuna ───
    "must_subscribe": (
        "🔒 Majburiy obuna matni",
        ("🔒 <b>Botdan foydalanish uchun obuna bo'ling</b>\n\n"
         "Quyidagi kanal(lar)ga obuna bo'ling. Zayavkali kanallarga "
         "so'rov yuborsangiz ham yetarli.\n\n"
         "✅ So'ng «Tekshirish» tugmasini bosing."),
        [],
    ),
    "still_not_subscribed": (
        "❌ Hali obuna bo'lmadi xabari",
        ("❌ Siz hali barcha kanallarga obuna bo'lmadingiz.\n\n"
         "Iltimos, obuna bo'lib qaytadan «Tekshirish» tugmasini bosing."),
        [],
    ),

    # ─── Yangi kino e'loni (premium) ───
    "new_movie_for_premium": (
        "🆕 Premium a'zolarga yangi kino e'loni",
        ("🆕 <b>Yangi kino qo'shildi!</b>\n\n"
         "🎬 <b>{title}</b>\n"
         "🆔 Kod: <code>{code}</code>{caption}\n\n"
         "👑 <i>Siz buni Premium a'zo sifatida birinchilardan ko'rdingiz!</i>"),
        ["{title}", "{code}", "{caption}"],
    ),
}


def default_text(key: str) -> str:
    """Standart matnni qaytaradi."""
    item = TEXTS.get(key)
    return item[1] if item else ""
