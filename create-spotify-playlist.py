import os
import sys
import datetime
from spotify_utils import get_spotify_client, search_and_match, create_playlist_with_tracks
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file>")
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    # Generate report filename
    base_name = os.path.splitext(input_file)[0]
    if base_name.endswith('-tracklist'):
        base_name = base_name[:-len('-tracklist')]
    report_file = f"{base_name}-spotify-playlist.txt"

    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print(f"Error: {input_file} is empty.")
        return

    source_url = lines[0]
    song_mentions = lines[1:]

    sp = get_spotify_client()
    
    found_uris = []
    report_lines = [f"Source URL: {source_url}\n", f"Processing Date: {datetime.date.today()}\n", "-"*20 + "\n"]
    
    matches_count = 0
    total_count = len(song_mentions)

    for query in song_mentions:
        print(f"Searching for: {query}...")
        uri, track_name, artist_name, score = search_and_match(sp, query)
        
        if uri:
            found_uris.append(uri)
            matches_count += 1
            report_lines.append(f"MATCHED: {query} -> {artist_name} - {track_name} (Confidence: {score}%)\n")
        else:
            report_lines.append(f"MISSING: {query} (No suitable match found)\n")

    # Create local report
    with open(report_file, 'w') as rf:
        rf.writelines(report_lines)
    
    print(f"Report saved to {report_file}")

    # Prepare playlist metadata
    playlist_name = f"Podcast Mentions - {datetime.date.today()}"
    description = f"Source: {source_url} | Found {matches_count}/{total_count} tracks. See local {report_file} for details."
    
    if found_uris:
        print(f"Creating playlist: {playlist_name}...")
        playlist_url = create_playlist_with_tracks(sp, playlist_name, found_uris, description)
        print(f"Success! Playlist created: {playlist_url}")
    else:
        print("No tracks found. Playlist was not created.")

if __name__ == "__main__":
    main()
