import os
import tempfile
import time
import logging
from dotenv import load_dotenv

from aiogram import Bot, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from app.database.models import get_draft_track

from database.models import get_db_session


from app.services.ai_processor import BAdAIntelligentAss


load_dotenv()

database_url = str(os.environ.get('DATABASE_URL'))

music_folder = ''

# photo_url = get_random_image('cyberpunk-music')

API_TOKEN = os.environ.get('BOT_TOKEN')
channel_id_work = os.environ.get('CHANNEL_ID')
admin_id = os.environ.get('ADMIN_ID')
channel_electro = os.environ.get('CHANNEL_ELECTRO_ID')
channel_hiphop = os.environ.get('CHANNEL_HIPHOP_ID')
session_work = get_db_session(database_url)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN) # type: ignore
dp = Dispatcher(bot)

music_descriptor = BAdAIntelligentAss()

# music_files = os.listdir(music_folder)
# photos_files = os.listdir(photos_folder)

# track = '/Users/pwn.show/Desktop/ALTE/22-25/Carlos Pires - Floating Flowers [Cause Org Records].mp3'


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")
    

# v0pdzW2UdQc
@dp.message_handler(commands=['share'])
async def share_youtube_video(message: types.Message):
    youtube_url = "https://www.youtube.com/watch?v=v0pdzW2UdQc"
    await bot.send_message(chat_id=channel_id_work, text=youtube_url) # type: ignore
    

@dp.message_handler(commands=['music'])
async def send_audio_post(message: types.Message, chat_id=channel_id_work, session=session_work):
    
    track_data = await get_draft_track(track)
    
    caption = f"🎧 {track_data['artist']} - {track_data['title']} \n\n 🌐 {track_data['channel_branch']}"
    
    
    with open(track_data["track_path"], "rb") as track_file:
        await bot.send_audio(chat_id=os.getenv("TELEGRAM_CHANNEL_ID"), audio=track_file, caption=caption)
    
    # Меняем статус трека на опубликованный
    track_file.status = 'published'  # type: ignore
    session.commit()

    # Создаем пост с использованием MusicDescriptor
    post = music_descriptor.generate_music_post(track.artist, track.title)

    # Создаем кнопки встроенной клавиатуры и добавляем их на клавиатуру
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(*[InlineKeyboardButton(text, callback_data=data) for text, data in [('👍', 'like'), ('👎', 'dislike')]])

    # Отправляем пост в канал
    await bot.send_message(chat_id, post)  # type: ignore

    # Отправляем аудиофайл с кнопками встроенной клавиатуры
    audio_file_id = track.file_id
    await bot.send_audio(chat_id, audio=audio_file_id, reply_markup=inline_kb)  # type: ignore


@dp.message_handler(content_types=types.ContentType.AUDIO)
async def get_audio_metadata(message: types.Message):
    file_id = message.audio.file_id
    file_info = await bot.get_file(file_id)
    file_bytes = await bot.download_file(file_info.file_path)
    print(f"{file_id}")
    
    # Создаем временный файл для сохранения аудиофайла
    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        # Записываем аудиофайл во временный файл
        tmp_file.write(file_bytes.getvalue())
        tmp_file.flush()

        # Получаем метаданные аудиофайла
        # metadata = await read_metadata(tmp_file.name)
        # print(metadata)
    # await bot.send_message(chat_id=message.chat.id, text=metadata)


async def upload_file_to_telegram(bot, file_path) -> str:
    with open(file_path, "rb") as file:
        input_file = types.InputFile(file)
        message = await bot.send_audio(chat_id=admin_id, audio=input_file)
        time.sleep(5)
        return message.audio.file_id


async def send_track(bot, track, channel_branch):
    """Send single audio file to channel"""
    
    # Используйте значение channel_branch для определения идентификатора канала
    channel_id = channel_electro if channel_branch == "electro" else channel_hiphop
    await bot.send_audio(audio=track.telegram_file_id, chat_id=channel_id)
    
    
async def on_startup(dp):
    await bot.send_message(chat_id=os.getenv("TELEGRAM_ADMIN_ID"), text="Бот запущен")

async def on_shutdown(dp):
    await bot.send_message(chat_id=os.getenv("TELEGRAM_ADMIN_ID"), text="Бот остановлен")
    
    
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

    
    
    
    
    
# @dp.message_handler(commands=['upload'])
# async def upload_tracks_to_tg():
#     directory = '/Users/pwn.show/Desktop/ALTE/22-25/'
#     for filename in os.listdir(directory):
#         if filename.endswith('.mp3'):
#             with open(os.path.join(directory, filename), 'rb') as audio_file:
#                 # Загружаем трек в Telegram и возвращаем file_id
#                 result = await bot.send_audio(chat_id=channel_id_work, audio=audio_file)  # type: ignore
#                 file_id = result.audio.file_id

#                 # Записываем данные о треке в базу данных
#                 track = AudioTrack(
#                     artist='Исполнитель',  # Замените это настоящими данными об исполнителе
#                     title='Название трека',  # Замените это настоящими данными о названии трека
#                     file_id=file_id,
#                     status='unpublished'
#                 )
#                 session.add(track)
#                 session.commit()

#                 print(f"Трек {filename} загружен в Telegram, file_id: {file_id}")


# async def start_bot():
#     # file_id = await upload_track_to_tg(track)
#     # print(f"Трек загружен в Telegram, {file_id}")
#     await executor.start_polling(dp, skip_updates=True) # type: ignore


# @dp.callback_query_handler(lambda c: c.data == 'like')
# async def process_callback_like(callback_query: types.CallbackQuery):
#     session = SessionLocal()  # Открываем новую сессию SQLAlchemy
#     try:
#         track_name = "example_track_name"  # Замените на имя трека, для которого был нажат лайк
#         likes = increment_likes(track_name, session)
#         await bot.answer_callback_query(callback_query.id, text=f"You liked the track! Total likes: {likes}")
#     finally:
#         session.close()  # Закрываем сессию SQLAlchemy

# @dp.callback_query_handler(lambda c: c.data == 'dislike')
# async def process_callback_dislike(callback_query: types.CallbackQuery):
#     session = SessionLocal()  # Открываем новую сессию SQLAlchemy
#     try:
#         track_name = "example_track_name"  # Замените на имя трека, для которого был нажат дизлайк
#         # genre = "example_genre"  # Замените на жанр трека
#         dislikes = increment_dislikes(track_name)
#         await bot.answer_callback_query(callback_query.id, text=f"You disliked the track! Total dislikes: {dislikes}")
#     finally:
#         session.close()  # Закрываем сессию SQLAlchemy

