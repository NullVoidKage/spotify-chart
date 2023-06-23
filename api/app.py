from flask import Flask, redirect, request, render_template, session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_personality_traits(genres):
    personality_traits = {
        'pop': {
            'trait': 'Outgoing and energetic',
            'image_url': 'https://example.com/pop.jpg'
        },
        'rock': {
            'trait': 'Creative and rebellious',
            'image_url': 'https://example.com/rock.jpg'
        },
        'hip-hop': {
            'trait': 'Confident and assertive',
            'image_url': 'https://example.com/hiphop.jpg'
        },
        'jazz': {
            'trait': 'Introspective and reflective',
            'image_url': 'https://example.com/jazz.jpg'
        },
        'classical': {
            'trait': 'Analytical and intellectual',
            'image_url': 'https://example.com/classical.jpg'
        },
        'electronic': {
            'trait': 'Innovative and adventurous',
            'image_url': 'https://example.com/electronic.jpg'
        }
        # Add more genre-personality mappings as desired
    }

    traits = []

    for genre in genres:
        if genre in personality_traits:
            traits.append(personality_traits[genre])

    return traits

def get_monthly_played_hours():
    if 'token_info' not in session:
        return redirect('/login')

    token_info = session['token_info']
    if token_info and 'access_token' in token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        now = datetime.now()
        start_date = now - timedelta(days=30)
        start_timestamp = int(start_date.timestamp()) * 1000
        end_timestamp = int(now.timestamp()) * 1000

        results = sp.current_user_top_tracks(limit=50, time_range='long_term')
        total_played_hours = 0
        genre_counter = {}

        for track in results['items']:
            track_id = track['id']
            track_info = sp.audio_analysis(track_id)
            duration = track_info['track']['duration']
            played_hours = duration / 1000 / 60 / 60
            total_played_hours += played_hours

            for genre in track['artists'][0]['genres']:
                genre_counter[genre] = genre_counter.get(genre, 0) + 1

        sorted_genres = sorted(genre_counter.items(), key=lambda x: x[1], reverse=True)
        top_genres = [genre for genre, _ in sorted_genres[:5]]

        personality_result = get_personality_traits(top_genres)

        return total_played_hours, personality_result

    return redirect('/login')

def get_most_played_artists():
    if 'token_info' not in session:
        return redirect('/login')

    token_info = session['token_info']
    if token_info and 'access_token' in token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])

        results = sp.current_user_top_artists(limit=10, time_range='long_term')
        most_played_artists = [artist['name'] for artist in results['items']]

        return most_played_artists

    return redirect('/login')

def get_most_played_songs():
    if 'token_info' not in session:
        return redirect('/login')

    token_info = session['token_info']
    if token_info and 'access_token' in token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        now = datetime.now()
        start_date = now - timedelta(days=30)
        start_timestamp = int(start_date.timestamp()) * 1000
        end_timestamp = int(now.timestamp()) * 1000

        results = sp.current_user_top_tracks(limit=10, time_range='short_term')
        most_played_songs = [song['name'] for song in results['items']]

        return most_played_songs

    return redirect('/login')

def get_played_hours_by_year():
    if 'token_info' not in session:
        return redirect('/login')

    token_info = session['token_info']
    if token_info and 'access_token' in token_info:
        sp = spotipy.Spotify(auth=token_info['access_token'])
        now = datetime.now()

        years = range(2010, now.year + 1)
        played_hours_by_year = {}

        for year in years:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31, 23, 59, 59)
            start_timestamp = int(start_date.timestamp()) * 1000
            end_timestamp = int(end_date.timestamp()) * 1000

            results = sp.current_user_recently_played(limit=50, after=start_timestamp, before=end_timestamp)
            total_played_hours = sum([item['track']['duration_ms'] for item in results['items']]) / 1000 / 60 / 60
            played_hours_by_year[year] = total_played_hours

        return played_hours_by_year

    return redirect('/login')

@app.route('/')
def index():
    if 'token_info' in session:
        return redirect('/result')
    else:
        return redirect('/login')

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(
        client_id= 'ba6a268d7e264ea899acac717e78ac09',
        client_secret='455aea128c024e8b8b81d8977ed7124b',
        redirect_uri='http://localhost:5000/callback',
        scope='user-read-recently-played user-top-read'
    )
    auth_url = sp_oauth.get_authorize_url()

    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(
        client_id= 'ba6a268d7e264ea899acac717e78ac09',
        client_secret='455aea128c024e8b8b81d8977ed7124b',
        redirect_uri='http://localhost:5000/callback',
        scope='user-read-recently-played user-top-read'
    )
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    if token_info:
        session['token_info'] = token_info
        return redirect('/result')

    return redirect('/login')

@app.route('/result')
def result():
    total_played_hours, personality_result = get_monthly_played_hours()
    most_played_artists = get_most_played_artists()
    most_played_songs = get_most_played_songs()
    played_hours_by_year = get_played_hours_by_year()

    return render_template('index.html', total_hours=total_played_hours, personality_result=personality_result,
                           top_artists=most_played_artists, top_songs=most_played_songs,
                           played_hours_by_year=played_hours_by_year)


if __name__ == '__main__':
    app.run()
