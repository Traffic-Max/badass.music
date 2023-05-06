import os
from aiogram import Bot, types
from aiogram.utils import exceptions
from aiogram.dispatcher import Dispatcher
from aiogram.types.input_file import InputFile
import asyncio

from dotenv import load_dotenv

# Импортируем модели и функции для работы с базой данных
from models import AudioTrack, add_track_to_db

load_dotenv()

# Токен бота
BOT_API_TOKEN = os.environ.get('BOT_TOKEN')
channel_id = os.environ.get('CHANNEL_ID')
branch = 'badass.electronic'

# Директория с аудио файлами
AUDIO_DIRECTORY = "/Users/pwn.show/projects_garbage/badass_music_channel/music_moderator/ARTBAT's DJ Mix"

# Создаем объект бота и диспетчер
bot = Bot(token=BOT_API_TOKEN) # type: ignore
dp = Dispatcher(bot)

# Функция для загрузки аудиофайлов и добавления информации в базу данных
async def upload_audio_tracks_to_telegram_and_db():
    # Проходимся по всем файлам в директории и ее поддиректориях
    for dirpath, _, filenames in os.walk(AUDIO_DIRECTORY):
        for filename in filenames:
            # Полный путь к файлу
            filepath = os.path.join(dirpath, filename)
            # Получаем информацию о файле
            file_stat = os.stat(filepath)
            print(file_stat)
            # Если размер файла равен 0, то пропускаем его
            if file_stat.st_size == 0:
                continue
            # Открываем файл и читаем его содержимое
            with open(filepath, 'rb') as audio_file:
                audio_content = audio_file.read()
            # Создаем объект InputFile из содержимого файла
            audio_input_file = InputFile(audio_content, filename=filename) # type: ignore
            print(audio_input_file)
            # Отправляем файл на сервер Telegram
            try:
                message = await bot.send_audio(chat_id=channel_id, audio=audio_input_file) # type: ignore
            except exceptions.TelegramAPIError as e:
                print(f'Error uploading file {filepath} to Telegram: {e}')
                continue
            # Добавляем информацию о треке в базу данных
            track = await add_track_to_db(
                track_name=filename,
                telegram_file_id=message.audio.file_id,
                artist='unknown',
                title='unknown',
                genre='unknown',
                channel_branch=branch,
                comments='testing schedule posting',
            )
            print(f'Track {filename} uploaded to Telegram and added to database')

if __name__ == '__main__':
    # Запускаем цикл загрузки аудиофайлов в Telegram и добавления информации в базу данных
    asyncio.run(upload_audio_tracks_to_telegram_and_db()) # type: ignore











# """Post scheduler imports"""
# from gino import Gino
# from datetime import datetime, timedelta
# from models import AudioTrack, PostTemplate, PostCover

# import aiogram
# from aiogram import Bot, types
# from aiogram.dispatcher import Dispatcher

# import schedule
# import time

# """Add tracks to db imports"""
# import os
# import asyncio
# import glob
# from pathlib import Path


# API_TOKEN = 'YOUR_API_TOKEN_HERE'
# CHANNEL_NAME = 'YOUR_CHANNEL_NAME_HERE'

# bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot)

# db = Gino()

# async def get_next_track_to_publish():
#     return (
#         await AudioTrack.query.where(AudioTrack.published == 'draft')
#         .order_by(AudioTrack.id)
#         .limit(1)
#         .gino.first()
#     )


# async def publish_next_track():
#     track = await get_next_track_to_publish()
#     if track:
#         post_template = await PostTemplate.query.where(PostTemplate.template_id == 1).gino.first()
#         post_cover = await PostCover.query.where(PostCover.post_id == post_template.template_id).gino.first()

#         audio = types.Audio(
#             track.telegram_file_id,
#             performer=track.artist,
#             title=track.title,
#             caption=post_template.template_description,
#             parse_mode=types.ParseMode.HTML,
#             duration=track.track_duration
#         )
#         buttons = types.InlineKeyboardMarkup()
#         like_button = types.InlineKeyboardButton(text='👍', callback_data=f'like_{track.id}')
#         dislike_button = types.InlineKeyboardButton(text='👎', callback_data=f'dislike_{track.id}')
#         buttons.add(like_button, dislike_button)

#         try:
#             await bot.send_photo(
#                 chat_id=CHANNEL_NAME,
#                 photo=post_cover.cover_file_id,
#                 caption=post_template.template_description,
#                 reply_markup=buttons
#             )
#             await bot.send_audio(chat_id=CHANNEL_NAME, audio=audio)
#             track.published = True
#             track.published_at = datetime.now()
#             await track.update().apply()
#         except aiogram.exceptions.TelegramAPIError as e:
#             print(f'Error publishing track {track.track_name}: {e}')


# # schedule.every(2).hours.do(publish_next_track)

# # while True:
# #     schedule.run_pending()
# #     time.sleep(1)


# async def add_tracks_from_directory_to_db(directory_path: str, channel_branch: str):
#     # Получить все файлы в директории
#     files = list(glob.glob(f'{directory_path}/**/*.*', recursive=True))

#     for file_path in files:
#         # Проверяем, является ли файл аудиофайлом
#         if Path(file_path).suffix.lower() in ['.mp3', '.wav', '.flac']:
#             # Получаем имя файла без расширения
#             track_name = os.path.splitext(os.path.basename(file_path))[0]

#             # Проверяем, есть ли уже трек с таким именем в базе данных
#             if await AudioTrack.query.where(AudioTrack.track_name == track_name).gino.first():
#                 print(f'Трек {track_name} уже есть в базе данных.')
#                 continue

#             # Добавляем трек в базу данных
#             print(f'Добавление трека {track_name} в базу данных...')
#             await add_track_to_db(
#                 track_name=track_name,
#                 artist='',
#                 title='',
#                 genre='',
#                 channel_branch=channel_branch,
#                 telegram_file_id='',
#             )
#     print('Добавление треков в базу данных завершено.')
    
    
# async def main():
#     await db.set_bind(database_url)
#     # добавьте путь к папке с треками и ветку канала, в который нужно опубликовать треки.
#     await add_tracks_from_directory_to_db('path/to/directory', 'channel_branch')
#     # другие функции, если это необходимо

