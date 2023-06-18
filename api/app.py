from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

# Spotify API credentials
CLIENT_ID = 'ba6a268d7e264ea899acac717e78ac09'
CLIENT_SECRET = '455aea128c024e8b8b81d8977ed7124b'


# Create a Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Search route
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = spotify.search(q=query, type='track', limit=10)
    tracks = results['tracks']['items']
    return render_template('results.html', tracks=tracks)

if __name__ == '__main__':
    app.run(debug=True)
