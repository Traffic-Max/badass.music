import json
import os
import time
import openai
from dotenv import load_dotenv

from typing import Tuple, List


load_dotenv()

openai.api_key = os.environ.get('OPENAI_API_KEY')


class BAdAIntelligentAss():
    def __init__(self) -> None:
        self.openai = openai
        
        
        def generate_music_post(self, artist, title):
            message = [
                {"role": "system", "content": "Вы - маркетинговый специалист с многолетним опытом и ведущий сео специалист, специализируетесь на создании интересных, релевантных и привлекательных хэштегов, описаний и определении музыкального жанра для музыкальных композиций и их продвижении."},
                {"role": "user", "content": f"Создайте привлекательное описание, перечень эффективных хештегов, определите музыкальный жанр и оформите красивый пост для музыкальной композиции, когдая говорю красивый пост, это значит что он должен быть оформлен в Markdown, иметь красивый emoji styling, и привлекательную сруктуру. Это должен быть полностью готовый впечатляющий пост, не требующий дополнительного редактирования, поэтому никакого лишнего текста типа 'Пост:', 'Описание:' и т.д. пожалуйста. Жанр публикуй с '#' как хештег. Вкратце презентуй исполнителя и его творчество. Говори от первого лица в репрезентативном молодежном стиле. Учитывай что трек уже под этим постом. Кпопки 'лайк' и 'дизлайк' тоже там, так что пусть голосуют, мы следим за статистикой -  это поможет нам публиковать более ориентированный контент. Исполнитель: {artist}, Название трека: {title}"}
            ]
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message,
                max_tokens=300,
                n=1,
                stop=None,
                temperature=0.8
            )
            
            content = response['choices'][0]['message']['content'] # type: ignore

            with open(f'{artist}_music_post.json', 'w') as f:
                json.dump(response, f)
                print(response)
            time.sleep(20)
            return content


    def generate_lyrics(self, theme, genre, artist_style):
        message = [
            {"role": "system", "content": "Вы - талантливый автор песен с многолетним опытом, специализируетесь на создании текстов песен в разных музыкальных жанрах и стилях."},
            {"role": "user", "content": f"Напишите текст песни на тему '{theme}', в жанре '{genre}', учитывая стиль исполнителя '{artist_style}'. Текст песни должен быть оригинальным, креативным и иметь приятный ритм и структуру. Включите в текст песни припев и пару куплетов."}
        ]
        response = self.openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.8
        )

        lyrics = response['choices'][0]['message']['content']  # type: ignore

        with open(f'{theme}_lyrics.json', 'w') as f:
            json.dump(response, f)
            print(response)
        time.sleep(20)
        return lyrics
    
    
    