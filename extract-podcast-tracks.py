import os
import sys
import requests
import subprocess
from bs4 import BeautifulSoup
from slugify import slugify

def extract_main_content(html):
    """Heuristically extracts the main title and body content from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try to find the main title
    title = soup.find('h1')
    if not title:
        title = soup.title
    
    title_text = title.get_text().strip() if title else "podcast-episode"
    
    # Heuristically remove common navigation and footer elements
    for element in soup(['nav', 'footer', 'header', 'aside', 'script', 'style']):
        element.decompose()
        
    # Get text from body or main content area if possible
    body = soup.find('main') or soup.find('article') or soup.body
    body_text = body.get_text(separator='\n').strip() if body else ""
    
    return title_text, body_text

def extract_tracks_with_gemini(text):
    """Uses the Gemini CLI to extract track mentions from the text."""
    prompt = (
        "You are an expert at identifying song mentions in podcast episode descriptions. "
        "From the following text, extract a list of all songs and artists mentioned. "
        "Provide the list with one track per line in the format 'Artist - Song Name' or just 'Song Name' if the artist is unknown. "
        "Do not include any other text, numbers, or bullet points. Only the song list.\n\n"
        f"Text:\n{text}"
    )
    
    try:
        # Calling the 'gemini' CLI command
        process = subprocess.Popen(['gemini', 'ask', prompt], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error calling Gemini CLI: {stderr}")
            return []
            
        # Split output into lines and clean up
        tracks = [line.strip() for line in stdout.split('\n') if line.strip()]
        return tracks
    except Exception as e:
        print(f"Failed to run Gemini CLI: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract-podcast-tracks.py <url>")
        return

    url = sys.argv[1]
    print(f"Fetching URL: {url}...")
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching the URL: {e}")
        return

    title, body = extract_main_content(response.text)
    slug = slugify(title)
    
    if not slug:
        slug = "podcast-episode"

    # Save body text
    body_filename = f"{slug}.txt"
    with open(body_filename, 'w') as f:
        f.write(body)
    print(f"Saved body content to {body_filename}")

    # Extract tracks using Gemini
    print("Extracting tracks using Gemini CLI...")
    tracks = extract_tracks_with_gemini(body)
    
    # Save tracklist
    tracklist_filename = f"{slug}-tracklist.txt"
    with open(tracklist_filename, 'w') as f:
        f.write(f"{url}\n")
        for track in tracks:
            f.write(f"{track}\n")
    
    print(f"Saved tracklist to {tracklist_filename}")
    print(f"Found {len(tracks)} tracks.")

if __name__ == "__main__":
    main()
