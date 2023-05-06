from typing import List
from sqlalchemy.orm import Session
from base import AudioTrack, SessionLocal


def get_db() -> Session: # type: ignore
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_all_tracks(db: Session) -> List[AudioTrack]:
    return db.query(AudioTrack).all()


def fetch_data_and_show_stats(db: Session):
    tracks = get_all_tracks(db)

    if not tracks:
        print("Нет записанных данных")
        return

    total_tracks = len(tracks)
    total_artists = len({track.artist for track in tracks})
    total_genres = len({track.genre for track in tracks})

    print(f"Всего треков: {total_tracks}")
    print(f"Всего артистов: {total_artists}")
    print(f"Всего жанров: {total_genres}")

    # Выводим статистику по артистам
    artists_stat = {}
    for track in tracks:
        if track.artist not in artists_stat:
            artists_stat[track.artist] = 1
        else:
            artists_stat[track.artist] += 1

    print("\nСтатистика по артистам:")
    for artist, count in artists_stat.items():
        print(f"{artist}: {count}")

    # Выводим статистику по жанрам
    genres_stat = {}
    for track in tracks:
        if track.genre not in genres_stat:
            genres_stat[track.genre] = 1
        else:
            genres_stat[track.genre] += 1

    print("\nСтатистика по жанрам:")
    for genre, count in genres_stat.items():
        print(f"{genre}: {count}")


def show_all_tracks(db: Session):
    tracks = get_all_tracks(db)

    if not tracks:
        print("Нет записанных данных")
        return

    print("\nСписок всех треков:")
    for track in tracks:
        _extracted_from_show_all_tracks_10(track)


# TODO Rename this here and in `show_all_tracks`
def _extracted_from_show_all_tracks_10(track):
    print(f"ID: {track.id} \n")
    print(f"Артист: {track.artist} \n")
    print(f"Название: {track.title} \n")
    print(f"Жанр: {track.genre} \n")
    print(f"Битрейт: {track.bitrate} \n")
    print(f"Продолжительность: {track.track_duration} сек. \n")
    print(f"Статус: {track.status} \n")
    print(f"Метаданные: {track.track_metadata} \n")
    print(f"Альбом: {track.status} \n")
    print(f"Лирикс?: {track.lyrics} \n")
    print(f"Телеграм айди: {track.telegram_file_id} \n")
    print(f"Ветка канала: {track.channel_branch} \n")


if __name__ == "__main__":
    db = next(get_db()) # type: ignore

    while True:
        print("\nВыберите опцию:")
        print("1. Вывести статистику")
        print("2. Показать все треки")
        print("3. Выход")
        user_choice = input("Введите номер опции: ")

        if user_choice == "1":
            fetch_data_and_show_stats(db)
        elif user_choice == "2":
            show_all_tracks(db)
        elif user_choice == "3":
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор, попробуйте снова.")
