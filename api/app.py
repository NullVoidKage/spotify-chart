from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

# Retrieve the Spotify API credentials from the environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

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
