import os
import re
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from rapidfuzz import fuzz
from dotenv import load_dotenv

load_dotenv(override=True)

def get_spotify_client():
    """Initializes and returns a Spotify client with necessary scopes."""
    scope = "playlist-modify-private playlist-modify-public user-read-email"
    
    # Strip any potential quotes or whitespace from env vars
    client_id = os.getenv('SPOTIPY_CLIENT_ID', '').strip().strip("'").strip('"')
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET', '').strip().strip("'").strip('"')
    redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI', '').strip().strip("'").strip('"')
    
    return Spotify(auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    ))

def clean_string(text):
    """Removes common noise from song/artist strings for better matching."""
    if not text:
        return ""
    # Remove contents of parentheses/brackets and common noise words
    text = re.sub(r'[\(\[][^\]\)]*[\)\]]', '', text)
    text = re.sub(r'\b(feat|ft|remix|edit|original|mix|version|remastered|remaster)\b', '', text, flags=re.IGNORECASE)
    # Remove special characters except spaces
    text = re.sub(r'[^\w\s-]', '', text)
    return ' '.join(text.split()).lower()

def search_and_match(sp, query, threshold=65):
    """
    Enhanced multi-stage search and matching logic.
    """
    # 1. Prepare query variations
    clean_q = clean_string(query)
    search_queries = [query, clean_q]
    
    # If there's a dash, try searching for parts
    if '–' in query or '-' in query:
        parts = re.split(r'–|-', query)
        if len(parts) >= 2:
            artist_part = clean_string(parts[0])
            song_part = clean_string(parts[1])
            search_queries.append(f"{artist_part} {song_part}")
            search_queries.append(song_part) # Broad search
    
    best_match = (None, None, None, 0)
    seen_uris = set()

    for q in search_queries:
        if not q or len(q) < 3: continue
        
        try:
            results = sp.search(q=q, limit=10, type='track')
            items = results.get('tracks', {}).get('items', [])
        except Exception:
            continue

        for item in items:
            uri = item['uri']
            if uri in seen_uris: continue
            seen_uris.add(uri)

            track_name = item['name']
            artist_name = item['artists'][0]['name']
            
            # Match against multiple combinations
            targets = [
                f"{artist_name} {track_name}",
                f"{track_name} {artist_name}",
                track_name
            ]
            
            item_scores = [
                fuzz.token_set_ratio(clean_q, clean_string(t)) for t in targets
            ]
            score = max(item_scores)
            
            if score > best_match[3]:
                best_match = (uri, track_name, artist_name, score)
                
            # Early exit for perfect match
            if score >= 95:
                return best_match

    if best_match[3] >= threshold:
        return best_match
        
    return (None, None, None, 0)

def create_playlist_with_tracks(sp, name, track_uris, description):
    """Creates a new playlist and adds tracks in batches."""
    auth_manager = sp.auth_manager
    token = auth_manager.get_access_token(as_dict=False)
    
    # Try POST to /me/playlists which worked in raw test
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": name,
        "public": False,
        "description": description
    }
    
    import requests
    response = requests.post(url, headers=headers, json=data)
    if response.status_code not in [200, 201]:
        print(f"Error creating playlist: {response.status_code} - {response.text}")
        # Try fallback to standard spotipy method
        user_id = sp.me()['id']
        playlist = sp.user_playlist_create(user_id, name, public=False, description=description)
    else:
        playlist = response.json()
        
    playlist_id = playlist['id']
    
    # Spotify limit is 100 tracks per request
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        sp.playlist_add_items(playlist_id, batch)
        
    return playlist['external_urls']['spotify']
