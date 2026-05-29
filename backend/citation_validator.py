import re
from typing import List

# Common Bible book abbreviations
BIBLE_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
    "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah",
    "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel",
    "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews",
    "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation"
]


def validate_citations(response: str, retrieved_context: List[str]) -> List[str]:
    """
    Extract and validate Bible citations from response.
    Only return citations that match retrieved context.
    """
    
    # Pattern: Book Chapter:Verse (e.g., "John 3:16")
    pattern = r'\b([1-3]?\s?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(\d+):(\d+(?:-\d+)?)\b'
    
    citations = re.findall(pattern, response)
    
    valid_citations = []
    
    for book, chapter, verse in citations:
        citation_str = f"{book} {chapter}:{verse}"
        
        # Check if this book is in the Bible
        book_valid = any(bible_book.lower() == book.lower().strip() 
                        for bible_book in BIBLE_BOOKS)
        
        if not book_valid:
            continue
        
        # Check if citation appears in retrieved context
        found_in_context = any(citation_str.lower() in context.lower() 
                              for context in retrieved_context)
        
        if found_in_context:
            valid_citations.append(citation_str)
    
    return valid_citations


def detect_fake_verses(response: str) -> List[str]:
    """
    Detect potential hallucinated verses.
    Returns list of suspicious citations.
    """
    
    pattern = r'\b([1-3]?\s?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(\d+):(\d+)\b'
    citations = re.findall(pattern, response)
    
    suspicious = []
    
    for book, chapter, verse in citations:
        # Check if book exists
        book_valid = any(bible_book.lower() == book.lower().strip() 
                        for bible_book in BIBLE_BOOKS)
        
        if not book_valid:
            suspicious.append(f"{book} {chapter}:{verse}")
        
        # Check for impossible chapter/verse numbers
        try:
            if int(chapter) > 150 or int(verse.split('-')[0]) > 176:
                suspicious.append(f"{book} {chapter}:{verse}")
        except:
            pass
    
    return suspicious