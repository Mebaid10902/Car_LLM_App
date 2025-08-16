import re
import unicodedata

BLOCKLIST = [
    "ignore previous",
    "system command",
    "delete all",
    "shutdown",
    "format disk"
]

# Precompile regex patterns for exact phrases (word boundaries)
BLOCKLIST_PATTERNS = [re.compile(r"\b" + re.escape(bad) + r"\b", re.IGNORECASE) for bad in BLOCKLIST]

# Fuzzy helper: normalize string
def normalize_text(text: str) -> str:
    """Lowercase, remove accents, convert punctuation to spaces."""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[\W_]+", " ", text)  # non-alphanumeric → space
    return text

def sanitize_input(text: str, redaction="[REDACTED]") -> str:
    """Sanitize text by redacting blocked phrases, including simple fuzzy matches."""
    clean_text = text
    normalized = normalize_text(text)

    for pattern, phrase in zip(BLOCKLIST_PATTERNS, BLOCKLIST):
        # Exact match redaction
        clean_text = pattern.sub(redaction, clean_text)

        # Simple fuzzy match: remove spaces and check if phrase in normalized text
        phrase_normalized = phrase.replace(" ", "")
        if phrase_normalized in normalized.replace(" ", ""):
            clean_text = re.sub(phrase_normalized, redaction, clean_text, flags=re.IGNORECASE)

    return clean_text

def is_safe(text: str) -> bool:
    """Return True if text contains no blocked phrases (including fuzzy)."""
    normalized = normalize_text(text)
    for phrase in BLOCKLIST:
        phrase_normalized = phrase.replace(" ", "")
        if re.search(r"\b" + re.escape(phrase) + r"\b", text, re.IGNORECASE) or \
           phrase_normalized in normalized.replace(" ", ""):
            return False
    return True

def flagged_words(text: str) -> list:
    """Return list of blocked phrases found in the text (including fuzzy)."""
    normalized = normalize_text(text)
    found = []
    for phrase in BLOCKLIST:
        phrase_normalized = phrase.replace(" ", "")
        if re.search(r"\b" + re.escape(phrase) + r"\b", text, re.IGNORECASE) or \
           phrase_normalized in normalized.replace(" ", ""):
            found.append(phrase)
    return found
