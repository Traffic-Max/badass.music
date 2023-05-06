from sqlalchemy.orm import Session
from typing import List, Dict
from base import AudioTrack
from base import SessionLocal

def get_tracks_info(db: Session) -> List[Dict[str, str]]:
    tracks = db.query(AudioTrack).all()
    track_count = len(tracks)
    
    print(f"Количество треков в базе данных: {track_count}")

    track_info_list = []
    for track in tracks:
        track_info = {
            "id": track.id,
            "track_name": track.track_name,
            "artist": track.artist,
            "title": track.title,
            "genre": track.genre,   
            "status": track.status,
            "likes": track.likes,
            "dislikes": track.dislikes,
            "publish_date": track.publish_date,
            "track_metadata": track.track_metadata,
            "album": track.album,
            "release_year": track.release_year,
            "track_duration": track.track_duration,
            "bitrate": track.bitrate,
            "lyrics": track.lyrics,
            "cover_art": track.cover_art,
            "comments": track.comments,
            "telegram_file_id": track.telegram_file_id
        }
        track_info_list.append(track_info)

    return track_info_list


db = SessionLocal()
track_info_list = get_tracks_info(db)

for track_info in track_info_list:
    print(track_info)
