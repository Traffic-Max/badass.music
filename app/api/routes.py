from fastapi import APIRouter
from app.api import music_moderation
from app import main

router = APIRouter()

@router.get("/unpublished_track")
async def get_unpublished_track():
    return await main.get_unpublished_track()


@router.post("/add_track")
async def add_track(track_data: dict):
    return await main.add_new_track(track_data)


@router.patch("/publish_track/{track_name}")
async def publish_track(track_name: str):
    return await main.publish_track(track_name)


@router.post("/add_tracks_from_folder")
async def add_tracks_from_folder():
    return await main.add_tracks_from_folder()
