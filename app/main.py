import os
import asyncio
from typing import Dict

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException

from aiogram import executor
import logging
from app.database.models import db, database_url, AudioTrack, add_track_to_db, change_status_to_published, get_draft_track
from app.api.routes import router as api_router
from app.bot.bot import bot, dp, send_track
from app.api.music_moderation import process_and_upload_track
from app.database.utils import create_tables, drop_tables
import pysnooper
load_dotenv()


app = FastAPI()

app.include_router(api_router)

folder_path = os.environ.get('FOLDER_PATH')
admin_id = os.environ.get("TELEGRAM_ADMIN_ID")
BRANDING_DATA = {
    "channel_name": "☠️ badass.music.channel🎧",
    "channel_link": "https://t.me/badasschannel",
    "admin_nickname": "@badass_marketing",
    "branch": "hiphop",
}


@app.on_event("startup")
async def startup_event():
    """On Startup"""
    
    # await drop_tables(database_url)
    # await create_tables(database_url)
    
    await db.set_bind(database_url) 

    # Получение списка всех файлов с треками в заданной папке
    # track_files = [
    #     os.path.join(root, file)
    #     for root, _, files in os.walk(folder_path)
    #     for file in files
    #     if file.lower().endswith(('.mp3', '.flac', '.m4a', '.ogg'))
    # ]

    # Обработка и загрузка каждого трека
    # for file_path in track_files:
        # await process_and_upload_track(bot, file_path, BRANDING_DATA)

    await bot.send_message(chat_id=admin_id, text="Бот и приложение FastAPI запущены")

    asyncio.create_task(publish_track_periodically())

@app.on_event("shutdown")
async def shutdown_event():
    """On Shutdown"""
    
    await bot.send_message(chat_id=admin_id, text="Бот и приложение FastAPI остановлены")
    await bot.close()

    
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


async def publish_track_periodically():
    """Scheduling with aioschedule"""
    
    while True:
        track = await get_draft_track()
        if track:
            print(f"Track to send is: {track.title}")
            try:    
                print(f"Channel ID: {os.getenv('CHANNEL_ELECTRO_ID')}")

                await change_status_to_published(track.id)
                await send_track(bot=bot, track=track, channel_branch=BRANDING_DATA['branch'])
                print(f"Трек {track.track_name} опубликован.")
            except Exception as e:
                print(f"[!] Error while track publish: {e}")
        await asyncio.sleep(180)  # Частота публикации треков (в секундах)


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup_event())

    executor.start_polling(dp, loop=loop, on_startup=None, on_shutdown=shutdown_event)
    
    
# /home/pax/music_dir/test
# /home/pax/music_dir/test2