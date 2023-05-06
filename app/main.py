import os
import time
import schedule

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from app.config import DATABASE_URL
from app.database.utils import create_tables, get_db_session
from app.database.models import db, database_url, AudioTrack, add_track_to_db, change_status_to_published, get_draft_track


load_dotenv()

TRACKS_FOLDER = os.getenv('TRACKS_FOLDER')

app = FastAPI()


@app.on_event("startup")
async def startup():
    # Загружаем треки из папки в базу данных при запуске приложения
    await db.set_bind(database_url)
    await add_tracks_from_folder()
    
async def add_tracks_from_folder():
    for filename in os.listdir(TRACKS_FOLDER):
        if filename.endswith(".mp3"):
            track_path = os.path.join(TRACKS_FOLDER, filename) # type: ignore
            # Здесь вы можете извлечь информацию из файла трека, например, с помощью библиотеки mutagen
            # Используйте функцию add_track_to_db для добавления трека в базу данных
            await add_track_to_db(track_name=filename, artist="Unknown", title="Unknown", genre="Unknown", channel_branch="badass.hiphop")


@app.get("/tracks/")
async def add_new_track(track_data):
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
    status = await change_status_to_published(track_name)
    if not status:
        raise HTTPException(status_code=404, detail="Трек не найден.😢")
    return {"status": status}


@app.get("/tracks/all")
async def get_all_tracks():
    tracks = await AudioTrack.query.gino.all()
    return tracks


    
    
