"""
═══════════════════════════════════════════════════════════════════
 XABAR MATNLARI (premium emoji bilan)
═══════════════════════════════════════════════════════════════════
"""
import emoji as E
from keyboards import fmt


def welcome(name: str, is_premium: bool = False) -> str:
    badge = f"\n\n{E.e('crown')} <b>Siz Premium a'zosiz!</b>" if is_premium else ""
    return (
        f"{E.e('wave')} Assalomu alaykum, <b>{name}</b>!\n\n"
        f"{E.e('movie')} <b>Kino botiga xush kelibsiz!</b>\n\n"
        f"Bu yerda siz minglab kinolarni kod orqali topishingiz, "
        f"premium a'zolikni rasmiylashtirishingiz va eng so'nggi "
        f"yangiliklardan birinchilardan bo'lib xabardor bo'lishingiz mumkin.\n\n"
        f"{E.e('down')} Quyidagi tugmalardan birini tanlang:"
        f"{badge}"
    )


def watch_intro() -> str:
    return (
        f"{E.e('movie')} <b>Kino ko'rish</b>\n\n"
        f"{E.e('search')} Kino kodini bilsangiz — «Kino kodini kiritish» tugmasini bosing.\n"
        f"{E.e('folder')} Yoki barcha kinolar to'plamini ko'rib chiqing."
    )


def ask_code() -> str:
    return (
        f"{E.e('search')} <b>Kino kodini yuboring</b>\n\n"
        f"Masalan: <code>123</code>\n\n"
        f"{E.e('info')} Kod kinoning tagida yoki kanalimizda ko'rsatilgan bo'ladi."
    )


def code_not_found(code: str) -> str:
    return (
        f"{E.e('cross')} <b>Kod topilmadi:</b> <code>{code}</code>\n\n"
        f"Iltimos, kodni tekshirib qaytadan yuboring."
    )


def premium_offer(prices: dict, stars: dict) -> str:
    return (
        f"{E.e('premium')} <b>Premium tarif</b>\n\n"
        f"Premium a'zolik sizga quyidagilarni beradi:\n\n"
        f"{E.e('bell')} Yangi kinolardan birinchi bo'lib xabardor bo'lasiz\n"
        f"{E.e('rocket')} Majburiy obunalarsiz tezkor foydalanish\n"
        f"{E.e('star')} Maxsus imkoniyatlar\n\n"
        f"{E.e('money')} <b>Narxlar:</b>\n"
        f"• 1 kun — {fmt(prices['1d'])} so'm / {stars['1d']} ⭐\n"
        f"• 10 kun — {fmt(prices['10d'])} so'm / {stars['10d']} ⭐\n"
        f"• 30 kun — {fmt(prices['30d'])} so'm / {stars['30d']} ⭐\n\n"
        f"{E.e('down')} Muddatni tanlang:"
    )


def choose_method(plan_label: str, price_som: str, price_stars: str) -> str:
    return (
        f"{E.e('tariff')} <b>Tanlangan tarif:</b> {plan_label}\n\n"
        f"{E.e('money')} Narx: <b>{fmt(price_som)} so'm</b> yoki <b>{price_stars} ⭐</b>\n\n"
        f"{E.e('card')} To'lov usulini tanlang:"
    )


def card_instructions(method: str, card: str, name: str,
                       plan_label: str, price: str) -> str:
    method_name = "Humo" if method == "humo" else "Uzcard"
    return (
        f"{E.e('card')} <b>{method_name} orqali to'lov</b>\n\n"
        f"{E.e('tariff')} Tarif: {plan_label}\n"
        f"{E.e('money')} Summa: <b>{fmt(price)} so'm</b>\n\n"
        f"{E.e('wallet')} Karta raqami:\n"
        f"<code>{card}</code>\n"
        f"{E.e('user')} Egasi: <b>{name}</b>\n\n"
        f"{E.e('warn')} To'lovni amalga oshirgach, <b>chek (skrinshot)</b>ni yuboring. "
        f"Admin tekshirib, premium faollashtiradi.\n\n"
        f"{E.e('down')} To'lagandan so'ng tugmani bosing:"
    )


def send_receipt() -> str:
    return (
        f"{E.e('send')} <b>Chekni yuboring</b>\n\n"
        f"To'lov chekining rasmini (skrinshot) shu yerga yuboring.\n"
        f"{E.e('clock')} Admin imkon qadar tez tekshiradi."
    )


def receipt_received() -> str:
    return (
        f"{E.e('check')} <b>Chek qabul qilindi!</b>\n\n"
        f"{E.e('clock')} Admin tekshirmoqda. Tasdiqlangach, sizga xabar keladi."
    )


def premium_activated(until_str: str, days: int) -> str:
    return (
        f"{E.e('crown')} <b>Tabriklaymiz! Premium faollashtirildi!</b>\n\n"
        f"{E.e('star')} Muddat: <b>{days} kun</b>\n"
        f"{E.e('clock')} Amal qiladi: <b>{until_str}</b> gacha\n\n"
        f"{E.e('bell')} Endi siz yangi kinolardan birinchi bo'lib xabardor bo'lasiz!"
    )


def main_channel_text(link: str | None) -> str:
    if not link:
        return f"{E.e('warn')} Asosiy kanal hali sozlanmagan."
    return (
        f"{E.e('channel')} <b>Asosiy kanalimiz</b>\n\n"
        f"Barcha yangiliklar va e'lonlar shu yerda:\n{link}"
    )


def must_subscribe() -> str:
    return (
        f"{E.e('lock')} <b>Botdan foydalanish uchun obuna bo'ling</b>\n\n"
        f"Quyidagi kanal(lar)ga obuna bo'ling. Zayavkali kanallarga "
        f"so'rov yuborsangiz ham yetarli.\n\n"
        f"{E.e('check')} So'ng «Tekshirish» tugmasini bosing."
    )


def still_not_subscribed() -> str:
    return (
        f"{E.e('cross')} Siz hali barcha kanallarga obuna bo'lmadingiz.\n\n"
        f"Iltimos, obuna bo'lib qaytadan «Tekshirish» tugmasini bosing."
    )


# ─── ADMIN matnlari ───────────────────────────────────────────────
def admin_welcome() -> str:
    return (
        f"{E.e('admin')} <b>Admin panel</b>\n\n"
        f"Kerakli bo'limni tanlang:"
    )


def stats_text(s: dict) -> str:
    return (
        f"{E.e('stats')} <b>Statistika</b>\n\n"
        f"{E.e('users')} Jami foydalanuvchilar: <b>{s['total']}</b>\n"
        f"{E.e('check')} Faol: <b>{s['active']}</b>\n\n"
        f"{E.e('chart')} <b>Bugun:</b>\n"
        f"• Qo'shildi: <b>+{s['joined_today']}</b>\n"
        f"• Tark etdi: <b>-{s['left_today']}</b>\n\n"
        f"{E.e('movie')} Kinolar: <b>{s['movies']}</b>\n"
        f"{E.e('gem')} Premium a'zolar: <b>{s['premium']}</b>"
    )


def ask_movie_code() -> str:
    return (
        f"{E.e('new')} <b>Yangi kino qo'shish (1/4)</b>\n\n"
        f"Kino <b>kodini</b> yuboring (masalan: <code>123</code>):"
    )


def ask_movie_title() -> str:
    return f"{E.e('movie')} <b>(2/4)</b> Kino <b>nomini</b> yuboring:"


def ask_movie_caption() -> str:
    return (
        f"{E.e('doc')} <b>(3/4)</b> Kino <b>tavsifini</b> yuboring.\n\n"
        f"(Tavsif kerak bo'lmasa «<code>-</code>» yuboring)"
    )


def ask_movie_file() -> str:
    return (
        f"{E.e('play')} <b>(4/4)</b> Endi kino <b>videosini</b> "
        f"(yoki hujjat sifatida) yuboring:"
    )


def movie_added(code: str, premium_count: int) -> str:
    return (
        f"{E.e('check')} <b>Kino qo'shildi!</b>\n\n"
        f"{E.e('movie')} Kod: <code>{code}</code>\n"
        f"{E.e('bell')} {premium_count} ta premium a'zoga xabar yuborilmoqda..."
    )


def new_movie_for_premium(code: str, title: str, caption: str) -> str:
    cap = f"\n\n{caption}" if caption and caption != "-" else ""
    return (
        f"{E.e('new')} <b>Yangi kino qo'shildi!</b>\n\n"
        f"{E.e('movie')} <b>{title}</b>\n"
        f"{E.e('id')} Kod: <code>{code}</code>{cap}\n\n"
        f"{E.e('crown')} <i>Siz buni Premium a'zo sifatida birinchilardan ko'rdingiz!</i>"
    )
