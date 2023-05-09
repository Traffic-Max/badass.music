import os

from dotenv import load_dotenv
from app.bot.bot import dp

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.builtin import CommandFilter

load_dotenv()

admin_id = os.environ.get('ADMIN_ID')

class IsAdminFilter(CommandFilter):
    async def check_filter(self, message: types.Message) -> bool:
        return message.from_user.id == int(admin_id)

dp.filters_factory.bind(IsAdminFilter, event_handlers=[dp.message_handlers])

