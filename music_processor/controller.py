"""
TKEY Determinator - get_key_of_audio_files_in_directory
Show all files in directore metadata - print_all_metadata_from_directory
Upload files to telegram server adn add data to database - upload_files_from_directory
Show single track metadata - get_track_metadata
Clean filenames in directory - ai_rename_files_in_directory (need to clean by stack about 10-15 files beacuse of openai maximum tokens restriction)
Define file genre with ai if exists - ai_genre_generator

"""
import sys
from music_moderator.names_cleaner import AI_Music_Generator
from music_moderator.base_adder import (
    get_all_files_in_directory,
    get_key_of_audio_files_in_directory,
    print_all_metadata_from_directory,
    
)
""" Controller draft """
from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/get_key_of_audio_files")
async def get_key_of_audio_files(directory: str):
    result = await get_key_of_audio_files_in_directory(directory)
    return {"result": result}

@app.get("/print_all_metadata")
async def print_all_metadata(directory: str):
    result = await print_all_metadata_from_directory(directory)
    return {"result": result}

@app.get("/upload_files")
async def upload_files(directory: str):
    result = await upload_files_from_directory(directory) # type: ignore
    return {"result": result}

# @app.get("/get_track_metadata")
# async def get_single_track_metadata(track_path: str):
#     result = await get_track_metadata(track_path)
#     return {"result": result}

# @app.post("/ai_rename_files")
# async def ai_rename_files(directory: str):
#     result = await ai_rename_files_in_directory(directory)
#     return {"result": result}

# @app.post("/ai_genre_generator")
# async def ai_genre_generator_endpoint(track_path: str):
#     result = await ai_genre_generator(track_path)
#     return {"result": result}
