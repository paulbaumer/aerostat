# Aerostat - Podcast to Spotify Playlist Toolkit

Aerostat is a set of tools to programmatically create Spotify playlists from podcast episode descriptions. It uses the Gemini CLI for intelligent track extraction from web pages and fuzzy matching to find the best possible matches in the Spotify catalog.

## Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Spotify API Credentials:**
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Create a new app.
   - Set the **Redirect URI** to `http://127.0.0.1:8888/callback`.
   - Copy your **Client ID** and **Client Secret**.

3. **Configure Environment (Secrets):**
   - The tool uses a `.env` file to store sensitive credentials locally. This file is ignored by git to prevent accidental exposure.
   - Create a `.env` file in the project root with the following content:
     ```env
     SPOTIPY_CLIENT_ID='your_client_id_here'
     SPOTIPY_CLIENT_SECRET='your_client_secret_here'
     SPOTIPY_REDIRECT_URI='http://127.0.0.1:8888/callback'
     ```
   - **Important:** Never commit your `.env` file or share your Client Secret.

## Tools

### 1. Podcast Episode Track Extraction (`extract-podcast-tracks.py`)

Downloads the content of a podcast episode page and extracts track mentions using the Gemini CLI.

**Usage:**
```bash
python extract-podcast-tracks.py <url>
```

**What it does:**
- Downloads the main body content of the provided URL using the website's API or XPath fallback.
- Saves the content to a file in the `_source/` directory with the naming format `{podcast-name}-{episode-number}-{transliterated-title}-{date}.txt`.
- Includes a header on the first line: `{Podcast Name} - {Number} - {Title} - {Date}` in the original language.
- Places the source URL on the second line.
- Extracts tracks and saves them to a similarly named `-tracklist.txt` file in `_source/`.

### 2. Spotify Playlist Generator (`create-spotify-playlist.py`)

Creates a Spotify playlist from a list of song mentions.

**Usage:**
```bash
python create-spotify-playlist.py _source/<tracklist_file>
```

**What it does:**
- Reads a tracklist file from the `_source/` directory.
- Searches Spotify for matches using enhanced fuzzy matching and multi-stage queries.
- Creates a new playlist with the found tracks.
- Generates a local report (e.g., `_source/{base_name}-spotify-playlist.txt`) with match details.


## Technical Details

- **Body Extraction:** Primarily uses the website's **REST API** for high-fidelity content retrieval, with a robust **lxml/XPath** fallback for static pages.
- **Track Extraction:** Deterministically extracts tracklists using specific structural markers (XPaths) identified in the podcast's web architecture.
- **Fuzzy Matching:** Employs a multi-stage search strategy and **rapidfuzz**'s weighted scoring to accurately identify tracks despite variations in artist or song naming.
- **Reporting:** Generates detailed match reports in the `_source/` directory, including confidence scores and reasons for any missing tracks.
- **Playlist Description:** The playlist description includes the source URL and a summary of found tracks.
