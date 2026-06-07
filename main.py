"""
═══════════════════════════════════════════════════════════════════
 KINO BOT — asosiy fayl (aiogram 3.x)
───────────────────────────────────────────────────────────────────
 • Bot API 9.4: rangli tugmalar (style) + premium emoji
 • PostgreSQL (Railway)
 • Polling yoki Webhook rejimi
═══════════════════════════════════════════════════════════════════
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery, ChatJoinRequest, ChatMemberUpdated, LabeledPrice,
    Message, PreCheckoutQuery,
)

import db
import emoji as E
import keyboards as K
import texts as T
from config import (BOT_TOKEN, OWNER_IDS, USE_WEBHOOK, WEBAPP_PORT,
                    WEBHOOK_HOST, WEBHOOK_PATH, WEBHOOK_SECRET)
from keyboards import fmt
from default_texts import TEXTS as DEFAULT_TEXTS
from states import (AdminSt, AdsSt, BroadcastSt, CardSt, ChannelSt, LinkSt,
                    MovieSt, PriceSt, TextSt, UserSt)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("kinobot")

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Plan yorliqlari
PLAN_LABELS = {"1d": "1 kunlik", "10d": "10 kunlik", "30d": "30 kunlik"}
PLAN_DAYS = {"1d": 1, "10d": 10, "30d": 30}


# ═══════════════════════════════════════════════════════════════════
#  YORDAMCHI FUNKSIYALAR
# ═══════════════════════════════════════════════════════════════════
async def safe_edit(cb: CallbackQuery, text: str, markup=None):
    """Xabarni tahrirlash (xatolarga chidamli)."""
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest:
        try:
            await cb.message.answer(text, reply_markup=markup)
        except TelegramBadRequest:
            pass


async def get_prices() -> dict:
    s = await db.all_settings()
    return {"1d": s["price_1d"], "10d": s["price_10d"], "30d": s["price_30d"]}


async def get_stars() -> dict:
    s = await db.all_settings()
    return {"1d": s["price_stars_1d"], "10d": s["price_stars_10d"], "30d": s["price_stars_30d"]}


async def notify_admins(text: str, markup=None, photo: str | None = None):
    """Barcha adminlarga xabar yuborish."""
    for aid in await db.list_admins():
        try:
            if photo:
                await bot.send_photo(aid, photo, caption=text, reply_markup=markup)
            else:
                await bot.send_message(aid, text, reply_markup=markup)
        except (TelegramForbiddenError, TelegramBadRequest):
            continue


# ─── Majburiy obuna tekshiruvi ────────────────────────────────────
async def get_unsubscribed(user_id: int) -> list[dict]:
    """Foydalanuvchi obuna bo'lmagan kanallar ro'yxati."""
    channels = await db.list_channels()
    not_subbed = []
    for ch in channels:
        chat_id = ch["chat_id"]
        # zayavkali kanal: so'rov yuborgan bo'lsa — yetarli
        if ch["join_type"] == "request":
            if await db.has_join_request(user_id, chat_id):
                continue
        # a'zolikni tekshirish
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status in ("left", "kicked"):
                not_subbed.append(ch)
        except TelegramBadRequest:
            # bot kanalda admin emas yoki chat topilmadi — o'tkazib yuboramiz
            continue
        except Exception:
            not_subbed.append(ch)
    return not_subbed


async def require_subscription(user_id: int) -> bool:
    """True = obuna to'liq. False = obuna kerak (xabar foydalanuvchiga yuboriladi)."""
    # premium a'zolar uchun majburiy obuna yo'q
    if await db.is_premium(user_id):
        return True
    not_subbed = await get_unsubscribed(user_id)
    return len(not_subbed) == 0


# ═══════════════════════════════════════════════════════════════════
#  /START
# ═══════════════════════════════════════════════════════════════════
@dp.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    user = msg.from_user
    is_new = await db.upsert_user(user.id, user.username, user.first_name)

    if await db.is_banned(user.id):
        await msg.answer(f"{E.e('cross')} Siz bloklangansiz.")
        return

    # majburiy obuna
    if not await require_subscription(user.id):
        not_subbed = await get_unsubscribed(user.id)
        await msg.answer(await T.must_subscribe(), reply_markup=K.subscribe_kb(not_subbed))
        return

    is_admin = await db.is_admin(user.id)
    is_prem = await db.is_premium(user.id)
    await msg.answer(
        await T.welcome(user.first_name or "do'stim", is_prem),
        reply_markup=K.main_menu(is_admin),
    )


# ─── Bosh menyuga qaytish ─────────────────────────────────────────
@dp.callback_query(F.data == "back_main")
async def cb_back_main(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    is_admin = await db.is_admin(cb.from_user.id)
    is_prem = await db.is_premium(cb.from_user.id)
    await safe_edit(cb, await T.welcome(cb.from_user.first_name or "do'stim", is_prem),
                    K.main_menu(is_admin))
    await cb.answer()


# ═══════════════════════════════════════════════════════════════════
#  MAJBURIY OBUNA — tekshirish
# ═══════════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "check_subs")
async def cb_check_subs(cb: CallbackQuery, state: FSMContext):
    if await require_subscription(cb.from_user.id):
        is_admin = await db.is_admin(cb.from_user.id)
        is_prem = await db.is_premium(cb.from_user.id)
        await safe_edit(cb, await T.welcome(cb.from_user.first_name or "do'stim", is_prem),
                        K.main_menu(is_admin))
        await cb.answer("✅ Obuna tasdiqlandi!", show_alert=False)
    else:
        not_subbed = await get_unsubscribed(cb.from_user.id)
        await safe_edit(cb, await T.still_not_subscribed(), K.subscribe_kb(not_subbed))
        await cb.answer("❌ Hali obuna bo'lmagansiz", show_alert=True)


# ─── Zayavka (join request) kelganda ──────────────────────────────
@dp.chat_join_request()
async def on_join_request(req: ChatJoinRequest):
    """
    Zayavkali kanal/guruhga so'rov kelганда:
      • avto tasdiqlaymiz (yoki shunchaki yozib qo'yamiz)
      • foydalanuvchini majburiy obuna uchun "obuna bo'lgan" deb belgilaymiz
    """
    chat_id = str(req.chat.id)
    await db.save_join_request(req.user_chat_id, chat_id)
    # avtomatik tasdiqlash
    try:
        await bot.approve_chat_join_request(req.chat.id, req.from_user.id)
    except TelegramBadRequest:
        pass


# ─── Bot bloklanganini aniqlash ───────────────────────────────────
@dp.my_chat_member()
async def on_my_chat_member(upd: ChatMemberUpdated):
    if upd.chat.type == "private":
        new_status = upd.new_chat_member.status
        if new_status in ("kicked", "left"):
            await db.mark_left(upd.from_user.id)
        elif new_status == "member":
            await db.upsert_user(upd.from_user.id, upd.from_user.username,
                                 upd.from_user.first_name)


# ═══════════════════════════════════════════════════════════════════
#  1) KINO KO'RISH
# ═══════════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "watch")
async def cb_watch(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    if not await require_subscription(cb.from_user.id):
        not_subbed = await get_unsubscribed(cb.from_user.id)
        await safe_edit(cb, await T.must_subscribe(), K.subscribe_kb(not_subbed))
        await cb.answer()
        return
    s = await db.all_settings()
    movies_link = s.get("movies_channel") or None
    await safe_edit(cb, await T.watch_intro(), K.watch_menu(movies_link))
    await cb.answer()


@dp.callback_query(F.data == "enter_code")
async def cb_enter_code(cb: CallbackQuery, state: FSMContext):
    await state.set_state(UserSt.waiting_code)
    await safe_edit(cb, await T.ask_code(), K.back_to_watch())
    await cb.answer()


@dp.message(UserSt.waiting_code, F.text)
async def on_code(msg: Message, state: FSMContext):
    code = msg.text.strip()
    movie = await db.get_movie(code)
    if not movie:
        await msg.answer(await T.code_not_found(code), reply_markup=K.back_to_watch())
        return
    await state.clear()
    await send_movie(msg.chat.id, movie)


async def send_movie(chat_id: int, movie: dict):
    """Kinoni yuborish."""
    caption = ""
    if movie.get("title"):
        caption += f"{E.e('movie')} <b>{movie['title']}</b>\n"
    caption += f"{E.e('id')} Kod: <code>{movie['code']}</code>"
    if movie.get("caption") and movie["caption"] != "-":
        caption += f"\n\n{movie['caption']}"
    try:
        if movie["file_type"] == "document":
            await bot.send_document(chat_id, movie["file_id"], caption=caption)
        else:
            await bot.send_video(chat_id, movie["file_id"], caption=caption)
    except TelegramBadRequest:
        await bot.send_message(chat_id, f"{E.e('warn')} Kinoni yuborishda xatolik. Admin bilan bog'laning.")


# Yangi kino e'lonidagi "Ko'rish" tugmasi (premium a'zolarga)
@dp.callback_query(F.data.startswith("watch_code_"))
async def cb_watch_code(cb: CallbackQuery):
    code = cb.data[len("watch_code_"):]
    movie = await db.get_movie(code)
    if movie:
        await send_movie(cb.from_user.id, movie)
        await cb.answer()
    else:
        await cb.answer("Kino topilmadi", show_alert=True)


# ═══════════════════════════════════════════════════════════════════
#  2) ASOSIY KANAL
# ═══════════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "main_channel")
async def cb_main_channel(cb: CallbackQuery):
    s = await db.all_settings()
    link = s.get("main_channel") or None
    await safe_edit(cb, await T.main_channel_text(link), K.back_main())
    await cb.answer()


# ═══════════════════════════════════════════════════════════════════
#  4) REKLAMA
# ═══════════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "ads")
async def cb_ads(cb: CallbackQuery):
    s = await db.all_settings()
    text = s.get("ads_text") or "Reklama ma'lumoti hali sozlanmagan."
    admin = s.get("ads_admin") or None
    await safe_edit(cb, text, K.ads_menu(admin))
    await cb.answer()


# ═══════════════════════════════════════════════════════════════════
#  3) PREMIUM / TARIF SOTIB OLISH
# ═══════════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "buy_premium")
async def cb_buy_premium(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    prices = await get_prices()
    stars = await get_stars()
    await safe_edit(cb, await T.premium_offer(prices, stars), K.premium_plans(prices))
    await cb.answer()


@dp.callback_query(F.data.startswith("plan_"))
async def cb_plan(cb: CallbackQuery):
    plan = cb.data[len("plan_"):]           # 1d | 10d | 30d
    if plan not in PLAN_LABELS:
        await cb.answer()
        return
    prices = await get_prices()
    stars = await get_stars()
    label = PLAN_LABELS[plan]
    await safe_edit(
        cb,
        await T.choose_method(label, prices[plan], stars[plan]),
        K.payment_methods(plan),
    )
    await cb.answer()


# ─── Karta orqali (Humo / Uzcard) ─────────────────────────────────
@dp.callback_query(F.data.startswith("pay_humo_") | F.data.startswith("pay_uzcard_"))
async def cb_pay_card(cb: CallbackQuery):
    parts = cb.data.split("_")            # pay_humo_1d
    method = parts[1]                     # humo | uzcard
    plan = parts[2]
    s = await db.all_settings()
    prices = await get_prices()
    card = s.get(f"card_{method}") or ""
    name = s.get(f"card_{method}_name") or "—"
    if not card:
        await cb.answer("Bu to'lov usuli hali sozlanmagan", show_alert=True)
        return
    await safe_edit(
        cb,
        await T.card_instructions(method, card, name, PLAN_LABELS[plan], prices[plan]),
        K.card_paid(plan, method),
    )
    await cb.answer()


@dp.callback_query(F.data.startswith("sent_"))
async def cb_sent_receipt(cb: CallbackQuery, state: FSMContext):
    # sent_humo_1d
    parts = cb.data.split("_")
    method = parts[1]
    plan = parts[2]
    prices = await get_prices()
    pid = await db.create_payment(cb.from_user.id, plan, method, prices[plan])
    await state.set_state(UserSt.waiting_receipt)
    await state.update_data(pid=pid)
    await safe_edit(cb, await T.send_receipt(), K.back_main())
    await cb.answer()


@dp.message(UserSt.waiting_receipt, F.photo | F.document)
async def on_receipt(msg: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("pid")
    if not pid:
        await state.clear()
        return
    file_id = msg.photo[-1].file_id if msg.photo else msg.document.file_id
    await db.attach_receipt(pid, file_id)
    pay = await db.get_payment(pid)
    await state.clear()

    await msg.answer(await T.receipt_received(), reply_markup=K.back_main())

    # adminga chekni yuborish
    u = msg.from_user
    uname = f"@{u.username}" if u.username else f"<a href='tg://user?id={u.id}'>{u.first_name}</a>"
    admin_text = (
        f"{E.e('card')} <b>Yangi to'lov so'rovi</b>\n\n"
        f"{E.e('user')} Foydalanuvchi: {uname} (<code>{u.id}</code>)\n"
        f"{E.e('tariff')} Tarif: {PLAN_LABELS.get(pay['plan'], pay['plan'])}\n"
        f"{E.e('wallet')} Usul: {pay['method'].upper()}\n"
        f"{E.e('money')} Summa: {fmt(pay['amount'])} so'm\n"
        f"{E.e('id')} ID: #{pid}"
    )
    for aid in await db.list_admins():
        try:
            await bot.send_photo(aid, file_id, caption=admin_text,
                                 reply_markup=K.payment_review(pid))
        except (TelegramForbiddenError, TelegramBadRequest):
            continue


# ─── Telegram Stars orqali (avtomatik) ────────────────────────────
@dp.callback_query(F.data.startswith("pay_stars_"))
async def cb_pay_stars(cb: CallbackQuery):
    plan = cb.data[len("pay_stars_"):]
    stars = await get_stars()
    amount = int(stars[plan])
    label = PLAN_LABELS[plan]
    prices_payload = f"stars_{plan}_{cb.from_user.id}"
    try:
        await bot.send_invoice(
            chat_id=cb.from_user.id,
            title=f"Premium — {label}",
            description=f"{label} premium a'zolik",
            payload=prices_payload,
            currency="XTR",                 # Telegram Stars
            prices=[LabeledPrice(label=label, amount=amount)],
        )
        await cb.answer()
    except TelegramBadRequest as ex:
        await cb.answer(f"Stars to'lovida xatolik: {ex}", show_alert=True)


@dp.pre_checkout_query()
async def on_pre_checkout(q: PreCheckoutQuery):
    await q.answer(ok=True)


@dp.message(F.successful_payment)
async def on_success_payment(msg: Message):
    payload = msg.successful_payment.invoice_payload   # stars_1d_<uid>
    parts = payload.split("_")
    if len(parts) >= 2 and parts[0] == "stars":
        plan = parts[1]
        days = PLAN_DAYS.get(plan, 0)
        if days:
            until = await db.grant_premium(msg.from_user.id, days)
            until_str = until.strftime("%d.%m.%Y %H:%M")
            await msg.answer(await T.premium_activated(until_str, days),
                             reply_markup=K.premium_success())
            # adminlarga xabar
            await notify_admins(
                f"{E.e('gem')} <b>Stars to'lov!</b>\n"
                f"User <code>{msg.from_user.id}</code> — {PLAN_LABELS[plan]} premium oldi."
            )


# ═══════════════════════════════════════════════════════════════════
#  ADMIN PANEL
# ═══════════════════════════════════════════════════════════════════
async def _is_admin_cb(cb: CallbackQuery) -> bool:
    if await db.is_admin(cb.from_user.id):
        return True
    await cb.answer("⛔ Bu bo'lim faqat adminlar uchun", show_alert=True)
    return False


@dp.message(Command("emoji"))
async def cmd_emoji(msg: Message):
    """
    Admin uchun: emoji ID'ni ko'rish vositasi.
      /emoji              → botda ishlatilayotgan barcha emoji nomlari
      /emoji <id>         → o'sha ID emojisini ko'rsatadi (mos kelishini tekshirish)
      /emoji <nom> <id>   → emoji.py dagi nomni shu ID ga vaqtincha bog'lash (test)
    """
    if not await db.is_admin(msg.from_user.id):
        return
    parts = (msg.text or "").split()
    # faqat /emoji — ro'yxat
    if len(parts) == 1:
        lines = [f"{E.e('sparkle')} <b>Botdagi emoji nomlari</b>\n"]
        for name, (eid, fb) in E.EMOJI.items():
            lines.append(f"<code>{name}</code> = {fb} <code>{eid}</code>")
        # uzun bo'lsa bo'lib yuboramiz
        chunk = ""
        for ln in lines:
            if len(chunk) + len(ln) > 3500:
                await msg.answer(chunk)
                chunk = ""
            chunk += ln + "\n"
        if chunk:
            await msg.answer(chunk)
        return
    # /emoji <id> — bitta ID ni ko'rsatish
    if len(parts) == 2 and parts[1].isdigit():
        eid = parts[1]
        html = f'<tg-emoji emoji-id="{eid}">⭐️</tg-emoji>'
        await msg.answer(
            f"ID <code>{eid}</code> uchun emoji:\n\n"
            f"{html} {html} {html}\n\n"
            f"{E.e('info')} Agar yulduzcha ko'rinsa — bu ID sizda ishlamadi "
            f"(yoki siz Premium emassiz). Agar boshqa emoji ko'rinsa — ishladi!"
        )
        return
    await msg.answer(
        f"{E.e('info')} Foydalanish:\n"
        f"<code>/emoji</code> — ro'yxat\n"
        f"<code>/emoji 5767199127775481841</code> — ID ni ko'rish"
    )


@dp.message(Command("admin"))
async def cmd_admin(msg: Message, state: FSMContext):
    await state.clear()
    if not await db.is_admin(msg.from_user.id):
        return
    await msg.answer(T.admin_welcome(), reply_markup=K.admin_main())


@dp.callback_query(F.data == "adm_main")
async def cb_adm_main(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.clear()
    await safe_edit(cb, T.admin_welcome(), K.admin_main())
    await cb.answer()


# ─── Statistika ───────────────────────────────────────────────────
@dp.callback_query(F.data == "adm_stats")
async def cb_adm_stats(cb: CallbackQuery):
    if not await _is_admin_cb(cb):
        return
    s = await db.stats()
    await safe_edit(cb, T.stats_text(s), K.admin_back())
    await cb.answer()


# ─── Kino qo'shish (4 bosqich) ────────────────────────────────────
@dp.callback_query(F.data == "adm_add_movie")
async def cb_adm_add_movie(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.set_state(MovieSt.code)
    await safe_edit(cb, T.ask_movie_code(), K.cancel_kb("adm_main"))
    await cb.answer()


@dp.message(MovieSt.code, F.text)
async def movie_code(msg: Message, state: FSMContext):
    code = msg.text.strip()
    existing = await db.get_movie(code)
    if existing:
        await msg.answer(f"{E.e('warn')} Bu kod band. Boshqa kod yuboring.",
                         reply_markup=K.cancel_kb("adm_main"))
        return
    await state.update_data(code=code)
    await state.set_state(MovieSt.title)
    await msg.answer(T.ask_movie_title(), reply_markup=K.cancel_kb("adm_main"))


@dp.message(MovieSt.title, F.text)
async def movie_title(msg: Message, state: FSMContext):
    await state.update_data(title=msg.text.strip())
    await state.set_state(MovieSt.caption)
    await msg.answer(T.ask_movie_caption(), reply_markup=K.cancel_kb("adm_main"))


@dp.message(MovieSt.caption, F.text)
async def movie_caption(msg: Message, state: FSMContext):
    await state.update_data(caption=msg.text.strip())
    await state.set_state(MovieSt.file)
    await msg.answer(T.ask_movie_file(), reply_markup=K.cancel_kb("adm_main"))


@dp.message(MovieSt.file, F.video | F.document)
async def movie_file(msg: Message, state: FSMContext):
    data = await state.get_data()
    if msg.video:
        file_id, ftype = msg.video.file_id, "video"
    else:
        file_id, ftype = msg.document.file_id, "document"

    ok = await db.add_movie(data["code"], data["title"], data["caption"], file_id, ftype)
    await state.clear()
    if not ok:
        await msg.answer(f"{E.e('cross')} Bu kod allaqachon mavjud.",
                         reply_markup=K.admin_back())
        return

    prem_ids = await db.premium_user_ids()
    await msg.answer(T.movie_added(data["code"], len(prem_ids)),
                     reply_markup=K.admin_back())

    # premium a'zolarga yangi kino e'loni
    movie = await db.get_movie(data["code"])
    announce = await T.new_movie_for_premium(data["code"], data["title"], data["caption"])
    sent = 0
    for uid in prem_ids:
        try:
            if ftype == "document":
                await bot.send_document(uid, file_id, caption=announce)
            else:
                await bot.send_video(uid, file_id, caption=announce)
            sent += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            continue
        await asyncio.sleep(0.05)
    if prem_ids:
        await msg.answer(f"{E.e('check')} {sent}/{len(prem_ids)} premium a'zoga yuborildi.",
                         reply_markup=K.admin_back())


# ─── Kino o'chirish ───────────────────────────────────────────────
@dp.callback_query(F.data == "adm_del_movie")
async def cb_adm_del_movie(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.set_state(MovieSt.delete)
    await safe_edit(cb, f"{E.e('trash')} O'chiriladigan kino <b>kodini</b> yuboring:",
                    K.cancel_kb("adm_main"))
    await cb.answer()


@dp.message(MovieSt.delete, F.text)
async def movie_delete(msg: Message, state: FSMContext):
    code = msg.text.strip()
    ok = await db.delete_movie(code)
    await state.clear()
    if ok:
        await msg.answer(f"{E.e('check')} Kino o'chirildi: <code>{code}</code>",
                         reply_markup=K.admin_back())
    else:
        await msg.answer(f"{E.e('cross')} Bunday kodli kino topilmadi.",
                         reply_markup=K.admin_back())


# ─── Kinolar ro'yxati ─────────────────────────────────────────────
@dp.callback_query(F.data == "adm_movies")
async def cb_adm_movies(cb: CallbackQuery):
    if not await _is_admin_cb(cb):
        return
    movies = await db.list_movies(40)
    if not movies:
        text = f"{E.e('movie')} Hali kino qo'shilmagan."
    else:
        lines = [f"{E.e('movie')} <b>Kinolar ro'yxati</b>\n"]
        for m in movies:
            lines.append(f"<code>{m['code']}</code> — {m['title']} ({m['views']} ko'rildi)")
        text = "\n".join(lines)
    await safe_edit(cb, text, K.admin_back())
    await cb.answer()


# ─── Premium a'zolar ──────────────────────────────────────────────
@dp.callback_query(F.data == "adm_prem_list")
async def cb_adm_prem_list(cb: CallbackQuery):
    if not await _is_admin_cb(cb):
        return
    ids = await db.premium_user_ids()
    if not ids:
        text = f"{E.e('gem')} Hozircha premium a'zolar yo'q."
    else:
        lines = [f"{E.e('gem')} <b>Premium a'zolar ({len(ids)} ta)</b>\n"]
        for uid in ids[:50]:
            until = await db.premium_until(uid)
            us = until.strftime("%d.%m.%Y") if until else "?"
            lines.append(f"<code>{uid}</code> — {us} gacha")
        text = "\n".join(lines)
    await safe_edit(cb, text, K.admin_back())
    await cb.answer()


# ─── MAJBURIY OBUNA boshqaruvi ────────────────────────────────────
@dp.callback_query(F.data == "adm_channels")
async def cb_adm_channels(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.clear()
    channels = await db.list_channels()
    text = (
        f"{E.e('channel')} <b>Majburiy obuna kanallari</b>\n\n"
        f"• <b>Ommaviy</b> — oddiy kanal/guruh, foydalanuvchi qo'shilishi kerak\n"
        f"• <b>Zayavkali</b> — yopiq kanal, so'rov yuborsa avto tasdiqlanadi\n\n"
        f"{E.e('warn')} Bot kanalga <b>admin</b> qilib qo'shilgan bo'lishi shart!"
    )
    await safe_edit(cb, text, K.admin_channels(channels))
    await cb.answer()


@dp.callback_query(F.data.in_({"adm_chadd_public", "adm_chadd_request"}))
async def cb_adm_chadd(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    join_type = "public" if cb.data.endswith("public") else "request"
    await state.set_state(ChannelSt.waiting)
    await state.update_data(join_type=join_type)
    jt_label = "ommaviy" if join_type == "public" else "zayavkali"
    text = (
        f"{E.e('plus')} <b>{jt_label.capitalize()} kanal qo'shish</b>\n\n"
        f"Quyidagilardan birini yuboring:\n"
        f"1) Kanaldan istalgan postni <b>forward</b> qiling, yoki\n"
        f"2) Kanal <b>ID</b>sini yuboring (masalan <code>-1001234567890</code>)\n\n"
        f"So'ng men kanal havolasini so'rayman."
    )
    await safe_edit(cb, text, K.cancel_kb("adm_channels"))
    await cb.answer()


@dp.message(ChannelSt.waiting)
async def channel_input(msg: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = None
    title = None

    # forward qilingan post
    if msg.forward_from_chat:
        chat_id = str(msg.forward_from_chat.id)
        title = msg.forward_from_chat.title
        if msg.forward_from_chat.username:
            link = f"https://t.me/{msg.forward_from_chat.username}"
        else:
            link = None
    elif msg.text:
        chat_id = msg.text.strip()
        title = None
        link = None
    else:
        await msg.answer(f"{E.e('warn')} Post forward qiling yoki kanal ID yuboring.")
        return

    # title/link to'liq bo'lmasa — botdan olishga harakat
    try:
        chat = await bot.get_chat(chat_id)
        title = title or chat.title
        if not link and chat.username:
            link = f"https://t.me/{chat.username}"
        if not link:
            # invite link yaratishga harakat (bot admin bo'lsa)
            try:
                inv = await bot.create_chat_invite_link(
                    chat.id, creates_join_request=(data["join_type"] == "request"))
                link = inv.invite_link
            except TelegramBadRequest:
                link = None
    except TelegramBadRequest:
        await msg.answer(
            f"{E.e('cross')} Kanalga ulanib bo'lmadi. Bot u yerda admin ekanini tekshiring."
        )
        return

    await db.add_channel(chat_id, title or "Kanal", link or "", data["join_type"])
    await state.clear()
    await msg.answer(
        f"{E.e('check')} Kanal qo'shildi: <b>{title or chat_id}</b>",
        reply_markup=K.admin_back(),
    )


@dp.callback_query(F.data.startswith("adm_chdel_"))
async def cb_adm_chdel(cb: CallbackQuery):
    if not await _is_admin_cb(cb):
        return
    ch_id = int(cb.data[len("adm_chdel_"):])
    await db.del_channel(ch_id)
    channels = await db.list_channels()
    await safe_edit(cb, f"{E.e('check')} Kanal o'chirildi.",
                    K.admin_channels(channels))
    await cb.answer()


# ─── NARXLAR boshqaruvi ───────────────────────────────────────────
@dp.callback_query(F.data == "adm_prices")
async def cb_adm_prices(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.clear()
    s = await db.all_settings()
    await safe_edit(cb, f"{E.e('money')} <b>Narxlarni sozlash</b>\n\nO'zgartirish uchun tugmani bosing:",
                    K.admin_prices(s))
    await cb.answer()


_PRICE_KEYS = {
    "adm_setp_1d": ("price_1d", "1 kunlik (so'm)"),
    "adm_setp_10d": ("price_10d", "10 kunlik (so'm)"),
    "adm_setp_30d": ("price_30d", "30 kunlik (so'm)"),
    "adm_sets_1d": ("price_stars_1d", "1 kunlik (Stars)"),
    "adm_sets_10d": ("price_stars_10d", "10 kunlik (Stars)"),
    "adm_sets_30d": ("price_stars_30d", "30 kunlik (Stars)"),
}


@dp.callback_query(F.data.in_(set(_PRICE_KEYS.keys())))
async def cb_set_price(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    key, label = _PRICE_KEYS[cb.data]
    await state.set_state(PriceSt.waiting)
    await state.update_data(key=key)
    await safe_edit(cb, f"{E.e('edit')} <b>{label}</b> uchun yangi narxni yuboring (faqat raqam):",
                    K.cancel_kb("adm_prices"))
    await cb.answer()


@dp.message(PriceSt.waiting, F.text)
async def price_input(msg: Message, state: FSMContext):
    val = msg.text.strip().replace(" ", "")
    if not val.isdigit():
        await msg.answer(f"{E.e('warn')} Faqat raqam yuboring.")
        return
    data = await state.get_data()
    await db.set_setting(data["key"], val)
    await state.clear()
    s = await db.all_settings()
    await msg.answer(f"{E.e('check')} Narx yangilandi: <b>{fmt(val)}</b>",
                     reply_markup=K.admin_prices(s))


# ─── KARTALAR boshqaruvi ──────────────────────────────────────────
@dp.callback_query(F.data == "adm_cards")
async def cb_adm_cards(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.clear()
    s = await db.all_settings()
    await safe_edit(cb, f"{E.e('card')} <b>To'lov kartalari</b>\n\nO'zgartirish uchun tanlang:",
                    K.admin_cards(s))
    await cb.answer()


_CARD_KEYS = {
    "adm_setcard_humo": ("card_humo", "Humo karta raqami"),
    "adm_setcard_humo_name": ("card_humo_name", "Humo karta egasi"),
    "adm_setcard_uzcard": ("card_uzcard", "Uzcard raqami"),
    "adm_setcard_uzcard_name": ("card_uzcard_name", "Uzcard egasi"),
}


@dp.callback_query(F.data.in_(set(_CARD_KEYS.keys())))
async def cb_set_card(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    key, label = _CARD_KEYS[cb.data]
    await state.set_state(CardSt.waiting)
    await state.update_data(key=key)
    await safe_edit(cb, f"{E.e('edit')} <b>{label}</b>ni yuboring:",
                    K.cancel_kb("adm_cards"))
    await cb.answer()


@dp.message(CardSt.waiting, F.text)
async def card_input(msg: Message, state: FSMContext):
    data = await state.get_data()
    await db.set_setting(data["key"], msg.text.strip())
    await state.clear()
    s = await db.all_settings()
    await msg.answer(f"{E.e('check')} Saqlandi.", reply_markup=K.admin_cards(s))


# ─── LINKLAR boshqaruvi ───────────────────────────────────────────
@dp.callback_query(F.data == "adm_links")
async def cb_adm_links(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.clear()
    s = await db.all_settings()
    await safe_edit(cb, f"{E.e('link')} <b>Linklarni sozlash</b>",
                    K.admin_links(s))
    await cb.answer()


_LINK_KEYS = {
    "adm_setlink_main": ("main_channel", "Asosiy kanal havolasi"),
    "adm_setlink_movies": ("movies_channel", "Kinolar to'plami havolasi"),
}


@dp.callback_query(F.data.in_(set(_LINK_KEYS.keys())))
async def cb_set_link(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    key, label = _LINK_KEYS[cb.data]
    await state.set_state(LinkSt.waiting)
    await state.update_data(key=key)
    await safe_edit(cb, f"{E.e('edit')} <b>{label}</b>ni yuboring (https://t.me/... yoki @username):",
                    K.cancel_kb("adm_links"))
    await cb.answer()


@dp.message(LinkSt.waiting, F.text)
async def link_input(msg: Message, state: FSMContext):
    data = await state.get_data()
    val = msg.text.strip()
    if val.startswith("@"):
        val = f"https://t.me/{val[1:]}"
    await db.set_setting(data["key"], val)
    await state.clear()
    s = await db.all_settings()
    await msg.answer(f"{E.e('check')} Saqlandi.", reply_markup=K.admin_links(s))


# ─── REKLAMA boshqaruvi ───────────────────────────────────────────
@dp.callback_query(F.data == "adm_ads")
async def cb_adm_ads(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.clear()
    s = await db.all_settings()
    await safe_edit(cb, f"{E.e('megaphone')} <b>Reklama sozlamalari</b>",
                    K.admin_ads(s))
    await cb.answer()


@dp.callback_query(F.data == "adm_set_ads_text")
async def cb_set_ads_text(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.set_state(AdsSt.text)
    await safe_edit(cb, f"{E.e('edit')} Yangi reklama matnini yuboring (HTML qo'llab-quvvatlanadi):",
                    K.cancel_kb("adm_ads"))
    await cb.answer()


@dp.message(AdsSt.text, F.text)
async def ads_text_input(msg: Message, state: FSMContext):
    await db.set_setting("ads_text", msg.html_text)
    await state.clear()
    s = await db.all_settings()
    await msg.answer(f"{E.e('check')} Reklama matni yangilandi.",
                     reply_markup=K.admin_ads(s))


@dp.callback_query(F.data == "adm_set_ads_admin")
async def cb_set_ads_admin(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.set_state(AdsSt.admin)
    await safe_edit(cb, f"{E.e('user')} Reklama uchun admin username yuboring (@ bilan yoki @ siz):",
                    K.cancel_kb("adm_ads"))
    await cb.answer()


@dp.message(AdsSt.admin, F.text)
async def ads_admin_input(msg: Message, state: FSMContext):
    await db.set_setting("ads_admin", msg.text.strip().lstrip("@"))
    await state.clear()
    s = await db.all_settings()
    await msg.answer(f"{E.e('check')} Reklama admini saqlandi.",
                     reply_markup=K.admin_ads(s))


# ─── MATNLARNI TAHRIRLASH ─────────────────────────────────────────
@dp.callback_query(F.data == "adm_texts")
async def cb_adm_texts(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.clear()
    items = [(key, label) for key, (label, _d, _ph) in DEFAULT_TEXTS.items()]
    text = (
        f"{E.e('edit')} <b>Matnlarni tahrirlash</b>\n\n"
        f"Qaysi matnni o'zgartirmoqchisiz? Tanlang — avval hozirgi matn "
        f"ko'rsatiladi, so'ng yangisini yuborasiz.\n\n"
        f"{E.e('info')} <i>{{...}}</i> ichidagi joylarni saqlang — ular avtomatik to'ldiriladi."
    )
    await safe_edit(cb, text, K.admin_texts(items))
    await cb.answer()


@dp.callback_query(F.data.startswith("txt_"))
async def cb_text_show(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    key = cb.data[len("txt_"):]
    if key not in DEFAULT_TEXTS:
        await cb.answer("Topilmadi", show_alert=True)
        return
    label, _default, placeholders = DEFAULT_TEXTS[key]
    current = await db.get_text(key)
    await state.set_state(TextSt.waiting)
    await state.update_data(text_key=key)

    ph_note = ""
    if placeholders:
        ph_list = ", ".join(f"<code>{p}</code>" for p in placeholders)
        ph_note = f"\n\n{E.e('warn')} Bu joylarni saqlang: {ph_list}"

    # hozirgi matnni "raw" ko'rsatamiz (HTML teglari ko'rinsin, premium emoji o'ralmasin)
    safe_current = current.replace("<", "&lt;").replace(">", "&gt;")
    msg_text = (
        f"{E.e('doc')} <b>{label}</b>\n\n"
        f"<b>Hozirgi matn:</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{safe_current}\n"
        f"━━━━━━━━━━━━━━{ph_note}\n\n"
        f"{E.e('edit')} Yangi matnni yuboring (HTML qo'llab-quvvatlanadi),\n"
        f"yoki bekor qilish/standartga qaytarish tugmasini bosing:"
    )
    await safe_edit(cb, msg_text, K.text_edit(key))
    await cb.answer()


@dp.callback_query(F.data.startswith("txtreset_"))
async def cb_text_reset(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    key = cb.data[len("txtreset_"):]
    if key not in DEFAULT_TEXTS:
        await cb.answer("Topilmadi", show_alert=True)
        return
    await db.reset_text(key)
    await state.clear()
    label = DEFAULT_TEXTS[key][0]
    await safe_edit(
        cb,
        f"{E.e('check')} <b>{label}</b> standart holatiga qaytarildi.",
        K.text_edit_done(key),
    )
    await cb.answer("✅ Standartga qaytarildi")


@dp.message(TextSt.waiting)
async def text_input(msg: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("text_key")
    if not key or key not in DEFAULT_TEXTS:
        await state.clear()
        return
    # HTML formatni saqlash uchun html_text (matn bo'lsa); aks holcaption
    new_text = msg.html_text if msg.text else (msg.caption or "")
    if not new_text.strip():
        await msg.answer(f"{E.e('warn')} Bo'sh matn yuborib bo'lmaydi. Qaytadan yuboring.")
        return
    await db.set_text(key, new_text)
    await state.clear()
    label = DEFAULT_TEXTS[key][0]
    await msg.answer(
        f"{E.e('check')} <b>{label}</b> yangilandi!\n\n"
        f"{E.e('info')} O'zgarishni ko'rish uchun tegishli bo'limga o'ting.",
        reply_markup=K.text_edit_done(key),
    )


# ─── ADMINLAR boshqaruvi ──────────────────────────────────────────
@dp.callback_query(F.data == "adm_admins")
async def cb_adm_admins(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.clear()
    admins = await db.list_admins()
    text = (
        f"{E.e('users')} <b>Adminlar</b>\n\n"
        f"👑 — asosiy admin (o'chirilmaydi)\n"
        f"Qo'shish uchun foydalanuvchi ID kerak."
    )
    await safe_edit(cb, text, K.admin_admins(admins, OWNER_IDS))
    await cb.answer()


@dp.callback_query(F.data == "adm_addadm")
async def cb_addadm(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.set_state(AdminSt.add)
    await safe_edit(cb, f"{E.e('plus')} Yangi admin <b>ID</b>sini yuboring:",
                    K.cancel_kb("adm_admins"))
    await cb.answer()


@dp.message(AdminSt.add, F.text)
async def addadm_input(msg: Message, state: FSMContext):
    val = msg.text.strip()
    if not val.lstrip("-").isdigit():
        await msg.answer(f"{E.e('warn')} Faqat raqamli ID yuboring.")
        return
    await db.add_admin(int(val))
    await state.clear()
    admins = await db.list_admins()
    await msg.answer(f"{E.e('check')} Admin qo'shildi: <code>{val}</code>",
                     reply_markup=K.admin_admins(admins, OWNER_IDS))


@dp.callback_query(F.data.startswith("adm_deladm_"))
async def cb_deladm(cb: CallbackQuery):
    if not await _is_admin_cb(cb):
        return
    aid = int(cb.data[len("adm_deladm_"):])
    await db.del_admin(aid)
    admins = await db.list_admins()
    await safe_edit(cb, f"{E.e('check')} Admin o'chirildi.",
                    K.admin_admins(admins, OWNER_IDS))
    await cb.answer()


# ─── BROADCAST (xabar yuborish) ───────────────────────────────────
@dp.callback_query(F.data == "adm_broadcast")
async def cb_adm_broadcast(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    await state.clear()
    text = (
        f"{E.e('send')} <b>Xabar yuborish</b>\n\n"
        f"Kimga yuborishni tanlang:"
    )
    await safe_edit(cb, text, K.broadcast_target())
    await cb.answer()


@dp.callback_query(F.data.in_({"bc_all", "bc_premium"}))
async def cb_bc_target(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    target = "all" if cb.data == "bc_all" else "premium"
    await state.set_state(BroadcastSt.content)
    await state.update_data(target=target)
    label = "barcha foydalanuvchilarga" if target == "all" else "premium a'zolarga"
    await safe_edit(
        cb,
        f"{E.e('send')} Endi <b>{label}</b> yuboriladigan xabarni yuboring.\n\n"
        f"{E.e('info')} Matn, rasm, video yoki ovozli xabar — istalganini yuborishingiz mumkin.",
        K.cancel_kb("adm_main"),
    )
    await cb.answer()


@dp.message(BroadcastSt.content)
async def bc_content(msg: Message, state: FSMContext):
    await state.update_data(
        chat_id=msg.chat.id,
        message_id=msg.message_id,
    )
    data = await state.get_data()
    target = data["target"]
    ids = await db.premium_user_ids() if target == "premium" else await db.all_user_ids(True)
    await state.update_data(count=len(ids))
    label = "premium a'zolar" if target == "premium" else "barcha foydalanuvchilar"
    await msg.answer(
        f"{E.e('warn')} <b>Tasdiqlang</b>\n\n"
        f"Yuqoridagi xabar <b>{label}</b>ga ({len(ids)} ta) yuboriladi.\n\n"
        f"Davom etamizmi?",
        reply_markup=K.broadcast_confirm(),
    )


@dp.callback_query(F.data == "bc_send")
async def cb_bc_send(cb: CallbackQuery, state: FSMContext):
    if not await _is_admin_cb(cb):
        return
    data = await state.get_data()
    target = data.get("target", "all")
    from_chat = data.get("chat_id")
    msg_id = data.get("message_id")
    await state.clear()

    if not from_chat or not msg_id:
        await cb.answer("Xabar topilmadi", show_alert=True)
        return

    ids = await db.premium_user_ids() if target == "premium" else await db.all_user_ids(True)
    await safe_edit(cb, f"{E.e('rocket')} Yuborilmoqda... (0/{len(ids)})", None)

    sent = failed = 0
    for i, uid in enumerate(ids, 1):
        try:
            await bot.copy_message(uid, from_chat, msg_id)
            sent += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1
            await db.mark_left(uid)
        except Exception:
            failed += 1
        if i % 25 == 0:
            try:
                await cb.message.edit_text(
                    f"{E.e('rocket')} Yuborilmoqda... ({i}/{len(ids)})")
            except TelegramBadRequest:
                pass
        await asyncio.sleep(0.05)

    await cb.message.answer(
        f"{E.e('check')} <b>Yuborildi!</b>\n\n"
        f"{E.e('ok')} Muvaffaqiyatli: <b>{sent}</b>\n"
        f"{E.e('cross')} Yetib bormadi: <b>{failed}</b>",
        reply_markup=K.admin_back(),
    )
    await cb.answer()


# ─── TO'LOV CHEKINI TASDIQLASH / RAD ETISH ────────────────────────
@dp.callback_query(F.data.startswith("pay_ok_"))
async def cb_pay_ok(cb: CallbackQuery):
    if not await _is_admin_cb(cb):
        return
    pid = int(cb.data[len("pay_ok_"):])
    pay = await db.get_payment(pid)
    if not pay or pay["status"] != "pending":
        await cb.answer("Bu so'rov allaqachon ko'rib chiqilgan", show_alert=True)
        return
    await db.set_payment_status(pid, "approved")
    days = PLAN_DAYS.get(pay["plan"], 0)
    until = await db.grant_premium(pay["user_id"], days)
    until_str = until.strftime("%d.%m.%Y %H:%M")

    # foydalanuvchiga xabar
    try:
        await bot.send_message(
            pay["user_id"],
            await T.premium_activated(until_str, days),
            reply_markup=K.premium_success(),
        )
    except (TelegramForbiddenError, TelegramBadRequest):
        pass

    # admin xabarini yangilash
    try:
        await cb.message.edit_caption(
            caption=cb.message.caption + f"\n\n{E.raw('check')} TASDIQLANDI",
            reply_markup=None,
        )
    except TelegramBadRequest:
        pass
    await cb.answer("✅ Tasdiqlandi va premium berildi")


@dp.callback_query(F.data.startswith("pay_no_"))
async def cb_pay_no(cb: CallbackQuery):
    if not await _is_admin_cb(cb):
        return
    pid = int(cb.data[len("pay_no_"):])
    pay = await db.get_payment(pid)
    if not pay or pay["status"] != "pending":
        await cb.answer("Bu so'rov allaqachon ko'rib chiqilgan", show_alert=True)
        return
    await db.set_payment_status(pid, "rejected")
    try:
        await bot.send_message(
            pay["user_id"],
            await T.payment_rejected(),
            reply_markup=K.back_main(),
        )
    except (TelegramForbiddenError, TelegramBadRequest):
        pass
    try:
        await cb.message.edit_caption(
            caption=cb.message.caption + f"\n\n{E.raw('cross')} RAD ETILDI",
            reply_markup=None,
        )
    except TelegramBadRequest:
        pass
    await cb.answer("❌ Rad etildi")


# ─── To'lov so'rovlari ro'yxati ───────────────────────────────────
@dp.callback_query(F.data == "adm_payments")
async def cb_adm_payments(cb: CallbackQuery):
    if not await _is_admin_cb(cb):
        return
    text = (
        f"{E.e('wallet')} <b>To'lov so'rovlari</b>\n\n"
        f"{E.e('info')} Yangi karta to'lovlari chek bilan birga "
        f"avtomatik ravishda shu yerga (admin lichkasiga) keladi.\n\n"
        f"Stars to'lovlari avtomatik tasdiqlanadi."
    )
    await safe_edit(cb, text, K.admin_back())
    await cb.answer()


@dp.callback_query(F.data == "noop")
async def cb_noop(cb: CallbackQuery):
    await cb.answer()


# ═══════════════════════════════════════════════════════════════════
#  ISHGA TUSHIRISH
# ═══════════════════════════════════════════════════════════════════
async def on_startup():
    await db.init()
    me = await bot.get_me()
    log.info(f"Bot ishga tushdi: @{me.username}")


async def on_shutdown():
    await db.close()
    await bot.session.close()


async def main_polling():
    await on_startup()
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await on_shutdown()


def main_webhook():
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    async def _startup(app):
        await on_startup()
        await bot.set_webhook(
            f"{WEBHOOK_HOST}{WEBHOOK_PATH}",
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
            allowed_updates=dp.resolve_used_update_types(),
        )

    async def _cleanup(app):
        await on_shutdown()

    app = web.Application()
    app.on_startup.append(_startup)
    app.on_cleanup.append(_cleanup)
    SimpleRequestHandler(dispatcher=dp, bot=bot,
                         secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=WEBAPP_PORT)


if __name__ == "__main__":
    if USE_WEBHOOK:
        main_webhook()
    else:
        asyncio.run(main_polling())
