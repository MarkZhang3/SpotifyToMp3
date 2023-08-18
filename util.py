import requests
import base64
import json
import youtube_dl
import yt_dlp 
from bs4 import BeautifulSoup
import re
from youtube_search import YoutubeSearch


def get_token(CLIENT_ID: str, CLIENT_SECRET: str) -> str:
    auth_string = CLIENT_ID + ":" + CLIENT_SECRET
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    # token url from Spotify Documentation (OAuth 2.0)
    # https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded" 
    }
    data = "grant_type=client_credentials"

    result = requests.post(token_url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token

def get_auth_header(token: str) -> dict:
    return {"Authorization": "Bearer " + token}

def get_songs_from_playlist(token: str, playlist_id: str) -> list:
    # https://developer.spotify.com/documentation/web-api/reference/get-playlist
    url = "https://api.spotify.com/v1/playlists/"
    headers = get_auth_header(token)
    endpoint = url + playlist_id
    result = requests.get(endpoint, headers=headers)
    print(result)
    json_result = json.loads(result.content)
    print(json_result)
    songs = []
    for i in json_result['tracks']['items']:
        song_artists = ''
        for artist_info in i['track']['artists']:
            song_artists += ' ' + str(artist_info['name'])
        song_name = str(i['track']['name'])
        songs.append(song_name + ' by' + song_artists)

    return songs 

def extract_playlist_id(playlist_url: str) -> str:
    spotify_url_start = 'https://open.spotify.com/playlist/'
    if playlist_url[:len(spotify_url_start)] != spotify_url_start:
        return playlist_url
    start = playlist_url.find('/playlist/') + len('/playlist/')
    end = playlist_url.find('?')
    return playlist_url[start:end]

def get_urls_using_requests(query: str, num_results=1):
    search_url = f'https://www.youtube.com/results?search_query={query}'
    HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36"
    }
    response = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'lxml')

    json_data = ""
    for script_tag in soup.find_all('script'):
        script_content = str(script_tag)
        if script_content and "var ytInitialData" in script_content:
            # Extract the content of ytInitialData using regular expressions
            match = re.search(r'var ytInitialData = (\{.*?\});', script_content)
            if match:
                init_data = str(match.group(1))
                json_data = json.loads(init_data)
                # print(yt_initial_data)
                break

    if json_data == '':
        return "NOT FOUND" 
    
    content = (
        json_data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    )
    
    video_urls = []
    yt_url = 'https://www.youtube.com/'

    for data in content:
        for k, v in data.items():
            if type(v) is dict and 'navigationEndpoint' in v.keys():
                watch_url = v['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
                video_urls.append(yt_url + watch_url)
            if len(video_urls) == num_results:
                break
    
    return video_urls[0]

def get_urls_using_yt_search(query, num_results=1):
    search_url = f'https://www.youtube.com/results?search_query={query}'
    results = YoutubeSearch(search_url, max_results=num_results).to_dict()
    video_urls = []
    yt_url = 'https://www.youtube.com/'
    for result in results:
        url = yt_url + result['url_suffix']
        video_urls.append(url)
    return video_urls
    

def download_songs(tracks: list) -> bool:

    ydl_opts = {
        'format': 'bestaudio/best',
        # 'postprocessors': [{
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        #     'preferredquality': '192',
        # }],
        'outtmpl': '~/Downloads/%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for track in tracks:
            video_urls = get_urls_using_yt_search(track)
            if video_urls == []:
                video_urls = get_urls_using_requests(track)
            if video_urls:
                ydl.download([video_urls[0]])
            else:
                return False 
    return True

