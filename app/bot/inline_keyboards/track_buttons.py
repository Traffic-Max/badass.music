from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def like_button(track_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❤️", callback_data=f"like:{track_id}"))
    return markup
