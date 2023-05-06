import os
import time
import schedule

from dotenv import load_dotenv

from typing import Dict

from fastapi import FastAPI, HTTPException
from app.config import DATABASE_URL
from app.database.utils import create_tables, get_db_session
from app.database.models import db, database_url, AudioTrack, add_track_to_db, change_status_to_published, get_draft_track
import asyncio
from app.database.db_init import init_db
from app.api.routes import router as api_router

from app.bot.bot import send_track


load_dotenv()

TRACKS_FOLDER = os.getenv('TRACKS_FOLDER')
database_url = str(os.environ.get('DATABASE_URL'))

app = FastAPI()

app.include_router(api_router)

@app.on_event("startup")
async def startup():
    # await create_tables(database_url)
    # Загружаем треки из папки в базу данных при запуске приложения
    await db.set_bind(database_url) 
    await add_tracks_from_folder()
    
    asyncio.create_task(publish_track_periodically())  # Запускаем периодическую публикацию треков

    
async def add_tracks_from_folder():
    for filename in os.listdir(TRACKS_FOLDER):
        if filename.endswith(".mp3"):
            track_path = os.path.join(TRACKS_FOLDER, filename) # type: ignore
            # Здесь вы можете извлечь информацию из файла трека, например, с помощью библиотеки mutagen
            # Используйте функцию add_track_to_db для добавления трека в базу данных
            await add_track_to_db(track_name=filename, artist="Unknown", title="Unknown", genre="Unknown", channel_branch="badass.electronic.sound")


@app.post("/tracks/")
async def add_new_track(track_data: Dict):
    """Add track to db with post and JSON body
    Example of body:
        {
            "track_name": "2pac - hit em up",
            "artist": "2pac",
            "title": "hit em up",
            "genre": "Rap",
            "channel_branch": "badass.electronic.sound"
        }
"""
    track = await add_track_to_db(**track_data)
    if not track:
        raise HTTPException(status_code=400, detail="Трек с таким названием уже существует.")
    return track

    

@app.get("/tracks/unpublished/")
async def get_unpublished_track():
    track = await get_draft_track()
    if track:
        return track
    raise HTTPException(status_code=404, detail="Неопубликованный трек не найден.😢")


@app.put("/tracks/{track_name}/publish/")
async def publish_track(track_name: str):
    print(track_name)
    status = await change_status_to_published(track_name)
    if not status:
        raise HTTPException(status_code=404, detail="Трек не найден.😢")
    return {"status": status}


@app.get("/tracks/all")
async def get_all_tracks():
    tracks = await AudioTrack.query.gino.all()
    return tracks


"""Scheduling with aioschedule"""
async def publish_track_periodically():
    while True:
        track = await get_draft_track()
        if track:
            await change_status_to_published(track.track_name)
            print(f"Трек {track.track_name} опубликован.")
        await asyncio.sleep(60)  # Частота публикации треков (в секундах)

