import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("vpn.db")
cursor = conn.cursor()


def init_db():
    # Добавляем reg_date для статистики
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        username TEXT,
        reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_banned INTEGER DEFAULT 0
    )
    """)
    # Добавляем цену в подписки, чтобы считать доход
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        tariff TEXT,
        expiry_date TEXT,
        uuid TEXT,
        amount INTEGER DEFAULT 0 
    )
    """)
    conn.commit()

def get_admin_stats():
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE expiry_date > datetime('now')")
    active_subs = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM subscriptions")
    total_revenue = cursor.fetchone()[0] or 0
    return total_users, active_subs, total_revenue



# ✅ Добавить пользователя
def add_user(tg_id, username):
    cursor.execute("""
    INSERT OR IGNORE INTO users (tg_id, username)
    VALUES (?, ?)
    """, (tg_id, username))
    conn.commit()


# ✅ Добавить подписку
def add_subscription(tg_id, tariff, days, user_uuid):
    expiry_date = datetime.now() + timedelta(days=days)
    cursor.execute("""
    INSERT INTO subscriptions (tg_id, tariff, expiry_date, uuid)
    VALUES (?, ?, ?, ?)
    """, (tg_id, tariff, expiry_date.strftime("%Y-%m-%d %H:%M:%S"), user_uuid))

    conn.commit()


def get_full_subscription(tg_id):
    cursor.execute("SELECT tariff, expiry_date, uuid FROM subscriptions WHERE tg_id = ? ORDER BY id DESC LIMIT 1", (tg_id,))
    return cursor.fetchone()


def get_user_subscription(tg_id):
    cursor.execute("""
    SELECT tariff, expiry_date FROM subscriptions 
    WHERE tg_id = ? ORDER BY id DESC LIMIT 1
    """, (tg_id,))
    return cursor.fetchone()


def has_used_trial(tg_id):
    cursor.execute("SELECT id FROM subscriptions WHERE tg_id = ? AND tariff = 'trial'", (tg_id,))
    return cursor.fetchone() is not None


def get_user_uuid(tg_id):
    # Предполагаем, что ты добавил колонку uuid в таблицу users или хранишь её в подписках.
    # Для простоты возьмем последний UUID из таблицы subscriptions
    cursor.execute("SELECT tariff, expiry_date FROM subscriptions WHERE tg_id = ? ORDER BY id DESC LIMIT 1", (tg_id,))
    return cursor.fetchone()