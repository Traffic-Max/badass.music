import os
import time
import openai
from dotenv import load_dotenv
import pysnooper


load_dotenv()

openai.api_key = os.environ.get('OPENAI_API_KEY')

class AI_Music_Generator:
    def __init__(self):
        self.openai = openai

    # @pysnooper.snoop()
    def new_rename_files_in_directory(self, directory_path):
        file_paths = self._get_mp3_file_paths(directory_path)
        raw_titles = [os.path.basename(file_path) for file_path in file_paths]
        cleaned_track_info_dict = self.new_clean_tracks_with_ai(raw_titles)

        for file_path in file_paths:
            raw_title = os.path.basename(file_path)
            if cleaned_track_info := cleaned_track_info_dict.get(raw_title):
                new_file_path = os.path.join(os.path.dirname(file_path), cleaned_track_info.strip())
                if not os.path.isdir(new_file_path):
                    os.rename(file_path, new_file_path)
                    print(f"Файл '{file_path}' переименован в '{cleaned_track_info}'")

    # print('[!] Sleep... ')
    # time.sleep(20)

    def _get_mp3_file_paths(self, directory_path):
        file_paths = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".mp3"):
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)
        print("GET PATHS DONE")
        return file_paths

    def new_clean_tracks_with_ai(self, raw_titles):
        print("[!] Cleaning process begin...")

        cleaned_titles = []

        messages = [
            {
                "role": "system",
                "content": "Очистите названия композиций от лишних слов, цифр и символов, оставив только имя исполнителя и название трека в формате 'artist - title.mp3'. Название должно содержать не более четырех слов до знака '-' и не более четырех слов после знака '-', а также заканчиваться на '.mp3'. Исправляй кодировку если она слоvамна либо отображается неверно. Без коментариев. Если название композиции содержит имя исполнителя или нескольких исполнителей, все имена исполнителей должны быть сохранены в названии композиции. Ваш ответ должен содержать только очищенные названия композиций без символа '->' и без добавления нового имени файла. Очистите каждое из представленных названий файлов и возвращайте их по одному, разделенными символом новой строки. В любом возможной ситуации твой ответ должен содержать ТОЛЬКО название композиции, измененное либо нет."
            }
        ]

        messages.extend(
            {
                "role": "user",
                "content": f"Очистите название композиции: '{raw_title}'.",
            }
            for raw_title in raw_titles
        )
        response = self.openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=2000,
            n=1,
            stop=None,
            temperature=0.4
        )

        # Извлекаем очищенные названия из последнего сообщения с ролью "assistant"
        last_assistant_message = response['choices'][0]['message']['content'] # type: ignore
        cleaned_titles = last_assistant_message.split('\n')

        # Удаляем пустые строки из списка
        cleaned_titles = list(filter(None, cleaned_titles))

        return dict(zip(raw_titles, cleaned_titles))



generator = AI_Music_Generator()
generator.new_rename_files_in_directory("/Users/pwn.show/projects_garbage/badass_music_channel/music_preprocessor/preprocess_data/Cahoots2907")
