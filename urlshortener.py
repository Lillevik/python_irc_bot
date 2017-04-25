import json
import requests
from config import get_key as key


def shorten_url(url_to_shorten):
    try:
        url = "https://www.googleapis.com/urlshortener/v1/url?key=" + key()
        data = json.JSONEncoder().encode({'longUrl': url_to_shorten})
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=data, headers=headers)
        return response.json()['id']
    except Exception as e:
        print(e)
        return False