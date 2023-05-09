from aiogram import types, Bot, dp

from app.bot.menu_commands import user_menu


@dp.message_handler(commands=['user'])
async def send_user_menu(message: types.Message):
    await user_menu(message)
