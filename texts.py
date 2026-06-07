"""
═══════════════════════════════════════════════════════════════════
 XABAR MATNLARI
───────────────────────────────────────────────────────────────────
 Matnlar bazadan o'qiladi (admin paneldan tahrirlanadi).
 Premium emoji yoqilgan bo'lsa, oddiy emoji'lar premium variantга
 avtomatik almashtiriladi (emoji.upgrade orqali).
═══════════════════════════════════════════════════════════════════
"""
import db
import emoji as E
from keyboards import fmt


def _render(raw: str) -> str:
    """Matndagi oddiy emoji'larni premium variantга almashtiradi (yoqilgan bo'lsa)."""
    return E.upgrade(raw)


async def welcome(name: str, is_premium: bool = False) -> str:
    raw = await db.get_text("welcome")
    raw = raw.replace("{name}", name)
    if is_premium:
        raw += await db.get_text("welcome_premium_badge")
    return _render(raw)


async def watch_intro() -> str:
    return _render(await db.get_text("watch_intro"))


async def ask_code() -> str:
    return _render(await db.get_text("ask_code"))


async def code_not_found(code: str) -> str:
    raw = (await db.get_text("code_not_found")).replace("{code}", code)
    return _render(raw)


async def premium_offer(prices: dict, stars: dict) -> str:
    raw = await db.get_text("premium_offer")
    raw = (raw
           .replace("{price_1d}", fmt(prices["1d"]))
           .replace("{price_10d}", fmt(prices["10d"]))
           .replace("{price_30d}", fmt(prices["30d"]))
           .replace("{stars_1d}", str(stars["1d"]))
           .replace("{stars_10d}", str(stars["10d"]))
           .replace("{stars_30d}", str(stars["30d"])))
    return _render(raw)


async def choose_method(plan_label: str, price_som: str, price_stars: str) -> str:
    raw = await db.get_text("choose_method")
    raw = (raw
           .replace("{plan}", plan_label)
           .replace("{price}", fmt(price_som))
           .replace("{stars}", str(price_stars)))
    return _render(raw)


async def card_instructions(method: str, card: str, name: str,
                            plan_label: str, price: str) -> str:
    method_name = "Humo" if method == "humo" else "Uzcard"
    raw = await db.get_text("card_instructions")
    raw = (raw
           .replace("{method}", method_name)
           .replace("{plan}", plan_label)
           .replace("{price}", fmt(price))
           .replace("{card}", card)
           .replace("{name}", name))
    return _render(raw)


async def send_receipt() -> str:
    return _render(await db.get_text("send_receipt"))


async def receipt_received() -> str:
    return _render(await db.get_text("receipt_received"))


async def premium_activated(until_str: str, days: int) -> str:
    raw = await db.get_text("premium_activated")
    raw = raw.replace("{days}", str(days)).replace("{until}", until_str)
    return _render(raw)


async def payment_rejected() -> str:
    return _render(await db.get_text("payment_rejected"))


async def main_channel_text(link: str | None) -> str:
    if not link:
        return _render("⚠️ Asosiy kanal hali sozlanmagan.")
    raw = (await db.get_text("main_channel")).replace("{link}", link)
    return _render(raw)


async def must_subscribe() -> str:
    return _render(await db.get_text("must_subscribe"))


async def still_not_subscribed() -> str:
    return _render(await db.get_text("still_not_subscribed"))


async def new_movie_for_premium(code: str, title: str, caption: str) -> str:
    cap = f"\n\n{caption}" if caption and caption != "-" else ""
    raw = await db.get_text("new_movie_for_premium")
    raw = (raw
           .replace("{title}", title)
           .replace("{code}", code)
           .replace("{caption}", cap))
    return _render(raw)


# ─── ADMIN matnlari (tahrirlanmaydigan, sobit) ────────────────────
def admin_welcome() -> str:
    return _render(
        "🛠 <b>Admin panel</b>\n\n"
        "Kerakli bo'limni tanlang:"
    )


def stats_text(s: dict) -> str:
    return _render(
        f"📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{s['total']}</b>\n"
        f"✅ Faol: <b>{s['active']}</b>\n\n"
        f"📈 <b>Bugun:</b>\n"
        f"• Qo'shildi: <b>+{s['joined_today']}</b>\n"
        f"• Tark etdi: <b>-{s['left_today']}</b>\n\n"
        f"🎬 Kinolar: <b>{s['movies']}</b>\n"
        f"💎 Premium a'zolar: <b>{s['premium']}</b>"
    )


def ask_movie_code() -> str:
    return _render(
        "🆕 <b>Yangi kino qo'shish (1/4)</b>\n\n"
        "Kino <b>kodini</b> yuboring (masalan: <code>123</code>):"
    )


def ask_movie_title() -> str:
    return _render("🎬 <b>(2/4)</b> Kino <b>nomini</b> yuboring:")


def ask_movie_caption() -> str:
    return _render(
        "📄 <b>(3/4)</b> Kino <b>tavsifini</b> yuboring.\n\n"
        "(Tavsif kerak bo'lmasa «<code>-</code>» yuboring)"
    )


def ask_movie_file() -> str:
    return _render(
        "▶️ <b>(4/4)</b> Endi kino <b>videosini</b> "
        "(yoki hujjat sifatida) yuboring:"
    )


def movie_added(code: str, premium_count: int) -> str:
    return _render(
        f"✅ <b>Kino qo'shildi!</b>\n\n"
        f"🎬 Kod: <code>{code}</code>\n"
        f"🔔 {premium_count} ta premium a'zoga xabar yuborilmoqda..."
    )
