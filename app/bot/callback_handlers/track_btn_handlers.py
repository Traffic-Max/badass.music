from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from app.bot.bot import dp
from app.database.models import add_liked_track_to_user


@dp.callback_query_handler(lambda call: call.data.startswith("like:"))
async def process_like_callback(call: CallbackQuery, state: FSMContext):
    track_id = int(call.data.split(":")[1])
    telegram_id = call.from_user.id
    await add_liked_track_to_user(telegram_id, track_id)
    await call.answer("Трек добавлен в список понравившихся")
