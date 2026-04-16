import os
import sys
import requests
import re
import html2text
from lxml import html
from slugify import slugify

def extract_episode_id(url):
    """Extracts the episode ID (number) from the URL."""
    match = re.search(r'release/(\d+)', url)
    return match.group(1) if match else None

def fetch_via_api(episode_id):
    """Attempts to fetch episode data via the website's API."""
    api_url = f"https://aerostatbg.ru/api/release/{episode_id}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            release = data.get('release', {})
            title = release.get('title', f"episode-{episode_id}")
            
            # Extract tracks
            tracks = []
            compositions = release.get('composition_list', [])
            for comp in compositions:
                name = comp.get('composition_name')
                if name:
                    tracks.append(name)
            
            # Extract content text
            content_html = ""
            content_list = release.get('content', [])
            for item in content_list:
                content_html += item.get('text', "")
            
            h = html2text.HTML2Text()
            h.ignore_links = True
            body_text = h.handle(content_html).strip()
            
            return title, body_text, tracks
    except Exception as e:
        print(f"API fetch failed: {e}")
    
    return None, None, None

def fetch_via_xpath(url, episode_id):
    """Fallback method using XPath (may not work for SPAs without JS execution)."""
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching the URL: {e}")
        return None, None, None

    tree = html.fromstring(response.content)
    
    # User's provided XPaths
    content_xpath = f'//*[@id="{episode_id}"]/div/div/div[1]'
    tracklist_xpath = f'//*[@id="{episode_id}"]/div/div/div[1]/div[1]/div[1]/div[2]/ol'
    
    content_elements = tree.xpath(content_xpath)
    if not content_elements:
        content_elements = tree.xpath(f'//*[@id="{episode_id}"]')
        
    if not content_elements:
        return None, None, None

    content_element = content_elements[0]
    body_text = content_element.text_content().strip()
    
    tracklist_elements = tree.xpath(tracklist_xpath)
    tracks = []
    if tracklist_elements:
        li_elements = tracklist_elements[0].xpath('.//li')
        for li in li_elements:
            track_text = ' '.join(li.text_content().strip().split())
            if track_text:
                tracks.append(track_text)

    title_elements = tree.xpath('//h1/text()')
    title_text = title_elements[0].strip() if title_elements else f"episode-{episode_id}"
    
    return title_text, body_text, tracks

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract-podcast-tracks.py <url>")
        return

    url = sys.argv[1]
    episode_id = extract_episode_id(url)
    
    if not episode_id:
        print("Could not determine episode ID from URL.")
        return

    print(f"Attempting to fetch data for episode {episode_id}...")
    
    # Try API first
    title, body, tracks = fetch_via_api(episode_id)
    
    # Fallback to XPath if API fails or returns no tracks (though API is preferred)
    if not tracks:
        print("API did not return tracks or failed. Trying XPath fallback...")
        title, body, tracks = fetch_via_xpath(url, episode_id)

    if not body and not tracks:
        print(f"Error: Could not extract content for episode {episode_id}")
        return

    slug = slugify(title) if title else f"episode-{episode_id}"
    if not slug:
        slug = f"episode-{episode_id}"

    # Save body text
    body_filename = f"{slug}.txt"
    with open(body_filename, 'w', encoding='utf-8') as f:
        f.write(body if body else "")
    print(f"Saved body content to {body_filename}")

    # Save tracklist
    tracklist_filename = f"{slug}-tracklist.txt"
    with open(tracklist_filename, 'w', encoding='utf-8') as f:
        f.write(f"{url}\n")
        for track in tracks:
            f.write(f"{track}\n")
    
    print(f"Saved tracklist to {tracklist_filename}")
    print(f"Found {len(tracks)} tracks.")

if __name__ == "__main__":
    main()
