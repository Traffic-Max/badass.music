import os
import time
import schedule
import asyncio
import random
import tempfile

import logging
from dotenv import load_dotenv

from aiogram import Bot, executor, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.types.input_media import InputMediaPhoto, InputMediaAudio

import mutagen

from database.models import AudioTrack, get_db_session


from app.services.ai_processor import BAdAIntelligentAss

load_dotenv()

database_url = str(os.environ.get('DATABASE_URL'))

music_folder = ''

photos_folder = ''
image = random.choice(os.listdir(photos_folder))

# Configure logging
logging.basicConfig(level=logging.INFO)

API_TOKEN = os.environ.get('BOT_TOKEN')
channel_id_work = os.environ.get('CHANNEL_ID')
admin_id = os.environ.get('ADMIN_ID')
session_work = get_db_session(database_url)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN) # type: ignore
dp = Dispatcher(bot)

music_descriptor = BAdAIntelligentAss()

# music_files = os.listdir(music_folder)
# photos_files = os.listdir(photos_folder)

track = '/Users/pwn.show/Desktop/ALTE/22-25/Carlos Pires - Floating Flowers [Cause Org Records].mp3'

async def read_metadata(file_path):
    tag = TinyTag.get(file_path)
    file_size = os.path.getsize(file_path)

    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                break
            size /= 1024.0
        return f"{size:.1f} {unit}"

    def format_channels(channels):
        if channels == 1:
            return 'Mono'
        elif channels == 2:
            return 'Stereo'
        else:
            return f'Dolby ({channels})'

    metadata = (
        f"Альбом: {tag.album}\n"
        f"Артист альбома: {tag.albumartist}\n"
        f"Артист: {tag.artist}\n"
        f"Битрейт: {tag.bitrate} кбит/с\n"
        f"Каналы: {format_channels(tag.channels)}\n"
        f"Комментарии: {tag.comment}\n"
        f"Композитор: {tag.composer}\n"
        f"Длительность: {int(tag.duration)} сек\n"
        f"Формат: MP3\n"
        f"Размер: {format_size(file_size)}\n"
        f"Жанр: {tag.genre}\n"
        f"Лейбл: {tag.extra.get('label')}\n"
        f"Тональность: {tag.extra.get('key')}\n"
        f"Частота дискретизации: {tag.samplerate} Гц\n"
        f"Битовая глубина: {tag.bitdepth}\n"
        f"Название трека: {tag.title}\n"
        f"Номер трека: {tag.track}\n"
        f"Всего треков: {tag.track_total}\n"
        f"Год: {tag.year}\n"
    )

    return metadata


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
async def send_track(message: types.Message, chat_id=channel_id_work, session=session_work):
    # Получаем неопубликованный трек из базы данных
    track = get_unpublished_track()
    if not track:
        # Обработка случая, когда нет неопубликованных треков
        return

    # Меняем статус трека на опубликованный
    track.status = 'published'  # type: ignore
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
        metadata = await read_metadata(tmp_file.name)
        print(metadata)
    await bot.send_message(chat_id=message.chat.id, text=metadata)



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


async def start_bot():
    # file_id = await upload_track_to_tg(track)
    # print(f"Трек загружен в Telegram, {file_id}")
    await executor.start_polling(dp, skip_updates=True) # type: ignore


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


async def upload_file_to_telegram(bot, file_path) -> str:
    with open(file_path, "rb") as file:
        input_file = types.InputFile(file)
        message = await bot.send_audio(chat_id=admin_id, audio=input_file)
        return message.audio.file_id
    
    

async def on_startup(dp):
    await bot.send_message(chat_id=admin_id, text="Бот запущен") # type: ignore

async def on_shutdown(dp):
    await bot.send_message(chat_id=admin_id, text="Бот остановлен") # type: ignore

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

    
    
    