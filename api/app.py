from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Spotify API credentials
CLIENT_ID = 'ba6a268d7e264ea899acac717e78ac09'
CLIENT_SECRET = '455aea128c024e8b8b81d8977ed7124b'
REDIRECT_URI = 'https://spotifychart.com/'

# Create a Spotify client
scope = 'user-read-private user-read-email'
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
)
spotify = spotipy.Spotify(auth_manager=sp_oauth)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Login route
@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# Callback route after successful login
@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('search'))

# Search route
@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'token_info' not in session:
        return redirect(url_for('login'))
    query = request.form.get('query')
    if query:
        token_info = session['token_info']
        access_token = token_info['access_token']
        spotify = spotipy.Spotify(auth=access_token)
        results = spotify.search(q=query, type='track', limit=10)
        tracks = results['tracks']['items']
        return render_template('results.html', tracks=tracks)
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
