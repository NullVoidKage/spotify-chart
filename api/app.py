from flask import Flask, render_template, request, redirect, session, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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

# Callback route
@app.route('/callback')
def callback():
    # Get authorization code from the request
    code = request.args.get('code')

    # Exchange authorization code for access token
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']

    # Set the access token for the Spotify client
    spotify.client_credentials_manager.token_info = token_info

    # Redirect to the results page
    return redirect(url_for('results'))

# Results route
@app.route('/results')
def results():
    query = request.args.get('query')
    results = spotify.search(q=query, type='track', limit=10)
    tracks = results['tracks']['items']
    return render_template('results.html', tracks=tracks)


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
