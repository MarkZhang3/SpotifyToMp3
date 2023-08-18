from flask import Flask, request, redirect, url_for, render_template
from main import runner

app = Flask(__name__) 

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        playlist_url = request.form['playlist-url']
        
        message = runner(playlist_url)

        return redirect(url_for('index', message=message))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True) 
