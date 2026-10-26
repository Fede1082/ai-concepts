import re
from collections import Counter

#Normalize
def normalize_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

#Remove noise, stopwords, and irrelevant content from the documents before injection
def noise_removal(text):
    """Collapse horizontal whitespace and remove repeated page headers/footers.

    Pages must be separated by form feeds (``\f``). Only matching first/last
    nonempty lines on a majority of nonempty pages (at least two) are removed.
    Line breaks are preserved; ordinary repeated lines inside pages are kept.
    """
    pages = []
    for page in text.split('\f'):
        lines = [re.sub(r'[^\S\r\n]+', ' ', line).strip()
                 for line in page.splitlines()]
        pages.append([line for line in lines if line])

    nonempty_pages = [page for page in pages if page]
    threshold = max(2, len(nonempty_pages) // 2 + 1)
    headers = Counter(page[0] for page in nonempty_pages)
    footers = Counter(page[-1] for page in nonempty_pages)

    cleaned_pages = []
    for page in pages:
        if not page:
            continue
        start = 1 if headers[page[0]] >= threshold else 0
        end = len(page) - (1 if footers[page[-1]] >= threshold else 0)
        cleaned = '\n'.join(page[start:end])
        if cleaned:
            cleaned_pages.append(cleaned)
    return '\n\n'.join(cleaned_pages)


def remove_stopwords(text, stopwords):
    """Remove stopwords from the text."""
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stopwords]
    return ' '.join(filtered_words)

def remove_irrelevant_content(text, irrelevant_patterns):
    """Remove irrelevant content based on specified patterns."""
    for pattern in irrelevant_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text

def preprocess_text(text, stopwords=None, irrelevant_patterns=None):
    """Preprocess the text by normalizing, removing noise, stopwords, and irrelevant content."""
    text = normalize_text(text)
    text = noise_removal(text)
    if stopwords:
        text = remove_stopwords(text, stopwords)
    if irrelevant_patterns:
        text = remove_irrelevant_content(text, irrelevant_patterns)
    return text

