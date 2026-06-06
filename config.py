"""
═══════════════════════════════════════════════════════════════════
 KINO BOT — Sozlamalar (.env / Railway environment variables)
═══════════════════════════════════════════════════════════════════
"""
import os
from typing import List


def _env(key: str, default: str = "") -> str:
    v = os.getenv(key, "")
    return v.strip() if v and v.strip() else default


def _env_int(key: str, default: int = 0) -> int:
    try:
        return int(_env(key, str(default)))
    except (TypeError, ValueError):
        return default


def _env_ids(key: str) -> List[int]:
    raw = _env(key, "")
    out: List[int] = []
    for part in raw.replace(" ", "").split(","):
        if part.isdigit() or (part.startswith("-") and part[1:].isdigit()):
            out.append(int(part))
    return out


# ─── Bot ───────────────────────────────────────────────────────────
BOT_TOKEN: str = _env("BOT_TOKEN")

# ─── Adminlar (vergul bilan ajratilgan ID'lar) ─────────────────────
#  Bu .env dagi "asosiy" adminlar. Qo'shimcha adminlar bazada saqlanadi.
OWNER_IDS: List[int] = _env_ids("ADMIN_IDS")

# ─── Ma'lumotlar bazasi (Railway PostgreSQL) ──────────────────────
#  Railway "DATABASE_URL" ni avtomatik beradi.
DATABASE_URL: str = _env("DATABASE_URL")

# ─── Webhook (ixtiyoriy — agar webhook rejimi kerak bo'lsa) ────────
#  Bo'sh bo'lsa bot "polling" rejimida ishlaydi (Railway uchun ham mos).
WEBHOOK_HOST: str = _env("WEBHOOK_HOST")            # masalan: https://xxx.up.railway.app
WEBHOOK_PATH: str = _env("WEBHOOK_PATH", "/webhook")
WEBHOOK_SECRET: str = _env("WEBHOOK_SECRET", "kino_secret")
WEBAPP_PORT: int = _env_int("PORT", 8080)          # Railway PORT ni beradi

USE_WEBHOOK: bool = bool(WEBHOOK_HOST)

# ─── Boshlang'ich (default) qiymatlar — keyin admin panelda o'zgaradi ──
#  Bular faqat baza birinchi marta yaratilganda ishlatiladi.
DEFAULT_SETTINGS = {
    # Premium narxlari (so'mda) — admin panelda o'zgartiriladi
    "price_1d": "3000",
    "price_10d": "20000",
    "price_30d": "50000",
    # Stars narxlari (XTR) — admin panelda o'zgartiriladi
    "price_stars_1d": "30",
    "price_stars_10d": "200",
    "price_stars_30d": "450",
    # To'lov kartalari
    "card_humo": "",
    "card_humo_name": "",
    "card_uzcard": "",
    "card_uzcard_name": "",
    # Kanallar / linklar
    "main_channel": "",          # @username yoki link — "Asosiy kanal" tugmasi
    "movies_channel": "",        # @username yoki link — "Kinolar to'plami"
    # Reklama
    "ads_text": (
        "📣 <b>Reklama va hamkorlik</b>\n\n"
        "Bizning bot orqali quyidagi xizmatlardan foydalanishingiz mumkin:\n\n"
        "• Kanal / guruh reklamasi\n"
        "• Post joylashtirish\n"
        "• Doimiy hamkorlik\n\n"
        "<b>Qoidalar:</b>\n"
        "1. Reklama mazmuni qonuniy bo'lishi shart\n"
        "2. Aldamchi loyihalar qabul qilinmaydi\n"
        "3. Narx kelishilgan holda belgilanadi\n\n"
        "Shartlar ma'qul bo'lsa, quyidagi tugmani bosing 👇"
    ),
    "ads_admin": "",             # reklama uchun admin username (@ siz)
}

# ─── Boshlang'ich emoji o'rni — keyin "premium emoji ON/OFF" admin sozlamasi ──
#  True bo'lsa botda premium custom emoji ishlatiladi (egasi Premium bo'lishi kerak).
PREMIUM_EMOJI_ENABLED: bool = _env("PREMIUM_EMOJI", "1") not in ("0", "false", "False", "")
