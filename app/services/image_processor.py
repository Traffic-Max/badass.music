import requests
import json
import os

def get_random_image(query):
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_API_KEY")
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = json.loads(response.text)
        if "urls" in data:
            image_url = data["urls"]["regular"]
            return image_url
        else:
            print("Ошибка: ключ 'urls' не найден в ответе API.")
            return None
    else:
        print(f"Ошибка: запрос к API Unsplash не был успешным. Код состояния: {response.status_code}")
        return None