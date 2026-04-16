import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from rapidfuzz import fuzz
from dotenv import load_dotenv

load_dotenv()

def get_spotify_client():
    """Initializes and returns a Spotify client with necessary scopes."""
    scope = "playlist-modify-public"
    return Spotify(auth_manager=SpotifyOAuth(scope=scope))

def search_and_match(sp, query, threshold=80):
    """
    Searches Spotify for a query and uses fuzzy matching to find the best track.
    Returns (track_uri, track_name, artist_name, score) or (None, None, None, 0).
    """
    results = sp.search(q=query, limit=5, type='track')
    items = results.get('tracks', {}).get('items', [])
    
    best_match = (None, None, None, 0)
    
    for item in items:
        track_name = item['name']
        artist_name = item['artists'][0]['name']
        full_name = f"{artist_name} {track_name}"
        
        # Calculate similarity score
        score = fuzz.token_sort_ratio(query.lower(), full_name.lower())
        
        if score >= threshold and score > best_match[3]:
            best_match = (item['uri'], track_name, artist_name, score)
            
    return best_match

def create_playlist_with_tracks(sp, name, track_uris, description):
    """Creates a new playlist and adds tracks in batches."""
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, name, public=True, description=description)
    playlist_id = playlist['id']
    
    # Spotify limit is 100 tracks per request
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        sp.playlist_add_items(playlist_id, batch)
        
    return playlist['external_urls']['spotify']
