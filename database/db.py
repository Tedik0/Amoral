import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("vpn.db")
cursor = conn.cursor()


def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        username TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        tariff TEXT,
        expiry_date TEXT
    )
    """)

    conn.commit()


# ✅ Добавить пользователя
def add_user(tg_id, username):
    cursor.execute("""
    INSERT OR IGNORE INTO users (tg_id, username)
    VALUES (?, ?)
    """, (tg_id, username))
    conn.commit()


# ✅ Добавить подписку
def add_subscription(tg_id, tariff, days):
    expiry_date = datetime.now() + timedelta(days=days)

    cursor.execute("""
    INSERT INTO subscriptions (tg_id, tariff, expiry_date)
    VALUES (?, ?, ?)
    """, (tg_id, tariff, expiry_date.strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()