import asyncio
import os
import re
from typing import Dict, Any, List, Tuple
import time
from .names_cleaner import AI_Music_Generator
import pysnooper

import mimetypes

from sqlalchemy import select
from sqlalchemy.orm import Session
from .bot import Bot, upload_file_to_telegram

BOT_APITOKEN = os.environ.get('BOT_TOKEN')
bot_instance = Bot(BOT_APITOKEN) # type: ignore

from mutagen import File # type: ignore
from pydub.utils import mediainfo
import librosa
import numpy as np

from database.models import add_track_to_db, get_db_session, AudioTrack
# import bot

from dotenv import load_dotenv

load_dotenv()

channel_hiphop = 'badass.hiphop'
channel_electronic = 'badass.electronic'


@pysnooper.snoop()            
def ai_rename_files_in_directory(directory_path):
    generator = AI_Music_Generator()
    file_paths = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    print(file_paths)
    cleaned_track_infos = generator.clean_folder_tracks([os.path.basename(file_path) for file_path in file_paths])
    for i, file_path in enumerate(file_paths):
        if i >= len(cleaned_track_infos):
            break
        cleaned_track_info = cleaned_track_infos[i]
        if cleaned_track_info:
            new_file_path = os.path.join(os.path.dirname(file_path), cleaned_track_info)
            if not os.path.isdir(new_file_path):
                os.rename(file_path, new_file_path)
                print(f"Файл '{file_path}' переименован в '{cleaned_track_info}'")
        print('[!] Sleep... ')
        time.sleep(20)
        
        
def is_track_unique(artist: str, title: str, session: Session) -> bool:
    """Проверяем, существует ли запись с таким артистом и названием"""
    
    existing_track = session.query(AudioTrack.id).filter((AudioTrack.artist == artist) & (AudioTrack.title == title)).scalar()
    return existing_track is None
        
        
def get_track_metadata(audio: File, filename: str) -> Dict[str, Any]: # type: ignore
    """Извлекаем метаданные из файла"""
    
    artist_from_filename, title_from_filename = extract_artist_and_title_from_filename(os.path.basename(filename))

    metadata = {
        "track_name": audio.get("TIT2", title_from_filename).text[0] if audio.get("TIT2") else title_from_filename,
        "artist": audio.get("TPE1", artist_from_filename).text[0] if audio.get("TPE1") else artist_from_filename,
        "title": audio.get("TIT2", None).text[0] if audio.get("TIT2") else None,
        "genre": audio.get("TCON", None).text[0] if audio.get("TCON") else None,
        "album": audio.get("§", None).text[0] if audio.get("TALB") else None,
        "release_year": int(audio.get("TDRC", None).text[0].split("-")[0]) if audio.get("TDRC") else None,
        "track_duration": None,
        "bitrate": None,
        "bpm": audio.get("TBPM", None).text[0] if audio.get("TBPM") else None,
        "key": audio.get("TKEY", None).text[0] if audio.get("TKEY") else None,
        "extra": None,
        "label": None,
    }

    if audio.info is not None:
        if audio.info.length is not None:
            metadata["track_duration"] = int(audio.info.length)
        if audio.info.bitrate is not None:
            metadata["bitrate"] = int(audio.info.bitrate)
    
    return metadata


def extract_artist_and_title_from_filename(filename: str) -> Tuple[str, str]:
    basename = os.path.basename(filename)
    without_ext = os.path.splitext(basename)[0]
    artist_and_title = re.split(" - ", without_ext, maxsplit=1)
    if len(artist_and_title) == 2:
        return artist_and_title[0], artist_and_title[1]
    else:
        return None, None # type: ignore


async def get_all_files_in_directory(path: str) -> List[str]:
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            files.append(file_path)
    return files


async def upload_files_from_directory(directory_path, bot_instance):
    """Загружаем треки в базу данных"""
    file_paths = await get_all_files_in_directory(directory_path)
    with get_db_session(database_url) as session:  # Добавьте это
        for file_path in file_paths:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None or not mime_type.startswith("audio"):
                print(f"Файл не является аудиофайлом: {file_path}")
                continue

            audio = File(file_path)
            if audio is None:
                print(f"Ошибка: не удалось открыть или обработать файл {file_path}")
                continue
            # print(audio)
            metadata = get_track_metadata(audio, file_path)  # Получаем метаданные трека

            # print(f"Processing file: {file_path}")
            # print(f"Metadata: {metadata}")
            
            file_id = await upload_file_to_telegram(bot_instance, file_path)  # Используйте эту строку вместо ошибочной

            channel_branch = channel_hiphop if metadata["genre"] == "Hip-Hop" else channel_electronic
            
            artist = metadata["artist"].strip() if metadata["artist"] else "Unknown"
            title = metadata["title"].strip() if metadata["title"] else "Unknown"

            
            if is_track_unique(artist, title, session):  # передайте сессию здесь
                # Добавляем трек в базу данных
                add_track_to_db(
                    track_name=metadata["track_name"],
                    artist=metadata["artist"],
                    title=metadata["title"],
                    genre=metadata["genre"],
                    channel_branch=channel_branch,  # Здесь замените на название вашего канала
                    metadata=metadata,
                    album=metadata.get("album"),
                    release_year=metadata.get("release_year"),
                    track_duration=metadata.get("track_duration"),
                    bitrate=metadata.get("bitrate"),
                    cover_art=metadata.get("cover_art"),
                    comments=metadata.get("comments"),
                    telegram_file_id=file_id,
                )
            else:
                continue
                


async def print_all_metadata_from_directory(directory_path):
    
    all_possible_fields = [
        "TIT2", "TPE1", "TRCK", "TALB", "TDRC", "TCON", "TSSE", "TIT3",
        "COMM", "TCOP", "TOPE", "TCOM", "TPOS", "TBPM", "TKEY", "TLAN",
        "WPAY", "WOAR", "AENC", "APIC", "ASPI", "COMM", "COMR", "ENCR",
        "EQU2", "ETCO", "GEOB", "GRID", "LINK", "MCDI", "MLLT", "OWNE",
        "PRIV", "PCNT", "POPM", "POSS", "RBUF", "RVA2", "RVRB", "SEEK",
        "SYLT", "SYTC", "TDEN", "TDLY", "TDOR", "TDRL", "TDTG", "TENC",
        "TEXT", "TFLT", "TIPL", "TIT1", "TKEY", "TLAN", "TLEN", "TMCL",
        "TMED", "TMOO", "TOAL", "TOFN", "TOLY", "TOPE", "TORY", "TOWN",
        "TPE2", "TPE3", "TPE4", "TPRO", "TPUB", "TRSN", "TRSO", "TSRC",
        "TSSE", "TSST", "TXXX", "UFID", "USER", "USLT", "WCOM", "WCOP",
        "WOAF", "WOAS", "WORS", "WPUB", "WXXX", "TDAT", "TIME", "TORY",
        "TRDA", "TSIZ", "TYER", "IPLS", "RVAD", "EQUA", "GEOB", "RVRB",
        "TDES", "TGID", "TSSO", "WFED", "PCST"
    ]

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


async def get_key_of_audio_files_in_directory(directory_path):
    """
    Возвращает тональность (ключ) каждого аудиофайла в заданной директории
    :param directory_path: путь к директории с аудиофайлами
    
    [!] Рабочая - определяет тональность если таковая определена.
    
    """
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac', '.m4a', '.ogg')):
                file_path = os.path.join(root, file)
                audio_info = mediainfo(file_path)
                if key := audio_info.get('TAG', {}).get('TKEY', ''):
                    print(f"Тональность файла {file}: {key}")
                else:
                    print(f"Тональность файла {file} не найдена")



def get_key_of_audio_file(audio_file_path):
    """Орпеделяю тональность в ее отсутствие. Три функции ниже."""
    
    try:
        y, sr = librosa.load(audio_file_path)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        pitches = np.zeros(12)
        for i in range(12):
            pitches[i] = np.sum(chroma[i])
        key = np.argmax(pitches)
        mode = 'major' if key < 6 else 'minor'
        tonic_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        tonic = tonic_names[key]
        return f'{tonic} {mode}' if tonic in tonic_names else ""
    except Exception as e:
        print(f"Ошибка при определении тональности: {e}")
        return ""


def analyze_directory(directory_path):
    tonalities = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac', '.m4a', '.ogg')):
                file_path = os.path.join(root, file)
                key = get_key_of_audio_file(file_path)
                file_name = str(file_path).split('/')[-1]
                """Конвертирую тональность в камелот """
                kamelot_key = convert_key_to_camelot(key)
                
                print(f"Тональность трека {file_name}: {kamelot_key}")
                
                tonalities.append(kamelot_key)
    
    return tonalities

                
                
def convert_key_to_camelot(key):
    """
    Преобразует название тональности в формат Camelot
    https://mixedinkey.com/harmonic-mixing-guide/
    """
    circle_of_fifths_sharps = ["A", "E", "B", "F#", "C#", "G#", "D#", "Bb", "F", "C", "G", "D"]
    circle_of_fifths_flats = ["F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb", "A", "D", "G", "C", "F"]
    tonic = key.split()[0]
    mode = key.split()[1]
    if (
        mode != "major"
        and mode == "minor"
        and tonic in circle_of_fifths_sharps
    ):
        return f"{circle_of_fifths_sharps.index(tonic)}B"
    elif mode != "major" and mode == "minor" and tonic in circle_of_fifths_flats:
        return f"{circle_of_fifths_flats.index(tonic)}A"
    elif mode != "major" and mode == "minor" or mode != "major":
        return "unknown"
    else:
        circle_of_fifths = ["C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F"]
        return f"{circle_of_fifths.index(tonic)}A" if tonic in circle_of_fifths else ""


async def main():
    
    """Запуск определения тональности"""
    loop = asyncio.get_event_loop()
    tonalities = await loop.run_in_executor(None, analyze_directory, "/Users/pwn.show/projects_garbage/badass_music_channel/music_moderator/I Love My Midwest Classics")
    for key in tonalities:
        if key == "unknown":
            print("Тональность не определена")
        else:
            print(key)

    await print_all_metadata_from_directory("/Users/pwn.show/projects_garbage/badass_music_channel/music_moderator")

    # print("Database dropped succesfully...")
    # drop_tables(database_url)


    # print("Tables created succesfully...")
    # create_tables(database_url)

if __name__ == "__main__":
    database_url = str(os.environ.get('DATABASE_URL'))
    asyncio.run(main())   


"""

new_track = AudioTrack(
        track_name=track_name, # Full-File name | TOFN: Original filename
        artist=artist, # TPE1
        title=title, # TIT2
        genre=genre, # TCON
        channel_branch=channel_branch,
        track_metadata=metadata,
        album=album, # TALB
        release_year=release_year, # TDRC
        track_duration=track_duration, # TLEN
        bitrate=bitrate, # TBPM
        cover_art=cover_art, # APIC
        comments=comments, # COMM
        telegram_file_id=telegram_file_id, # UFID
    )
    
    # TENC: Кодируется
    # WXXX: Определяемая пользователем рамка ссылки URL
    # TIT3: Субтитр
    # TKEY: Тональность
    # TOWN: Владелец файла
    # TPE4: Интерпретировано, ремикшировано или иным образом изменено
    # TPOS: Часть сета - интересно для диджеев
    # UFID: Уникальный идентификатор файла
    # WOAF: Официальная веб-страница аудиофайла
    # WOAS: Официальная веб-страница аудиоисточника
    # IPLS: Список вовлеченных лиц
    # WFED: URL подкаста
    
    # Not Meta Related
    id: Column[int] = 
    file_id: Column[str] = 
    status: Column[str] = 
    likes: Column[int] = 
    dislikes: Column[int] = 
    publish_date: Column[datetime] = 
    comments: Column[str] = 
    telegram_file_id: Column[str] = 
    channel_branch = 
    
    track_name: Column[str] = 
    artist: Column[str] = 
    title: Column[str] = 
    genre: Column[str] = 
    track_metadata: Column[dict] = 
    album: Column[str] = 
    release_year: Column[int] = 
    track_duration: Column[int] = 
    bitrate: Column[int] = 
    cover_art: Column[str] = 
    
    
AENC: Audio encryption
APIC: Attached picture (альбомная обложка)
ASPI: Audio seek point index
COMM: Comments
COMR: Commercial frame
ENCR: Encryption method registration
EQU2: Equalisation (2)
ETCO: Event timing codes
GEOB: General encapsulated object
GRID: Group identification registration
LINK: Linked information
MCDI: Music CD identifier
MLLT: MPEG location lookup table
OWNE: Ownership frame
PRIV: Private frame
PCNT: Play counter
POPM: Popularimeter
POSS: Position synchronisation frame
RBUF: Recommended buffer size
RVA2: Relative volume adjustment (2)
RVRB: Reverb
SEEK: Seek frame
SYLT: Synchronised lyric/text
SYTC: Synchronised tempo codes
TALB: Album
TBPM: Beats per minute
TCOM: Composer
TCON: Genre
TCOP: Copyright
TDEN: Encoding time
TDLY: Playlist delay
TDOR: Original release time
TDRC: Recording time
TDRL: Release time
TDTG: Tagging time
TENC: Encoded by
TEXT: Lyricist
TFLT: File type
TIPL: Involved people list
TIT1: Content group description
TIT2: Title
TIT3: Subtitle
TKEY: Initial key
TLAN: Language
TLEN: Length
TMCL: Musician credits list
TMED: Media type
TMOO: Mood
TOAL: Original album
TOFN: Original filename
TOLY: Original lyricist
TOPE: Original artist
TORY: Original release year
TOWN: File owner
TPE1: Artist
TPE2: Band/orchestra/accompaniment
TPE3: Conductor
TPE4: Interpreted, remixed, or otherwise modified by
TPOS: Part of a set
TPRO: Produced notice
TPUB: Publisher
TRCK: Track number
TRSN: Internet radio station name
TRSO: Internet radio station owner
TSRC: ISRC (international standard recording code)
TSSE: Software/hardware and settings used for encoding
TSST: Set subtitle
TXXX: User-defined text information
UFID: Unique file identifier
USER: Terms of use
USLT: Unsynchronised lyric/text transcription
WCOM: Commercial information
WCOP: Copyright/Legal information
WOAF: Official audio file webpage
WOAR: Official artist/performer webpage
WOAS: Official audio source webpage
WORS: Official internet radio station homepage
WPAY: Payment
WPUB: Publishers official webpage
WXXX: User-defined URL link frame
TDAT: Date
TIME: Time
TORY: Original release year
TRDA: Recording dates
TSIZ: Size
TYER: Year
IPLS: Involved people list
RVAD: Relative volume adjustment
EQUA: Equalization
GEOB: General encapsulated object
RVRB: Reverb
TDES: Podcast Description
TGID: Podcast Identifier
TSSO: Podcast Sort Order
WFED: Podcast Feed URL
PCST: Podcast Indicator
"""

"""
TPRO: Примечание о производстве
TPUB: Издатель
TRCK: Номер трека
TRSN: Название интернет-радиостанции
TRSO: Владелец интернет-радиостанции
TSRC: ISRC (международный стандартный код записи)
TSSE: Программное/аппаратное обеспечение и настройки используемые при кодировании
TSST: Субтитры
TXXX: Пользовательская информация
UFID: Уникальный идентификатор файла
USER: Условия использования
USLT: Транскрипция текста/текста песни без синхронизации
WCOM: Коммерческая информация
WCOP: Авторские права/юридическая информация
WOAF: Официальная веб-страница аудио файла
WOAS: Официальный источник аудио
WORS: Официальная веб-страница интернет-радиостанции
WPUB: Официальная веб-страница издателя
WXXX: Пользовательский URL-ссылочный фрейм
TDAT: Дата
TIME: Время
TORY: Оригинальный год выпуска
TRDA: Даты записи
TSIZ: Размер
TYER: Год
IPLS: Список участников
RVAD: Относительная корректировка громкости
EQUA: Эквалайзер
GEOB: Общий инкапсулированный объект
RVRB: Реверберация
TDES: Описание подкаста
TGID: Идентификатор подкаста
TSSO: Порядок сортировки подкаста
WFED: URL ленты подкаста
PCST: Индикатор подкаста
AENC: Зашифрование аудио
APIC: Прикрепленное изображение (альбомная обложка)
ASPI: Индекс точек поиска аудио
COMM: Комментарии
COMR: Коммерческий фрейм
ENCR: Регистрация метода шифрования
EQU2: Эквалайзер (2)
ETCO: Коды времени событий
GEOB: Общий инкапсулированный объект
GRID: Регистрация идентификации группы
LINK: Связанная информация
MCDI: Идентификатор музыкального CD
MLLT: MPEG таблица поиска местоположения
OWNE: Фрейм владения
PRIV: Частный фрейм
PCNT: Счетчик воспроизведения
POPM: Популярность
POSS: Фрейм синхронизации позиции
RBUF: Рекомендуемый размер буфера
RVA2: Относительное корректирование громкости (2)
RVRB: Реверберация
SEEK: Фрейм поиска
SYLT: Синхронизированный фрейм текста/текста песни
SYTC: Синхронизированный фрейм кодов темпа
TDEN: Время кодирования
TDLY: Задержка плейлиста
TDOR: Время первоначального релиза
TDRL: Время релиза
TDTG: Время тэгирования
TENC: Кодировано
TEXT: Текст песен
TFLT: Тип файла
TIPL: Список участников
TIT1: Описание группы содержимого
TIT2: Название
TIT3: Подзаголовок
TKEY: Начальный ключ
TLAN: Язык
TLEN: Длительность
TMCL: Список музыкантов
TMED: Тип носителя
TMOO: Настроение
TOAL: Оригинальный альбом
TOFN: Оригинальное имя файла
TOLY: Оригинальный автор текста песни
TOPE: Оригинальный исполнитель
TORY: Оригинальный год выпуска
TOWN: Владелец файла
TPE1: Исполнитель
TPE2: Группа/оркестр/сопровождение
TPE3: Дирижер
TPE4: Интерпретировано, переработано или иначе изменено
"""
