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
# Skip if already processed (default)
python extract-podcast-tracks.py <url>

# Force overwrite
python extract-podcast-tracks.py <url> --force
```

**What it does:**
- Checks the `_source/` directory and skips processing if a file for this episode ID already exists (unless `--force` is used).
- Downloads the main body content of the provided URL using the website's API or XPath fallback.
- Saves the content to a file in the `_source/` directory with the naming format `{slug-podcast}-{episode-number}-{transliterated-title}-{date}.txt`.
- Includes a header on the first line: `{Podcast Name} - {Number} - {Title} - {Date}` in the original language.
- Places the source URL on the second line.
- Extracts tracks and saves them to a similarly named `-tracklist.txt` file in `_source/`.

### 2. Spotify Playlist Generator (`create-spotify-playlist.py`)

Creates a Spotify playlist from a list of song mentions.

**Usage:**
```bash
# Skip if Jekyll page already exists (default)
python create-spotify-playlist.py _source/<tracklist_file>

# Force re-process and overwrite
python create-spotify-playlist.py _source/<tracklist_file> --force
```

**What it does:**
- Checks the `_episodes/` directory and skips processing if a Markdown file for this episode already exists (unless `--force` is used).
- Reads a tracklist file from the `_source/` directory.
- Searches Spotify for matches using enhanced fuzzy matching and multi-stage queries.
- Creates a new playlist with the found tracks.
- Generates a local report (e.g., `_source/{base_name}-spotify-playlist.txt`) with match details.


## Jekyll Integration (GitHub Pages)

This repository is configured as a minimalistic Jekyll site to showcase your playlists.

### Site Structure:
- **Home Page:** Automatically lists all processed episodes from the `_episodes/` directory.
- **Episode Pages:** Each page features the original episode description and an embedded Spotify player.

### Workflow:
1. Run `extract-podcast-tracks.py` to get the metadata.
2. Run `create-spotify-playlist.py` to create the Spotify playlist and generate the Jekyll Markdown file in `_episodes/`.
3. Commit and push the new files to the `main` branch.
4. GitHub Actions will automatically build and deploy your site to GitHub Pages.

### Configuration:
- `_config.yml`: Jekyll configuration.
- `index.md`: Home page layout.
- `_layouts/`: Contains `default.html` and `episode.html` templates.
- `_episodes/`: Contains the generated Markdown files for each podcast.
