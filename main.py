from util import get_token, get_songs_from_playlist, extract_playlist_id, download_songs

def runner(playlist_url: str):
    try:
        file = open('text.txt', 'r')
        CLIENT_ID, CLIENT_SECRET = str(file.readline().strip()), str(file.readline().strip())
        # print(CLIENT_ID, CLIENT_SECRET)

        playlist_id = extract_playlist_id(playlist_url)
        token = get_token(CLIENT_ID, CLIENT_SECRET)
        song_info = get_songs_from_playlist(token, playlist_id)
        ## print(song_info)

        if download_songs(song_info): 
            return "Download Complete"
        else:
            return "Unable to complete download"
    except: 
        return "Error"

## one song, one artist: 20TpNNYVhhqvfPzB9kReaF
## one song, featuring artist: 5fIA5cFSbwXWAqb6iuB2a3