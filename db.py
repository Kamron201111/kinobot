"""
═══════════════════════════════════════════════════════════════════
 MA'LUMOTLAR BAZASI (PostgreSQL / asyncpg)
───────────────────────────────────────────────────────────────────
 Railway PostgreSQL bilan ishlaydi. DATABASE_URL avtomatik beriladi.
═══════════════════════════════════════════════════════════════════
"""
import datetime as dt
from typing import Any, Optional

import asyncpg

from config import DATABASE_URL, DEFAULT_SETTINGS, OWNER_IDS
from default_texts import TEXTS

_pool: Optional[asyncpg.Pool] = None


async def init() -> None:
    """Pool ochish + jadvallarni yaratish + default qiymatlar."""
    global _pool
    dsn = DATABASE_URL
    # Railway ba'zan "postgres://" beradi — asyncpg "postgresql://" ni xohlaydi
    if dsn.startswith("postgres://"):
        dsn = "postgresql://" + dsn[len("postgres://"):]
    _pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)
    await _create_tables()
    await _seed_settings()
    await _seed_texts()
    await _seed_owners()


async def close() -> None:
    if _pool:
        await _pool.close()


async def _create_tables() -> None:
    async with _pool.acquire() as c:
        await c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id  BIGINT PRIMARY KEY,
            username     TEXT,
            first_name   TEXT,
            is_active    BOOLEAN DEFAULT TRUE,   -- botni bloklamaganmi
            is_banned    BOOLEAN DEFAULT FALSE,
            joined_at    TIMESTAMPTZ DEFAULT now(),
            left_at      TIMESTAMPTZ              -- botni to'xtatgan vaqt
        );

        CREATE TABLE IF NOT EXISTS movies (
            id          SERIAL PRIMARY KEY,
            code        TEXT UNIQUE NOT NULL,
            title       TEXT,
            caption     TEXT,
            file_id     TEXT,                     -- telegramdagi video file_id
            file_type   TEXT DEFAULT 'video',     -- video | document
            views       INT DEFAULT 0,
            created_at  TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS channels (
            id          SERIAL PRIMARY KEY,
            chat_id     TEXT NOT NULL,            -- -100... yoki @username
            title       TEXT,
            link        TEXT,                     -- t.me/... yoki join request link
            join_type   TEXT DEFAULT 'public',    -- public | request (zayavkali)
            added_at    TIMESTAMPTZ DEFAULT now()
        );

        -- zayavkali kanal/guruhga so'rov yuborganlar (tasdiqlangan deb hisoblanadi)
        CREATE TABLE IF NOT EXISTS join_requests (
            user_id     BIGINT,
            chat_id     TEXT,
            approved    BOOLEAN DEFAULT TRUE,
            created_at  TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (user_id, chat_id)
        );

        CREATE TABLE IF NOT EXISTS premium (
            user_id     BIGINT PRIMARY KEY,
            until       TIMESTAMPTZ NOT NULL,
            updated_at  TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS payments (
            id          SERIAL PRIMARY KEY,
            user_id     BIGINT,
            plan        TEXT,                     -- 1d | 10d | 30d
            method      TEXT,                     -- humo | uzcard | stars
            amount      TEXT,                     -- summa (so'm yoki XTR)
            status      TEXT DEFAULT 'pending',   -- pending | approved | rejected
            receipt_id  TEXT,                     -- yuborilgan chek photo file_id
            created_at  TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS admins (
            telegram_id BIGINT PRIMARY KEY,
            added_at    TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        );

        -- kunlik statistika uchun yordamchi jurnal
        CREATE TABLE IF NOT EXISTS events (
            id        SERIAL PRIMARY KEY,
            user_id   BIGINT,
            kind      TEXT,                       -- join | leave
            at        TIMESTAMPTZ DEFAULT now()
        );
        """)


async def _seed_settings() -> None:
    async with _pool.acquire() as c:
        for k, v in DEFAULT_SETTINGS.items():
            await c.execute(
                "INSERT INTO settings(key, value) VALUES($1,$2) "
                "ON CONFLICT (key) DO NOTHING",
                k, v,
            )


async def _seed_owners() -> None:
    async with _pool.acquire() as c:
        for oid in OWNER_IDS:
            await c.execute(
                "INSERT INTO admins(telegram_id) VALUES($1) "
                "ON CONFLICT DO NOTHING",
                oid,
            )


async def _seed_texts() -> None:
    """Tahrirlanadigan matnlarni 'text_<key>' shaklida bazaga joylaydi."""
    async with _pool.acquire() as c:
        for key, (label, default, ph) in TEXTS.items():
            await c.execute(
                "INSERT INTO settings(key, value) VALUES($1,$2) "
                "ON CONFLICT (key) DO NOTHING",
                f"text_{key}", default,
            )


# ═══════════════════════════════════════════════════════════════════
#  TAHRIRLANADIGAN MATNLAR
# ═══════════════════════════════════════════════════════════════════
async def get_text(key: str) -> str:
    """Matnni bazadan oladi (yo'q bo'lsa standartdan)."""
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT value FROM settings WHERE key=$1", f"text_{key}")
    if row and row["value"] is not None:
        return row["value"]
    item = TEXTS.get(key)
    return item[1] if item else ""


async def set_text(key: str, value: str) -> None:
    async with _pool.acquire() as c:
        await c.execute(
            "INSERT INTO settings(key,value) VALUES($1,$2) "
            "ON CONFLICT (key) DO UPDATE SET value=$2",
            f"text_{key}", value,
        )


async def reset_text(key: str) -> str:
    """Matnni standart holatiga qaytaradi."""
    item = TEXTS.get(key)
    default = item[1] if item else ""
    await set_text(key, default)
    return default


# ═══════════════════════════════════════════════════════════════════
#  SETTINGS
# ═══════════════════════════════════════════════════════════════════
async def get_setting(key: str, default: str = "") -> str:
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT value FROM settings WHERE key=$1", key)
    return row["value"] if row and row["value"] is not None else default


async def set_setting(key: str, value: str) -> None:
    async with _pool.acquire() as c:
        await c.execute(
            "INSERT INTO settings(key,value) VALUES($1,$2) "
            "ON CONFLICT (key) DO UPDATE SET value=$2",
            key, value,
        )


async def all_settings() -> dict:
    async with _pool.acquire() as c:
        rows = await c.fetch("SELECT key, value FROM settings")
    return {r["key"]: r["value"] for r in rows}


# ═══════════════════════════════════════════════════════════════════
#  USERS
# ═══════════════════════════════════════════════════════════════════
async def upsert_user(tg_id: int, username: str | None, first_name: str | None) -> bool:
    """Yangi foydalanuvchi bo'lsa True qaytaradi (statistika uchun)."""
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT telegram_id, is_active FROM users WHERE telegram_id=$1", tg_id)
        if row is None:
            await c.execute(
                "INSERT INTO users(telegram_id, username, first_name) VALUES($1,$2,$3)",
                tg_id, username, first_name,
            )
            await c.execute("INSERT INTO events(user_id, kind) VALUES($1,'join')", tg_id)
            return True
        else:
            # qaytib kelgan bo'lsa active=true
            await c.execute(
                "UPDATE users SET username=$2, first_name=$3, is_active=TRUE, left_at=NULL "
                "WHERE telegram_id=$1",
                tg_id, username, first_name,
            )
            if not row["is_active"]:
                await c.execute("INSERT INTO events(user_id, kind) VALUES($1,'join')", tg_id)
            return False


async def mark_left(tg_id: int) -> None:
    async with _pool.acquire() as c:
        await c.execute(
            "UPDATE users SET is_active=FALSE, left_at=now() WHERE telegram_id=$1",
            tg_id,
        )
        await c.execute("INSERT INTO events(user_id, kind) VALUES($1,'leave')", tg_id)


async def ban_user(tg_id: int, banned: bool) -> None:
    async with _pool.acquire() as c:
        await c.execute("UPDATE users SET is_banned=$2 WHERE telegram_id=$1", tg_id, banned)


async def is_banned(tg_id: int) -> bool:
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT is_banned FROM users WHERE telegram_id=$1", tg_id)
    return bool(row and row["is_banned"])


async def get_user(tg_id: int) -> Optional[dict]:
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT * FROM users WHERE telegram_id=$1", tg_id)
    return dict(row) if row else None


async def all_user_ids(active_only: bool = True) -> list[int]:
    q = "SELECT telegram_id FROM users"
    if active_only:
        q += " WHERE is_active=TRUE AND is_banned=FALSE"
    async with _pool.acquire() as c:
        rows = await c.fetch(q)
    return [r["telegram_id"] for r in rows]


# ═══════════════════════════════════════════════════════════════════
#  STATISTIKA
# ═══════════════════════════════════════════════════════════════════
async def stats() -> dict:
    today = dt.datetime.now(dt.timezone.utc).date()
    start = dt.datetime.combine(today, dt.time.min, tzinfo=dt.timezone.utc)
    async with _pool.acquire() as c:
        total = await c.fetchval("SELECT COUNT(*) FROM users")
        active = await c.fetchval("SELECT COUNT(*) FROM users WHERE is_active=TRUE AND is_banned=FALSE")
        joined_today = await c.fetchval(
            "SELECT COUNT(*) FROM events WHERE kind='join' AND at>=$1", start)
        left_today = await c.fetchval(
            "SELECT COUNT(*) FROM events WHERE kind='leave' AND at>=$1", start)
        movies = await c.fetchval("SELECT COUNT(*) FROM movies")
        prem = await c.fetchval("SELECT COUNT(*) FROM premium WHERE until>now()")
    return {
        "total": total or 0,
        "active": active or 0,
        "joined_today": joined_today or 0,
        "left_today": left_today or 0,
        "movies": movies or 0,
        "premium": prem or 0,
    }


# ═══════════════════════════════════════════════════════════════════
#  MOVIES
# ═══════════════════════════════════════════════════════════════════
async def add_movie(code: str, title: str, caption: str, file_id: str, file_type: str) -> bool:
    async with _pool.acquire() as c:
        try:
            await c.execute(
                "INSERT INTO movies(code,title,caption,file_id,file_type) VALUES($1,$2,$3,$4,$5)",
                code, title, caption, file_id, file_type,
            )
            return True
        except asyncpg.UniqueViolationError:
            return False


async def get_movie(code: str) -> Optional[dict]:
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT * FROM movies WHERE code=$1", code)
        if row:
            await c.execute("UPDATE movies SET views=views+1 WHERE code=$1", code)
    return dict(row) if row else None


async def delete_movie(code: str) -> bool:
    async with _pool.acquire() as c:
        res = await c.execute("DELETE FROM movies WHERE code=$1", code)
    return res.endswith("1")


async def list_movies(limit: int = 50) -> list[dict]:
    async with _pool.acquire() as c:
        rows = await c.fetch(
            "SELECT code,title,views FROM movies ORDER BY created_at DESC LIMIT $1", limit)
    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════════
#  MAJBURIY KANALLAR
# ═══════════════════════════════════════════════════════════════════
async def add_channel(chat_id: str, title: str, link: str, join_type: str) -> None:
    async with _pool.acquire() as c:
        await c.execute(
            "INSERT INTO channels(chat_id,title,link,join_type) VALUES($1,$2,$3,$4)",
            chat_id, title, link, join_type,
        )


async def del_channel(ch_id: int) -> None:
    async with _pool.acquire() as c:
        await c.execute("DELETE FROM channels WHERE id=$1", ch_id)


async def list_channels() -> list[dict]:
    async with _pool.acquire() as c:
        rows = await c.fetch("SELECT * FROM channels ORDER BY id")
    return [dict(r) for r in rows]


async def save_join_request(user_id: int, chat_id: str) -> None:
    async with _pool.acquire() as c:
        await c.execute(
            "INSERT INTO join_requests(user_id,chat_id) VALUES($1,$2) "
            "ON CONFLICT DO NOTHING",
            user_id, chat_id,
        )


async def has_join_request(user_id: int, chat_id: str) -> bool:
    async with _pool.acquire() as c:
        row = await c.fetchrow(
            "SELECT 1 FROM join_requests WHERE user_id=$1 AND chat_id=$2",
            user_id, chat_id)
    return row is not None


# ═══════════════════════════════════════════════════════════════════
#  PREMIUM
# ═══════════════════════════════════════════════════════════════════
async def grant_premium(user_id: int, days: int) -> dt.datetime:
    now = dt.datetime.now(dt.timezone.utc)
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT until FROM premium WHERE user_id=$1", user_id)
        base = row["until"] if row and row["until"] > now else now
        new_until = base + dt.timedelta(days=days)
        await c.execute(
            "INSERT INTO premium(user_id,until) VALUES($1,$2) "
            "ON CONFLICT (user_id) DO UPDATE SET until=$2, updated_at=now()",
            user_id, new_until,
        )
    return new_until


async def is_premium(user_id: int) -> bool:
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT until FROM premium WHERE user_id=$1", user_id)
    return bool(row and row["until"] > dt.datetime.now(dt.timezone.utc))


async def premium_until(user_id: int) -> Optional[dt.datetime]:
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT until FROM premium WHERE user_id=$1", user_id)
    return row["until"] if row else None


async def premium_user_ids() -> list[int]:
    async with _pool.acquire() as c:
        rows = await c.fetch("SELECT user_id FROM premium WHERE until>now()")
    return [r["user_id"] for r in rows]


# ═══════════════════════════════════════════════════════════════════
#  PAYMENTS
# ═══════════════════════════════════════════════════════════════════
async def create_payment(user_id: int, plan: str, method: str, amount: str) -> int:
    async with _pool.acquire() as c:
        pid = await c.fetchval(
            "INSERT INTO payments(user_id,plan,method,amount) VALUES($1,$2,$3,$4) RETURNING id",
            user_id, plan, method, amount,
        )
    return pid


async def attach_receipt(pid: int, file_id: str) -> None:
    async with _pool.acquire() as c:
        await c.execute("UPDATE payments SET receipt_id=$2 WHERE id=$1", pid, file_id)


async def set_payment_status(pid: int, status: str) -> Optional[dict]:
    async with _pool.acquire() as c:
        row = await c.fetchrow(
            "UPDATE payments SET status=$2 WHERE id=$1 RETURNING *", pid, status)
    return dict(row) if row else None


async def get_payment(pid: int) -> Optional[dict]:
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT * FROM payments WHERE id=$1", pid)
    return dict(row) if row else None


# ═══════════════════════════════════════════════════════════════════
#  ADMINS
# ═══════════════════════════════════════════════════════════════════
async def is_admin(tg_id: int) -> bool:
    if tg_id in OWNER_IDS:
        return True
    async with _pool.acquire() as c:
        row = await c.fetchrow("SELECT 1 FROM admins WHERE telegram_id=$1", tg_id)
    return row is not None


async def add_admin(tg_id: int) -> None:
    async with _pool.acquire() as c:
        await c.execute(
            "INSERT INTO admins(telegram_id) VALUES($1) ON CONFLICT DO NOTHING", tg_id)


async def del_admin(tg_id: int) -> None:
    if tg_id in OWNER_IDS:
        return  # owner o'chmaydi
    async with _pool.acquire() as c:
        await c.execute("DELETE FROM admins WHERE telegram_id=$1", tg_id)


async def list_admins() -> list[int]:
    async with _pool.acquire() as c:
        rows = await c.fetch("SELECT telegram_id FROM admins ORDER BY added_at")
    ids = [r["telegram_id"] for r in rows]
    for oid in OWNER_IDS:
        if oid not in ids:
            ids.insert(0, oid)
    return ids
