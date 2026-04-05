import asyncio
import random
import uuid

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import ADMIN_ID
from config import (
    BOT_TOKEN, YOOMONEY_WALLET, YOOMONEY_TOKEN,
    XUI_URL, XUI_USERNAME, XUI_PASSWORD, INBOUND_ID
)
# Добавь новые функции в импорт
from keyboards.inline import tariffs_kb, check_payment_kb, main_menu_inline, back_to_menu_kb, profile_kb
from keyboards.admin_inline import admin_main_kb
from services.yoomoney import create_payment_link, check_payment
from services.xui_client import XUIClient

from database.db import get_admin_stats
from database.db import init_db, add_user, add_subscription
from database.db import get_user_subscription, has_used_trial, get_full_subscription

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
xui = XUIClient(XUI_URL, XUI_USERNAME, XUI_PASSWORD)

# --- ТВОИ ТАРИФЫ (Примерно 28-я строка) ---
TARIFFS = {
    "trial": {"price": 0, "days": 7, "name": "Пробный период"}, # Вставляй СЮДА
    "1": {"price": 50, "days": 30, "name": "1 месяц"},
    "3": {"price": 100, "days": 90, "name": "3 месяца"},
    "12": {"price": 500, "days": 365, "name": "1 год"}
}


# --- ОБРАБОТКА МЕНЮ ---

@dp.message(Command("start"))
@dp.callback_query(F.data == "main_menu")
async def start(event):
    text = "<b>I'm Amoral</b>" \
           "\n\nУ меня появился всой серивис, написанный своими ручками" \
           "\n\n!!! VPN находится в разработке, чтобы получить доступ нажимате \n<b>Проверить оплату и вам выдадут ключ</b>" \
           "\nЕсли будут какие-то проблемы с vpn-ом, жду фитбека @tediko"
    if isinstance(event, Message):
        await event.answer(text, reply_markup=main_menu_inline())
    else:
        await event.message.edit_text(text, reply_markup=main_menu_inline())


# Обнови обработку вызова тарифов
@dp.callback_query(F.data == "menu_tariffs")
async def show_tariffs(callback: CallbackQuery):
    trial_used = has_used_trial(callback.from_user.id)
    # Показываем кнопку триала, если пользователь еще не пользовался им
    await callback.message.edit_text(
        "🚀 <b>Выберите подходящий тариф:</b>",
        reply_markup=tariffs_kb(show_trial=not trial_used)
    )


# Добавь новый тариф в словарь TARIFFS (в начале bot.py)
# TARIFFS = { "trial": {"price": 0, "days": 7, "name": "Пробный период"}, ... }

@dp.callback_query(F.data == "buy_trial")
async def activate_trial(callback: CallbackQuery):
    tg_id = callback.from_user.id

    if has_used_trial(tg_id):
        await callback.answer("❌ Вы уже использовали пробный период", show_alert=True)
        return

    await callback.message.edit_text("⏳ Активирую ваш пробный период...")

    user_name = callback.from_user.username or "no_name"
    user_email = f"trial_{tg_id}"
    user_uuid = str(uuid.uuid4())

    if xui.add_client(INBOUND_ID, user_uuid, user_email, days=7):
        vpn_link = xui.get_link(INBOUND_ID, user_uuid, f"Trial_{user_name}")
        add_user(tg_id, user_name)
        add_subscription(tg_id, "trial", 7, user_uuid)  # Записываем в БД

        await callback.message.answer(
            f"🎁 <b>Пробный период активирован!</b>\n\n"
            f"Вам доступно 7 дней VPN.\n\n"
            f"Твой ключ:\n<code>{vpn_link}</code>",
            reply_markup=main_menu_inline()
        )
    else:
        await callback.message.answer("❌ Ошибка при создании доступа. Попробуйте позже.")


@dp.callback_query(F.data == "menu_instructions")
async def instructions(callback: CallbackQuery):
    text = (
        "<b>💡 Инструкция по подключению:</b>\n\n"
        "1. Скопируйте ключ, который выдаст бот.\n"
        "2. Скачайте приложение:\n"
        "   • Android: <b>v2rayNG</b>\n"
        "   • iOS: <b>Streisand</b> или Shadowrocket\n"
        "   • PC: <b>v2rayN</b>\n"
        "3. В приложении нажмите '+' и выберите 'Импорт из буфера'."
    )
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb())


@dp.callback_query(F.data == "menu_referral")
async def referral(callback: CallbackQuery):
    await callback.message.edit_text(
        "💫 <b>Партнёрская программа</b>\n\n🚧 В разработке... Совсем скоро здесь появится ваша реферальная ссылка!",
        reply_markup=back_to_menu_kb())


@dp.callback_query(F.data == "menu_about")
async def about(callback: CallbackQuery):
    text = (
        "🌍 <b>О проекте</b>\n\n"
        "Еу еу еу, пока сыро криво, но будет все дорабатываться\n"
        "Проект создан исключительно для ознакомления с технологией"
    )
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb())


@dp.callback_query(F.data == "menu_contact")
async def contact(callback: CallbackQuery):
    await callback.message.edit_text("📲 <b>Связь с поддержкой</b>\n\nПо всем вопросам пишите: @tediko",
                                     reply_markup=back_to_menu_kb())


# bot.py

@dp.callback_query(F.data == "menu_profile")
async def show_profile(callback: CallbackQuery):
    tg_id = callback.from_user.id
    # Получаем данные вместе с UUID
    sub = get_full_subscription(tg_id)

    if sub:
        tariff, expiry, user_uuid = sub
        user_name = callback.from_user.username or "user"

        # Генерируем ссылку заново по сохраненному UUID
        vpn_link = xui.get_link(INBOUND_ID, user_uuid, f"VPN_{user_name}")

        text = (
            f"👤 <b>Личный кабинет</b>\n\n"
            f"🆔 Ваш ID: <code>{tg_id}</code>\n"
            f"💎 Тариф: <b>{tariff}</b>\n"
            f"📅 Истекает: <code>{expiry}</code>\n\n"
            f"🔑 <b>Ваш ключ:</b>\n<code>{vpn_link}</code>\n\n"
            f"<i>Вы можете продлить подписку, нажав кнопку ниже.</i>"
        )
        await callback.message.edit_text(text, reply_markup=profile_kb(has_sub=True))
    else:
        text = (
            "👤 <b>Личный кабинет</b>\n\n"
            "У вас пока нет активных подписок. Подключитесь, чтобы получить доступ к VPN."
        )
        await callback.message.edit_text(text, reply_markup=profile_kb(has_sub=False))

# --- ТВОЯ ЛОГИКА ПОКУПКИ (С НЕБОЛЬШИМИ ПРАВКАМИ ПОД EDIT_TEXT) ---


@dp.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_panel(message: Message):
    await message.answer("🛠 <b>Панель управления Amoral VPN</b>", reply_markup=admin_main_kb())


@dp.callback_query(F.data == "admin_stats", F.from_user.id == ADMIN_ID)
async def show_admin_stats(callback: CallbackQuery):
    total, active, money = get_admin_stats()
    text = (
        "📊 <b>Статистика сервиса:</b>\n\n"
        f"👥 Всего пользователей: <b>{total}</b>\n"
        f"⚡️ Активных подписок: <b>{active}</b>\n"
        f"💰 Общий доход: <b>{money} ₽</b>"
    )
    await callback.message.edit_text(text, reply_markup=admin_main_kb())


@dp.callback_query(F.data.startswith("buy_"))
async def buy(callback: CallbackQuery):
    tariff_key = callback.data.split("_")[1]
    tariff_data = TARIFFS.get(tariff_key)

    amount = tariff_data["price"]
    label = f"{callback.from_user.id}_{tariff_key}_{random.randint(1000, 9999)}"
    pay_url = create_payment_link(amount, label, YOOMONEY_WALLET)

    await callback.message.edit_text(
        f"💳 <b>Оплата тарифа: {tariff_data['name']}</b>\n"
        f"К оплате: <b>{amount}₽</b>\n\n"
        f"Ссылка на оплату:\n{pay_url}",
        reply_markup=check_payment_kb(label)
    )


@dp.callback_query(F.data.startswith("check_"))
async def check(callback: CallbackQuery):
    label = callback.data.split("_", 1)[1]
    await callback.answer("⏳ Проверяем...")

    try:
        is_paid = check_payment(YOOMONEY_TOKEN, label)
    except Exception:
        await callback.message.answer("❌ Ошибка связи с ЮMoney. Попробуйте еще раз.")
        return

    if is_paid:
        parts = label.split("_")
        tg_id, tariff_key = int(parts[0]), parts[1]
        days = TARIFFS[tariff_key]["days"]

        user_name = callback.from_user.username or "no_name"
        user_email = f"tg_{tg_id}_{user_name}"[:32]
        user_uuid = str(uuid.uuid4())

        await callback.message.edit_text(f"✅ Оплата подтверждена! Создаю профиль...")

        if xui.add_client(INBOUND_ID, user_uuid, user_email, days=days):
            vpn_link = xui.get_link(INBOUND_ID, user_uuid, f"VPN_{user_name}")
            add_user(tg_id, user_name)

            add_subscription(tg_id, tariff_key, days, user_uuid)

            await callback.message.answer(
                f"🎉 <b>Подписка активирована!</b>\n\n"
                f"Твой ключ:\n<code>{vpn_link}</code>",
                reply_markup=main_menu_inline()  # Возвращаем меню
            )
        else:
            await callback.message.answer("❌ Ошибка панели.")
    else:
        await callback.answer("❌ Платёж не найден", show_alert=True)


async def main():
    init_db()
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())