"""
═══════════════════════════════════════════════════════════════════
 PREMIUM EMOJI moduli
───────────────────────────────────────────────────────────────────
 Telegram Bot API 9.4:
   • Xabarlarda:  <tg-emoji emoji-id="ID">fallback</tg-emoji>
   • Tugmalarda:  InlineKeyboardButton(..., custom_emoji_id="ID")

 ESLATMA: premium (custom) emoji faqat bot EGASI Telegram Premium
 bo'lsa yoki bot Fragment'da username sotib olgan bo'lsa ko'rinadi.
 Aks holda Telegram avtomatik ravishda fallback (oddiy) emojini
 ko'rsatadi — ya'ni bot baribir to'g'ri ishlaydi.

 ID'lar foydalanuvchi bergan to'plamlardan tanlab olingan. Agar
 biror ID mos kelmasa, pastdagi lug'atdan o'zgartirish kifoya.
═══════════════════════════════════════════════════════════════════
"""
from config import PREMIUM_EMOJI_ENABLED

# ─── Maqsadli emoji → (custom_emoji_id, oddiy_fallback) ───────────
#  Har bir kalit botning ma'lum bir joyida ishlatiladi.
EMOJI = {
    # umumiy / salomlashish
    "wave":     ("5773677501825945508", "👋"),
    "fire":     ("6028346797368283073", "🔥"),
    "sparkle":  ("5775870512127283512", "✨"),
    "rocket":   ("5904258298764334001", "🚀"),
    "star":     ("5850309953293653168", "⭐️"),
    "crown":    ("5850332476102153487", "👑"),
    "diamond":  ("5850392884817172292", "💎"),

    # kino / media
    "movie":    ("5767199127775481841", "🎬"),
    "clapper":  ("5942734685976138521", "🎬"),
    "popcorn":  ("6035162669948867129", "🍿"),
    "film":     ("6032742198179532882", "🎞"),
    "tv":       ("5924722061288150929", "📺"),
    "play":     ("5776424837786374634", "▶️"),
    "search":   ("5771449289972650710", "🔍"),
    "folder":   ("5895519358871932592", "📁"),

    # kanal / reklama
    "megaphone":("6039422865189638057", "📣"),
    "channel":  ("6030776052345737530", "📢"),
    "link":     ("5895534923833413814", "🔗"),
    "ad":       ("5893444447286334441", "📣"),
    "pin":      ("5886437972647088483", "📌"),

    # to'lov / premium
    "money":    ("5893236738372932548", "💰"),
    "card":     ("5893057118545646106", "💳"),
    "wallet":   ("5920046907782074235", "👛"),
    "premium":  ("5951802070607597636", "💎"),
    "gem":      ("5922693616953725714", "💎"),
    "gift":     ("5773626993010546707", "🎁"),
    "tariff":   ("5766994197705921104", "🎟"),

    # holatlar
    "ok":       ("5774022692642492953", "✅"),
    "check":    ("5774077015388852135", "✅"),
    "cross":    ("5774034804450267485", "❌"),
    "warn":     ("5893316448670978477", "⚠️"),
    "clock":    ("5778420863707649338", "⏰"),
    "hourglass":("5773677501825945508", "⏳"),
    "bell":     ("5960671702059848143", "🔔"),
    "lock":     ("6030657343744644592", "🔒"),
    "key":      ("5938437708635443119", "🔑"),

    # profil / admin / odamlar
    "user":     ("6035084557378654059", "👤"),
    "users":    ("5938196735200333756", "👥"),
    "admin":    ("6028435952299413210", "🛠"),
    "settings": ("6028171274939797252", "⚙️"),
    "stats":    ("5904219717073114606", "📊"),
    "chart":    ("6034969813032374911", "📈"),
    "id":       ("5774022692642492953", "🆔"),
    "people":   ("6030848053177486888", "👥"),

    # navigatsiya
    "back":     ("6039539366177541657", "⬅️"),
    "cancel":   ("5774034804450267485", "❌"),
    "edit":     ("5766915217552315762", "✏️"),
    "plus":     ("6037496202990194718", "➕"),
    "trash":    ("6037249452824072506", "🗑"),
    "send":     ("5895383238473421210", "📤"),
    "down":     ("6030466823290360017", "⬇️"),
    "right":    ("6035128606563241721", "➡️"),
    "info":     ("5895364284782743985", "ℹ️"),
    "doc":      ("5769289093221454192", "📄"),
    "new":      ("6037622221625626773", "🆕"),
    "list":     ("6030400221232501136", "📋"),
}


def _on() -> bool:
    """Premium emoji yoqilganmi? (admin OFF qiloladi — pastda override bor)."""
    return PREMIUM_EMOJI_ENABLED


# Run-time'da admin tomonidan o'zgartirilishi mumkin (main.py o'rnatadi)
_runtime_enabled = {"value": PREMIUM_EMOJI_ENABLED}


def set_enabled(flag: bool) -> None:
    _runtime_enabled["value"] = bool(flag)


def is_enabled() -> bool:
    return _runtime_enabled["value"]


def e(name: str) -> str:
    """
    Xabar matni uchun premium emoji HTML.
    Premium o'chirilgan bo'lsa — faqat oddiy emoji qaytadi.
    """
    eid, fb = EMOJI.get(name, ("", "•"))
    if is_enabled() and eid:
        return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>'
    return fb


def raw(name: str) -> str:
    """Faqat oddiy (fallback) emoji — premiumsiz joylar uchun."""
    return EMOJI.get(name, ("", "•"))[1]


def eid(name: str) -> str | None:
    """
    Tugma uchun custom_emoji_id (premium yoqilgan bo'lsa).
    Aks holda None — bu holda oddiy emoji tugma matniga qo'shiladi.
    """
    if not is_enabled():
        return None
    return EMOJI.get(name, ("", ""))[0] or None


# ─── Oddiy emoji → premium ID xaritasi (teskari) ──────────────────
#  Matn ichidagi oddiy emoji'larni premium variantга almashtirish uchun.
#  Bir xil fallback'li bir nechta nom bo'lsa, birinchisi olinadi.
_FALLBACK_TO_ID: dict[str, str] = {}
for _name, (_eid, _fb) in EMOJI.items():
    if _fb and _fb not in _FALLBACK_TO_ID and _eid:
        _FALLBACK_TO_ID[_fb] = _eid


def upgrade(text: str) -> str:
    """
    Matndagi tanish oddiy emoji'larni premium <tg-emoji> ga almashtiradi.
    Premium o'chiq bo'lsa — matn o'zgarmaydi (oddiy emoji qoladi).
    Allaqachon <tg-emoji ...> bor bo'lsa — qayta o'ramaslik uchun tegmaydi.
    """
    if not is_enabled() or not text:
        return text
    # agar matnda allaqachon premium emoji bo'lsa, ikki marta o'ramaymiz
    if "<tg-emoji" in text:
        return text
    # uzunroq emoji'lar oldin almashtirilishi uchun uzunligi bo'yicha saralaymiz
    for fb in sorted(_FALLBACK_TO_ID.keys(), key=len, reverse=True):
        if fb in text:
            eid_ = _FALLBACK_TO_ID[fb]
            text = text.replace(fb, f'<tg-emoji emoji-id="{eid_}">{fb}</tg-emoji>')
    return text
