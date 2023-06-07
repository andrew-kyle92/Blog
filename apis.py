# ########## All the APIs that random.html uses ##########
import requests
import datetime as dt
from dotenv import dotenv_values
from starting_nasa_data import nasa_data_start
import spotipy
from spotipy.oauth2 import SpotifyOAuth

config = dotenv_values(".env")


class APIs:
    def __init__(self):
        self.current_hour = 1
        self.nasa_data = None
        self.nasa_key = config.get("NASA_KEY")
        self.news_key = config.get("NEWS_KEY")

    def nasa(self):
        params = {
            "api_key": self.nasa_key,
            "count": 5,
        }
        url = "https://api.nasa.gov/planetary/apod?"
        current_hour = dt.datetime.now().hour
        if current_hour < self.current_hour or current_hour > self.current_hour or self.current_hour is None:
            with requests.get(url=url, params=params, headers={"content-type": "application/json"}) as req:
                if req.status_code == 200:
                    self.current_hour = current_hour
                    self.nasa_data = req.json()
                    return self.nasa_data
                else:
                    print(f"Bad Request;\nStatus: {req.status_code}\nResponse: {req.text}")
                    return nasa_data_start
        else:
            self.nasa_data = nasa_data_start if self.nasa_data is None else self.nasa_data
            return self.nasa_data

    def news(self, q, sort_by, amount):
        params = {
            "q": q,
            "sortBy": sort_by,
            "language": "en",
            "pageSize": amount,
            "apiKey": self.news_key
        }
        url = "https://newsapi.org/v2/everything?"

        try:
            with requests.get(url=url, params=params) as req:
                if req.status_code == 200:
                    data = req.json()
                    return data["articles"]
        except requests.exceptions as e:
            print(e)
            return False

    def jokes(self, url):
        try:
            with requests.get(url=url) as req:
                data = req.json()
                return data
        except requests.exceptions as e:
            print(e)
            return False


apis = APIs()
nasa_data = apis.nasa()
print(nasa_data)


class Spotify:
    """
        For using the spotipy api (essentially spotify's api) and using it for
        music streaming
    """
    def __init__(self):
        self.client_id = config.get("SPOTIFY_CLIENT_ID")
        self.client_secret = config.get("SPOTIFY_CLIENT_SECRET")
        self.redirect_url = "http://127.0.0.1:5000/callback"

    def search_artist(self, a):
        """
        Search artist by name and pull any data related to them
        :param a:
        :return artist music data:
        """
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_url,
            scope="user-library-read"
        ))
        results = sp.search(q=a, limit=10)
        print(results)
