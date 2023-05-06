import os
import time
import sys
import pysnooper

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from trash.ai_generator import AI_Music_Generator
from music_moderator.base_adder import get_key_of_audio_files_in_directory

dirty_tracks_folder = "/Users/pwn.show/projects_garbage/badass_music_channel/music_moderator/I Love My Midwest Classics/half"


"""1st stage names cleaning"""
@pysnooper.snoop()
def ai_clean_track_names(dirty_tracks_folder):
    generator = AI_Music_Generator()
    file_paths = []
    for root, dirs, files in os.walk(dirty_tracks_folder):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    print("Track names before cleaning:", [os.path.basename(file_path) for file_path in file_paths])
    cleaned_tracks = generator.clean_folder_tracks([os.path.basename(file_path) for file_path in file_paths])
    # cleaned_tracks = [f"cleaned_{os.path.basename(file_path)}" for file_path in file_paths]

    for i, file_path in enumerate(file_paths):
        if i >= len(cleaned_tracks):
            break
        if cleaned_track := cleaned_tracks[i]:
            new_file_path = os.path.join(os.path.dirname(file_path), cleaned_track)
            if not os.path.isdir(new_file_path):
                os.rename(file_path, new_file_path)
                print(f"File '{file_path}' is renamed to '{cleaned_track}'")
        print('[!] Sleep...')
        time.sleep(20)


"""2nd stage metadata processing"""

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






if __name__ == '__main__':
    ai_clean_track_names(dirty_tracks_folder)


