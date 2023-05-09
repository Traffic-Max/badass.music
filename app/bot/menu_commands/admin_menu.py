"""А саме хуй зна нашо мені меню адміна в боті якшо можу вище зразу робити собі дашборд
Але хай буде для інших адмінів"""
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def admin_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("Statistics", callback_data="stats"), 
                 InlineKeyboardButton("Publish post", callback_data="publish"),
                 InlineKeyboardButton("Upload Tracks from folder", callback_data="upload")
                )

    await message.reply("Admin Menu", reply_markup=keyboard)
    
    