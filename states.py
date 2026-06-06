"""FSM holatlari (admin inputlari va foydalanuvchi kod kiritishi uchun)."""
from aiogram.fsm.state import State, StatesGroup


class UserSt(StatesGroup):
    waiting_code = State()          # kino kodini kutish
    waiting_receipt = State()       # to'lov chekini kutish


class MovieSt(StatesGroup):
    code = State()
    title = State()
    caption = State()
    file = State()
    delete = State()


class ChannelSt(StatesGroup):
    waiting = State()               # kanal forward yoki ID kutish


class PriceSt(StatesGroup):
    waiting = State()               # narx kiritish


class CardSt(StatesGroup):
    waiting = State()               # karta/ism kiritish


class LinkSt(StatesGroup):
    waiting = State()               # link kiritish


class AdsSt(StatesGroup):
    text = State()
    admin = State()


class AdminSt(StatesGroup):
    add = State()                   # admin qo'shish (ID)


class BroadcastSt(StatesGroup):
    content = State()               # broadcast kontenti
