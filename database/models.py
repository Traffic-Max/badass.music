import os
from datetime import datetime
from typing import Optional, Dict, Any, Union
from gino import Gino
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text
from sqlalchemy.sql import func

from dotenv import load_dotenv

load_dotenv()

database_url = str(os.environ.get('DATABASE_URL'))

db = Gino()

class DJ(db.Model):
    __tablename__ = "djs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dj_bio = Column(String, nullable=True)


class Playlist(db.Model):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True, index=True)
    dj_id = Column(Integer, ForeignKey("djs.id"), nullable=True)
    name = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AudioTrack(db.Model):
    __tablename__ = "audio_tracks"

    id = Column(Integer, primary_key=True, index=True)
    track_name = Column(String, unique=True)
    file_id = Column(String, unique=True)
    artist = Column(String)
    title = Column(String)
    genre = Column(String)
    status = Column(String, default="draft")
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    publish_date = Column(DateTime(timezone=True), server_default=func.now())
    track_metadata = Column(JSON, nullable=True)
    album = Column(String, nullable=True)
    release_year = Column(Integer, nullable=True)
    track_duration = Column(Integer, nullable=True)
    bitrate = Column(Integer, nullable=True)
    cover_art = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    telegram_file_id = Column(String, nullable=True)
    channel_branch = Column(String, nullable=False)
    
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=True)


class PostTemplate(db.Model):
    __tablename__ = "post_templates"

    template_id = Column(Integer, primary_key=True, index=True)
    track_artist = Column(String, nullable=True)
    track_title = Column(String, nullable=True)
    template_description = Column(Text, nullable=True)
    hashtags = Column(String, nullable=True)
    cta_text = Column(String, nullable=True)
    emojis = Column(Text, nullable=True)


class PostCover(db.Model):
    __tablename__ = "post_covers"

    cover_id = Column(Integer, primary_key=True, index=True)
    cover_file_id = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("post_templates.template_id"))


"""Functions for database async Interaction"""

async def add_track_to_db(
    track_name: str,
    artist: str,
    title: str,
    genre: str,
    channel_branch: str,
    metadata: Optional[Dict[str, Any]] = None,
    album: Optional[str] = None,
    release_year: Optional[int] = None,
    track_duration: Optional[int] = None,
    bitrate: Optional[int] = None,
    cover_art: Optional[str] = None,
    comments: Optional[str]= None,
    telegram_file_id: Optional[str] = None,
    ) -> Union[AudioTrack, None]:
    if await AudioTrack.query.where(AudioTrack.track_name == track_name).gino.first():
        return None

    return await AudioTrack.create(
        track_name=track_name,
        artist=artist,
        title=title,
        genre=genre,
        channel_branch=channel_branch,
        track_metadata=metadata,
        album=album,
        release_year=release_year,
        track_duration=track_duration,
        bitrate=bitrate,
        cover_art=cover_art,
        comments=comments,
        telegram_file_id=telegram_file_id,
    )


async def change_status_to_published(track_name: str):
    track = await AudioTrack.query.where(AudioTrack.track_name == track_name).gino.first()
    if track:
        await track.update(status="published").apply()
        return track.status


async def get_unpublished_track():
    return await AudioTrack.query.where(AudioTrack.status == "draft").gino.first()


async def get_db_session(database_url: str):
    await db.set_bind(database_url)


async def drop_tables(database_url: str):
    await db.set_bind(database_url)
    await db.gino.drop_all() # type: ignore
    


async def create_tables(database_url: str):
    await db.set_bind(database_url)
    await db.gino.create_all() # type: ignore
    
    
    
async def main():
    await db.set_bind(database_url)
    # db.drop_all()
    # print("Tables dropped")
    # db.create_all() # type: ignore
    # print("Tables created")
    
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
