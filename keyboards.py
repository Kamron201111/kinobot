"""
═══════════════════════════════════════════════════════════════════
 INLINE KLAVIATURALAR
───────────────────────────────────────────────────────────────────
 Bot API 9.4:
   style = "primary" (ko'k) | "success" (yashil) | "danger" (qizil)
   icon_custom_emoji_id = premium emoji ID

 Premium emoji o'chiq bo'lsa — emoji tugma matni boshiga qo'shiladi.
═══════════════════════════════════════════════════════════════════
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import emoji as E


def btn(text: str, *, cb: str = "", url: str = "",
        emoji: str = "", style: str = "") -> InlineKeyboardButton:
    """
    Bitta tugma yaratuvchi.
      emoji  — emoji.py dagi kalit (masalan "movie")
      style  — "primary" | "success" | "danger"
    """
    kwargs: dict = {}
    label = text

    if emoji:
        cid = E.eid(emoji)
        if cid:
            kwargs["icon_custom_emoji_id"] = cid
        else:
            # premium o'chiq — oddiy emojini matnga qo'shamiz
            label = f"{E.raw(emoji)} {text}"

    if style:
        kwargs["style"] = style
    if cb:
        kwargs["callback_data"] = cb
    if url:
        kwargs["url"] = url

    return InlineKeyboardButton(text=label, **kwargs)


def kb(rows: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ═══════════════════════════════════════════════════════════════════
#  FOYDALANUVCHI — BOSH MENYU (4 ta asosiy tugma)
# ═══════════════════════════════════════════════════════════════════
def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    rows = [
        # 1-qator: Kino ko'rish (yashil) | Asosiy kanal (qizil)
        [btn("Kino ko'rish", cb="watch", emoji="movie", style="success"),
         btn("Asosiy kanal", cb="main_channel", emoji="channel", style="danger")],
        # 2-qator: Tarif sotib olish (ko'k) | Reklama
        [btn("Tarif sotib olish", cb="buy_premium", emoji="premium", style="primary"),
         btn("Reklama", cb="ads", emoji="megaphone")],
    ]
    if is_admin:
        rows.append([btn("Admin panel", cb="adm_main", emoji="admin", style="primary")])
    return kb(rows)


# ─── Kino ko'rish bo'limi ─────────────────────────────────────────
def watch_menu(movies_link: str | None) -> InlineKeyboardMarkup:
    rows = [
        [btn("Kino kodini kiritish", cb="enter_code", emoji="search", style="success")],
    ]
    if movies_link:
        rows.append([btn("Kinolar to'plami", url=movies_link, emoji="folder")])
    rows.append([btn("Orqaga", cb="back_main", emoji="back")])
    return kb(rows)


def back_to_watch() -> InlineKeyboardMarkup:
    return kb([[btn("Orqaga", cb="watch", emoji="back")]])


# ─── Premium / tarif bo'limi ──────────────────────────────────────
def premium_plans(prices: dict) -> InlineKeyboardMarkup:
    """prices = {'1d': '3000', '10d': '20000', '30d': '50000'}"""
    rows = [
        [btn(f"1 kunlik — {fmt(prices['1d'])} so'm", cb="plan_1d", emoji="clock", style="primary")],
        [btn(f"10 kunlik — {fmt(prices['10d'])} so'm", cb="plan_10d", emoji="star", style="primary")],
        [btn(f"30 kunlik — {fmt(prices['30d'])} so'm", cb="plan_30d", emoji="crown", style="primary")],
        [btn("Orqaga", cb="back_main", emoji="back")],
    ]
    return kb(rows)


def payment_methods(plan: str) -> InlineKeyboardMarkup:
    """To'lov usulini tanlash."""
    return kb([
        [btn("Humo", cb=f"pay_humo_{plan}", emoji="card", style="success")],
        [btn("Uzcard", cb=f"pay_uzcard_{plan}", emoji="card", style="primary")],
        [btn("Telegram Stars", cb=f"pay_stars_{plan}", emoji="star")],
        [btn("Orqaga", cb="buy_premium", emoji="back")],
    ])


def card_paid(plan: str, method: str) -> InlineKeyboardMarkup:
    """Karta orqali to'lagandan keyin chek yuborish."""
    return kb([
        [btn("To'lov qildim — chek yuborish", cb=f"sent_{method}_{plan}", emoji="check", style="success")],
        [btn("Bekor qilish", cb="buy_premium", emoji="cancel", style="danger")],
    ])


def premium_success() -> InlineKeyboardMarkup:
    return kb([
        [btn("Bosh menyu", cb="back_main", emoji="rocket", style="primary")],
    ])


# ─── Reklama bo'limi ──────────────────────────────────────────────
def ads_menu(admin_username: str | None) -> InlineKeyboardMarkup:
    rows = []
    if admin_username:
        rows.append([btn("Shartlarga roziman — bog'lanish",
                          url=f"https://t.me/{admin_username.lstrip('@')}",
                          emoji="check", style="success")])
    rows.append([btn("Orqaga", cb="back_main", emoji="back")])
    return kb(rows)


def back_main() -> InlineKeyboardMarkup:
    return kb([[btn("Bosh menyu", cb="back_main", emoji="back")]])


# ═══════════════════════════════════════════════════════════════════
#  MAJBURIY OBUNA (foydalanuvchiga)
# ═══════════════════════════════════════════════════════════════════
def subscribe_kb(channels: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for ch in channels:
        title = ch.get("title") or "Kanal"
        link = ch.get("link") or ""
        if link:
            rows.append([btn(title, url=link, emoji="channel")])
    rows.append([btn("Tekshirish", cb="check_subs", emoji="check", style="success")])
    return kb(rows)


# ═══════════════════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════════════════
def admin_main() -> InlineKeyboardMarkup:
    return kb([
        [btn("Kino qo'shish", cb="adm_add_movie", emoji="plus", style="success"),
         btn("Kino o'chirish", cb="adm_del_movie", emoji="trash", style="danger")],
        [btn("Statistika", cb="adm_stats", emoji="stats"),
         btn("Kinolar ro'yxati", cb="adm_movies", emoji="list")],
        [btn("Majburiy obuna", cb="adm_channels", emoji="channel", style="primary")],
        [btn("Premium narxlar", cb="adm_prices", emoji="money", style="primary"),
         btn("Karta sozlash", cb="adm_cards", emoji="card")],
        [btn("To'lov so'rovlari", cb="adm_payments", emoji="wallet"),
         btn("Premium a'zolar", cb="adm_prem_list", emoji="gem")],
        [btn("Linklar sozlash", cb="adm_links", emoji="link"),
         btn("Reklama sozlash", cb="adm_ads", emoji="megaphone")],
        [btn("Matnlarni tahrirlash", cb="adm_texts", emoji="edit", style="primary")],
        [btn("Adminlar", cb="adm_admins", emoji="users"),
         btn("Xabar yuborish", cb="adm_broadcast", emoji="send", style="primary")],
        [btn("Bot menyusiga", cb="back_main", emoji="back")],
    ])


def admin_back() -> InlineKeyboardMarkup:
    return kb([[btn("Admin panel", cb="adm_main", emoji="back")]])


def cancel_kb(back_cb: str = "adm_main") -> InlineKeyboardMarkup:
    return kb([[btn("Bekor qilish", cb=back_cb, emoji="cancel", style="danger")]])


# ─── Admin: matnlar ro'yxati (2 ustun) ────────────────────────────
def admin_texts(text_items: list[tuple]) -> InlineKeyboardMarkup:
    """text_items = [(key, label), ...] — 2 ustun qilib chiqaramiz."""
    rows = []
    row = []
    for key, label in text_items:
        row.append(btn(label, cb=f"txt_{key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([btn("Orqaga", cb="adm_main", emoji="back")])
    return kb(rows)


# ─── Admin: bitta matnni tahrirlash ───────────────────────────────
def text_edit(key: str) -> InlineKeyboardMarkup:
    return kb([
        [btn("Standartga qaytarish", cb=f"txtreset_{key}", emoji="back", style="danger")],
        [btn("Orqaga (bekor)", cb="adm_texts", emoji="cancel")],
    ])


def text_edit_done(key: str) -> InlineKeyboardMarkup:
    return kb([
        [btn("Yana tahrirlash", cb=f"txt_{key}", emoji="edit"),
         btn("Matnlar ro'yxati", cb="adm_texts", emoji="list")],
        [btn("Admin panel", cb="adm_main", emoji="back")],
    ])


# ─── Admin: majburiy kanallar ─────────────────────────────────────
def admin_channels(channels: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for ch in channels:
        jt = "🔓 ommaviy" if ch["join_type"] == "public" else "🔒 zayavkali"
        rows.append([
            btn(f"{ch['title']} ({jt})", url=ch["link"] or "https://t.me", emoji="channel"),
            btn("O'chirish", cb=f"adm_chdel_{ch['id']}", emoji="trash", style="danger"),
        ])
    rows.append([btn("Ommaviy qo'shish", cb="adm_chadd_public", emoji="plus", style="success")])
    rows.append([btn("Zayavkali qo'shish", cb="adm_chadd_request", emoji="lock", style="primary")])
    rows.append([btn("Orqaga", cb="adm_main", emoji="back")])
    return kb(rows)


# ─── Admin: narxlar ───────────────────────────────────────────────
def admin_prices(s: dict) -> InlineKeyboardMarkup:
    return kb([
        [btn(f"1 kun (karta): {fmt(s['price_1d'])} so'm", cb="adm_setp_1d", emoji="edit")],
        [btn(f"10 kun (karta): {fmt(s['price_10d'])} so'm", cb="adm_setp_10d", emoji="edit")],
        [btn(f"30 kun (karta): {fmt(s['price_30d'])} so'm", cb="adm_setp_30d", emoji="edit")],
        [btn(f"1 kun (Stars): {s['price_stars_1d']} ⭐", cb="adm_sets_1d", emoji="edit")],
        [btn(f"10 kun (Stars): {s['price_stars_10d']} ⭐", cb="adm_sets_10d", emoji="edit")],
        [btn(f"30 kun (Stars): {s['price_stars_30d']} ⭐", cb="adm_sets_30d", emoji="edit")],
        [btn("Orqaga", cb="adm_main", emoji="back")],
    ])


# ─── Admin: kartalar ──────────────────────────────────────────────
def admin_cards(s: dict) -> InlineKeyboardMarkup:
    humo = s.get("card_humo") or "kiritilmagan"
    uz = s.get("card_uzcard") or "kiritilmagan"
    return kb([
        [btn(f"Humo: {humo}", cb="adm_setcard_humo", emoji="card", style="success")],
        [btn(f"Humo egasi: {s.get('card_humo_name') or '—'}", cb="adm_setcard_humo_name", emoji="user")],
        [btn(f"Uzcard: {uz}", cb="adm_setcard_uzcard", emoji="card", style="primary")],
        [btn(f"Uzcard egasi: {s.get('card_uzcard_name') or '—'}", cb="adm_setcard_uzcard_name", emoji="user")],
        [btn("Orqaga", cb="adm_main", emoji="back")],
    ])


# ─── Admin: linklar ───────────────────────────────────────────────
def admin_links(s: dict) -> InlineKeyboardMarkup:
    main_c = s.get("main_channel") or "kiritilmagan"
    mov_c = s.get("movies_channel") or "kiritilmagan"
    return kb([
        [btn(f"Asosiy kanal: {main_c}", cb="adm_setlink_main", emoji="channel", style="danger")],
        [btn(f"Kinolar to'plami: {mov_c}", cb="adm_setlink_movies", emoji="folder")],
        [btn("Orqaga", cb="adm_main", emoji="back")],
    ])


# ─── Admin: reklama ───────────────────────────────────────────────
def admin_ads(s: dict) -> InlineKeyboardMarkup:
    adm = s.get("ads_admin") or "kiritilmagan"
    return kb([
        [btn("Reklama matnini o'zgartirish", cb="adm_set_ads_text", emoji="edit", style="primary")],
        [btn(f"Reklama admini: @{adm}", cb="adm_set_ads_admin", emoji="user")],
        [btn("Orqaga", cb="adm_main", emoji="back")],
    ])


# ─── Admin: adminlar ──────────────────────────────────────────────
def admin_admins(admins: list[int], owners: list[int]) -> InlineKeyboardMarkup:
    rows = []
    for aid in admins:
        is_owner = aid in owners
        if is_owner:
            rows.append([btn(f"👑 {aid} (asosiy)", cb="noop")])
        else:
            rows.append([
                btn(f"{aid}", cb="noop", emoji="user"),
                btn("O'chirish", cb=f"adm_deladm_{aid}", emoji="trash", style="danger"),
            ])
    rows.append([btn("Admin qo'shish", cb="adm_addadm", emoji="plus", style="success")])
    rows.append([btn("Orqaga", cb="adm_main", emoji="back")])
    return kb(rows)


# ─── Admin: broadcast turi ────────────────────────────────────────
def broadcast_target() -> InlineKeyboardMarkup:
    return kb([
        [btn("Hammaga", cb="bc_all", emoji="users", style="primary")],
        [btn("Faqat premium a'zolarga", cb="bc_premium", emoji="gem", style="success")],
        [btn("Orqaga", cb="adm_main", emoji="back")],
    ])


def broadcast_confirm() -> InlineKeyboardMarkup:
    return kb([
        [btn("Yuborish", cb="bc_send", emoji="send", style="success"),
         btn("Bekor qilish", cb="adm_main", emoji="cancel", style="danger")],
    ])


# ─── To'lov chekini admin tasdiqlashi ─────────────────────────────
def payment_review(pid: int) -> InlineKeyboardMarkup:
    return kb([
        [btn("Tasdiqlash", cb=f"pay_ok_{pid}", emoji="check", style="success"),
         btn("Rad etish", cb=f"pay_no_{pid}", emoji="cancel", style="danger")],
    ])


# ─── Yangi kino e'loni (premium a'zolarga) — ko'rish tugmasi ──────
def new_movie_announce(code: str) -> InlineKeyboardMarkup:
    return kb([[btn(f"Ko'rish — kod: {code}", cb=f"watch_code_{code}", emoji="play", style="success")]])


# ═══════════════════════════════════════════════════════════════════
#  YORDAMCHI
# ═══════════════════════════════════════════════════════════════════
def fmt(value) -> str:
    """Raqamni 50000 → 50 000 ko'rinishida formatlash."""
    try:
        n = int(str(value).replace(" ", ""))
        return f"{n:,}".replace(",", " ")
    except (TypeError, ValueError):
        return str(value)
