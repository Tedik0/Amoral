from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мои ключи / Оплата 💳", callback_data="menu_tariffs")],
        [InlineKeyboardButton(text="Инструкции 💡", callback_data="menu_instructions"),
         InlineKeyboardButton(text="Партнёрка 💫", callback_data="menu_referral")],
        [InlineKeyboardButton(text="О проекте 🌍", callback_data="menu_about"),
         InlineKeyboardButton(text="Связь 📲", callback_data="menu_contact")]
    ])

def back_to_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="main_menu")]
    ])