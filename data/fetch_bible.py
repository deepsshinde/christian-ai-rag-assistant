# data/fetch_bible.py - NEW FILE NEEDED
import requests
import json

def fetch_full_bible():
    """Fetch complete Bible from API.bible or bible-api.com"""
    
    # Option 1: Using bible-api.com (free, no key needed)
    base_url = "https://bible-api.com"
    
    # Common verses to fetch
    books = [
        "Genesis", "Exodus", "Matthew", "John", "Romans", 
        "Psalms", "Proverbs", "Isaiah"
        # ... need all 66 books
    ]
    
    all_verses = []
    
    for book in books:
        for chapter in range(1, 51):  # Adjust per book
            try:
                response = requests.get(f"{base_url}/{book}+{chapter}")
                if response.status_code == 200:
                    data = response.json()
                    # Parse verses...
                    all_verses.append(data)
            except:
                break
    
    return all_verses

# OR Option 2: Download pre-made JSON
# https://github.com/thiagobodruk/bible - 31,000 verses