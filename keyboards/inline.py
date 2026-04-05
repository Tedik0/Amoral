from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def tariffs_kb(show_trial=False):
    buttons = []
    if show_trial:
        buttons.append([InlineKeyboardButton(text="🎁 Попробовать 7 дней (бесплатно)", callback_data="buy_trial")])

    buttons.extend([
        [InlineKeyboardButton(text="💳 1 месяц — 50₽", callback_data="buy_1")],
        [InlineKeyboardButton(text="💳 3 месяца — 100₽", callback_data="buy_3")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def check_payment_kb(label):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Проверить оплату", callback_data=f"check_{label}")]
    ])


def main_menu_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Личный кабинет", callback_data="menu_profile")], # Оставили только ЛК
        [InlineKeyboardButton(text="Инструкции 💡", callback_data="menu_instructions"),
         InlineKeyboardButton(text="Партнёрка 💫", callback_data="menu_referral")],
        [InlineKeyboardButton(text="О проекте 🌍", callback_data="menu_about"),
         InlineKeyboardButton(text="Связь 📲", callback_data="menu_contact")]
    ])


def profile_kb(has_sub=False):
    buttons = []
    if has_sub:
        # Если подписка есть, даем возможность продлить
        buttons.append([InlineKeyboardButton(text="🔄 Продлить подписку", callback_data="menu_tariffs")])
    else:
        # Если нет — купить
        buttons.append([InlineKeyboardButton(text="💳 Купить подписку", callback_data="menu_tariffs")])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="main_menu")]
    ])