import os
import sys
import requests
import re
from lxml import html
from slugify import slugify

def extract_episode_id(url):
    """Extracts the episode ID (number) from the URL."""
    match = re.search(r'(\d+)', url)
    return match.group(1) if match else "1086"

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract-podcast-tracks.py <url>")
        return

    url = sys.argv[1]
    print(f"Fetching URL: {url}...")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching the URL: {e}")
        return

    tree = html.fromstring(response.content)
    
    episode_id = extract_episode_id(url)
    
    # User's provided XPaths
    content_xpath = f'//*[@id="{episode_id}"]/div/div/div[1]'
    tracklist_xpath = f'//*[@id="{episode_id}"]/div/div/div[1]/div[1]/div[1]/div[2]/ol'
    
    # Try content first
    content_elements = tree.xpath(content_xpath)
    if not content_elements:
        print(f"Warning: Could not find content with XPath {content_xpath}")
        # Let's try to just find any div with an ID that matches the ID
        content_elements = tree.xpath(f'//*[@id="{episode_id}"]')
        
    if not content_elements:
        print(f"Error: Could not find content for ID {episode_id}")
        return

    content_element = content_elements[0]
    # Get text content from the content element
    body_text = content_element.text_content().strip()
    
    # Find tracks from the ol list
    tracklist_elements = tree.xpath(tracklist_xpath)
    tracks = []
    
    if tracklist_elements:
        ol = tracklist_elements[0]
        # Get all li elements under the ol
        # We look for direct li or any li inside?
        # Usually they are direct.
        li_elements = ol.xpath('.//li')
        for li in li_elements:
            # We want the text content, clean up whitespace
            # Some entries might have nested spans for artist/title
            track_text = li.text_content().strip()
            # Clean up potential extra whitespace within the string
            track_text = ' '.join(track_text.split())
            if track_text:
                tracks.append(track_text)
    else:
        print(f"Warning: Could not find tracklist with XPath {tracklist_xpath}")

    # Title - let's try to get it from the page
    title_elements = tree.xpath('//h1/text()')
    title_text = title_elements[0].strip() if title_elements else f"episode-{episode_id}"
    
    slug = slugify(title_text)
    if not slug:
        slug = f"episode-{episode_id}"

    # Save body text
    body_filename = f"{slug}.txt"
    with open(body_filename, 'w', encoding='utf-8') as f:
        f.write(body_text)
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
