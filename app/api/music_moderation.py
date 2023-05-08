import os
import sys
import re
from typing import Dict, Any
import logging

from dotenv import load_dotenv
from fastapi import HTTPException
from mutagen import File

from aiogram import types
from aiogram.types import InputMediaPhoto, InputMediaAudio

from app.config import all_possible_meta_fields

from app.bot.bot import bot, upload_file_to_telegram
from app.database.models import add_track_to_db
from app.services.image_processor import get_random_image

import base64

load_dotenv()

# BRANDING_METADATA = os.environ.get('BRANDING_DATA')

# folder_path = input("Введите путь к папке с треками: ")

# # Проверьте, что папка существует
# if not os.path.isdir(folder_path):
#     print("Ошибка: указанная папка не существует")
#     sys.exit(1)

# # Задайте путь к папке с треками и ветку канала перед началом выполнения
# TRACKS_FOLDER = folder_path
folder_path = os.environ.get('FOLDER_PATH')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

channel_link = os.environ.get("CHANNEL_LINK")
channel_admin = os.environ.get("ADMIN_USERNAME")
channel_name = os.environ.get("CHANNEL_NAME")


def print_all_metadata(audio: File):
    print("[ DEBUG ] Metadata BEFORE processing")
    
    all_possible_fields = all_possible_meta_fields
    print("Все возможные метаданные:")
    for field in audio:
        if field in all_possible_fields:
            value = audio.get(field)
            if (
                value is not None
                and "APIC" not in field
                and not field.startswith("----:com.apple.metadata:artwork")
            ):
                print(f"{field}: {value}")
    print("\n")
    
    
def print_metadata_after_processing(metadata: Dict[str, Any]):
    print("[ DEBUG ] Metadata AFTER processing")
    for key, value in metadata.items():
        print(f"{key}: {value}")
    print("\n")
    

def process_metadata(audio: File, branding_metadata: Dict[str, str], filename: str) -> Dict[str, Any]:
    """Extract and process metadata from track"""
    print("Start processing...")
    # Если исполнитель или название не существуют в метаданных, получаем их из имени файла
    artist_from_filename, title_from_filename = extract_artist_and_title_from_filename(os.path.basename(filename))

    # Сохраняем обложку, если она существует
    cover_art = None
    for tag in audio.tags:
        if tag.startswith("APIC:"):
            cover_art = audio[tag].data
            break
    else:
        print("[!] Cover not exist")

    metadata = {
        "track_name": f"{artist_from_filename} - {title_from_filename}",
        "artist": audio.get("TPE1").text[0] if audio.get("TPE1") and hasattr(audio.get("TPE1"), "text") else artist_from_filename,
        "title": audio.get("TIT2", None).text[0] if audio.get("TIT2") and hasattr(audio.get("TIT2"), "text") else title_from_filename,
        "genre": audio.get("TCON", None).text[0] if audio.get("TCON") and hasattr(audio.get("TCON"), "text") else None,
        "album": audio.get("TALB", None).text[0] if audio.get("TALB") and hasattr(audio.get("TALB"), "text") else None,
        "release_year": int(str(audio.get("TDRC", None).text[0]).split("-")[0]) if audio.get("TDRC") and hasattr(audio.get("TDRC"), "text") else None,
        
        "track_duration": int(audio.info.length) if audio.info.length is not None else None,
        "bitrate": int(audio.info.bitrate) if audio.info.bitrate is not None else None,
        "bpm": audio.get("TBPM", None).text[0] if audio.get("TBPM") else None,
        "ton_key": audio.get("TKEY", None).text[0] if audio.get("TKEY") else None,
        
        "label": None,
        "cover_art": cover_art,
        "extra": None,
        "comments": audio.get("COMM", None).text[0] if audio.get("COMM") and hasattr(audio.get("COMM"), "text") else None,
        "channel_name": branding_metadata["channel_name"],
        "channel_link": branding_metadata["channel_link"],
        "admin_nickname": branding_metadata["admin_nickname"],
        "branch": branding_metadata["branch"],
    }

    # Замена информации об исполнителе и названии трека
    artist = metadata["artist"]
    title = metadata["title"]

    if branding_metadata["channel_name"] not in artist:
        artist = f"{artist_from_filename} | {branding_metadata['channel_name']}"
    if branding_metadata["admin_nickname"] not in title:
        title = f"{title_from_filename} | {branding_metadata['admin_nickname']} | {branding_metadata['channel_link']}"

    audio["TPE1"].text[0] = artist
    audio["TIT2"].text[0] = title

    # Обновление словаря metadata
    metadata["artist"] = artist
    metadata["title"] = title
    
    # Добавление информации в комментарии
    if audio.get("COMM"):
        new_comment = f"{metadata['comments']} | Augmented music channel {channel_name} \n| Admin {channel_admin} invites you \n| to follow link {channel_link}"
        audio["COMM"].text[0] = new_comment
        metadata["comments"] = new_comment
        
        # Проверка длительности трека и битрейта, если они существуют
    if audio.info is not None:
        if audio.info.length is not None:
            metadata["track_duration"] = int(audio.info.length)
        else:
            print("[!] Длительность трека не обработана")
        if audio.info.bitrate is not None:
            metadata["bitrate"] = int(audio.info.bitrate)
        else:
            print("[!] Битрейт трека не обработан")

    return metadata


def extract_artist_and_title_from_filename(filename: str):
    # Удаляем расширение файла
    name_without_ext = os.path.splitext(filename)[0]

    # Создаем регулярное выражение для поиска исполнителя и названия трека
    pattern = re.compile(r"(.*?)\s*[-,]\s*(.*)")

    # Ищем совпадения в имени файла
    match = pattern.match(name_without_ext)

    if match:
        # Если совпадения найдены, извлекаем исполнителя и название трека
        artist = match.group(1).strip()
        title = match.group(2).strip()
    else:
        # Разделяем имя файла по символу " - "
        parts = name_without_ext.split("-")
        if len(parts) == 2:
            artist = parts[0].strip()
            title = parts[1].strip()
        else:
            artist = "Unknown Artist"
            title = "Unknown Title"

    return artist, title


async def print_all_metadata_from_directory(directory_path):
    
    all_possible_fields = all_possible_meta_fields

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac', '.m4a', '.ogg')):
                file_path = os.path.join(root, file)
                audio = File(file_path)

                print(f"Все возможные метаданные для файла {file}:")
                for field in audio: # type: ignore
                    if field in all_possible_fields:
                        value = audio.get(field) # type: ignore
                        if (
                            value is not None
                            and "APIC" not in field
                            and not field.startswith(
                                "----:com.apple.metadata:artwork"
                            )
                        ):
                            print(f"{field}: {value}")
                print("\n")
                
                
async def process_and_upload_track(bot, file_path, branding_metadata):
    logger.info(f"Начало обработки трека: {file_path}")
    # Обработка метаданных трека
    audio = File(file_path)
    metadata = process_metadata(audio, branding_metadata, file_path)
    logger.info("Завершена обработка метаданных")
    # Загрузка трека на сервер Телеграм и получение ID файла
    telegram_file_id = await upload_file_to_telegram(bot, file_path)

    if "cover_art" in metadata:
        metadata["cover_art"] = base64.b64encode(metadata["cover_art"]).decode()
    else:
        metadata["cover_art"] = None
    
    # Сохранение ID телеграма вместо локального пути файла
    metadata["telegram_file_id"] = telegram_file_id
    logger.info(f"Получен идентификатор файла в Телеграм: {metadata['telegram_file_id']}")
    # Сохранение метаданных в базе данных
    track = await add_track_to_db(
        track_name=metadata["track_name"],
        artist=metadata["artist"],
        title=metadata["title"],
        genre=metadata["genre"],
        channel_branch=metadata["branch"],
        metadata=metadata,
        album=metadata["album"],
        release_year=metadata["release_year"],
        track_duration=metadata["track_duration"],
        bitrate=metadata["bitrate"],
        ton_key=metadata["ton_key"],
        cover_art=metadata["cover_art"],
        comments=metadata["comments"],
        telegram_file_id=metadata["telegram_file_id"],
    )
    
    logger.info(f"Трек {file_path} успешно обработан и сохранен в базе данных")





"""
hiphop
TIT2: Белый - Я Разъебу Весь Мир (luwqp Q
TPE1: loowqp Q
TRCK: 012
TALB: Tomkos
TDRC: 2019-04-26 09




electro
TIT2: Adriatique - Hound (Original Mix)
TPE1: Underground Deep-Tech STATION
TRCK: 13
TALB: Must Have 2 / DTS
TDRC: 2019-06-21 17
TCON: Melodic House & Techno

"""



"""
Шаблон регулярного выражения, который я использовал, состоит из следующих частей:

(.*?): этот фрагмент соответствует любому количеству 
символов (за исключением символа новой строки), но как можно меньше. 
Здесь используется нежадный квантификатор *?. Эта часть 
выражения находит имя исполнителя.

\s*[-,]\s*: здесь \s* означает любое количество пробельных символов 
(включая пробелы, табуляции и переносы строк). [-,] соответствует 
либо символу -, либо символу ,. Вместе эта часть выражения ищет разделитель 
между именем исполнителя и названием трека, который может быть окружен 
пробелами или другими пробельными символами.

(.*): этот фрагмент соответствует любому количеству символов 
(за исключением символа новой строки). 
Эта часть выражения находит название трека.

"""