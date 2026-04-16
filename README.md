# Aerostat - Spotify Playlist Generator from Podcast Mentions

This tool programmatically creates Spotify playlists from a list of song mentions found in podcast episodes. It uses fuzzy matching to handle naming variations and provides a detailed report of matches and missing tracks.

## Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Spotify API Credentials:**
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Create a new app.
   - Set the **Redirect URI** to `http://localhost:8888/callback`.
   - Copy your **Client ID** and **Client Secret**.

3. **Configure Environment (Secrets):**
   - The tool uses a `.env` file to store sensitive credentials locally. This file is ignored by git to prevent accidental exposure.
   - Create a `.env` file in the project root with the following content:
     ```env
     SPOTIPY_CLIENT_ID='your_client_id_here'
     SPOTIPY_CLIENT_SECRET='your_client_secret_here'
     SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
     ```
   - **Important:** Never commit your `.env` file or share your Client Secret.

## Usage

1. **Prepare Input:**
   - Create a text file (e.g., `mentions.txt`).
   - The **first line** should be the URL of the podcast episode source.
   - Subsequent lines should be the song mentions (e.g., "Artist - Song Name").

2. **Run the Script:**
   ```bash
   python create-spotify-playlist.py mentions.txt
   ```
   - On the first run, it will open a browser window for you to log in to Spotify and authorize the app.

3. **Check Results:**
   - A new playlist will be created in your Spotify account named "Podcast Mentions - [Date]".
   - A local report (e.g., `mentions-playlist.txt`) will be generated with detailed match results and confidence scores.

## How it Works

- **Fuzzy Matching:** The script uses the `rapidfuzz` library to compare your input mentions against Spotify's search results. It selects the best match with a similarity score above 80%.
- **Missing Songs:** Any songs not found in Spotify's catalog (or with a low similarity score) are excluded from the playlist but listed in the generated report file.
- **Playlist Description:** The playlist description includes the source URL and a summary of found tracks.
