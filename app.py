from flask import Flask, request, redirect, url_for, render_template, Response, flash
from main import get_song_urls
from util import download_playlist

app = Flask(__name__) 
app.secret_key = 'key'

@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    if request.method == 'POST':
        playlist_url = request.form['playlist-url']
        
        song_urls = get_song_urls(playlist_url=playlist_url)

        messages = download_playlist(song_urls)
        
        print('logged' + messages)
        flash(messages)
        # return Response(download_playlist(song_urls), content_type='text/event-stream')
    return redirect(url_for('index'))

@app.route('/events', methods=['POST']) 
def events():
    if request.method == 'POST':
        playlist_url = request.form['playlist-url']
        
        song_urls = get_song_urls(playlist_url=playlist_url)

        return Response(download_playlist(song_urls), content_type='text/event-stream')
    return Response(download_playlist([]), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True) 
