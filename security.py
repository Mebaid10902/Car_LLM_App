import re
import unicodedata
from difflib import SequenceMatcher

# Blocklist keywords / key phrases
BLOCKLIST_KEYWORDS = [
    "ignore", "forget", "bypass", "override", "disregard", "safety",
    "delete", "shutdown", "format", "erase", "reset", "disable",
    "execute", "run", "script", "terminal", "connect", "fetch", "shell",
    "api key", "token", "password", "private data", "confidential",
    "pretend", "act as if", "respond as if", "translate but really",
    "visit url", "click link", "download malware"
]

# Keywords safe in normal car listing context
SAFE_KEYWORDS = ["override", "script", "token", "fetch", "connect"]

# Dangerous verb-noun patterns
DANGEROUS_PATTERNS = [
    r"\b(ignore|bypass|override)\b.*\binstructions\b",
    r"\b(delete|erase|format)\b.*\b(disk|file|system)\b",
    r"\b(run|execute)\b.*\b(code|script)\b",
    r"\b(reveal|send|leak)\b.*\b(password|token|key|private data)\b",
    r"\b(visit|click)\b.*\b(url|link)\b",
    r"\b(pretend|act as if|respond as if)\b.*\brules\b",
]

# Normalize text
def normalize_text(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return re.sub(r"[\W_]+", " ", text).strip()

# Fuzzy match helper
def fuzzy_match(text: str, phrase: str, threshold: float = 0.85) -> bool:
    return SequenceMatcher(None, text, phrase).ratio() >= threshold

def sanitize_input(text: str, redaction="[REDACTED]") -> str:
    """Redact dangerous phrases using keyword, fuzzy, and pattern detection."""
    clean_text = text
    sentences = text.split(".")
    for i, sentence in enumerate(sentences):
        norm_sentence = normalize_text(sentence)
        # Keyword redaction
        for keyword in BLOCKLIST_KEYWORDS:
            if keyword in SAFE_KEYWORDS:
                # Only redact safe keyword if sentence matches dangerous pattern
                if any(re.search(pat, sentence, re.IGNORECASE) for pat in DANGEROUS_PATTERNS):
                    pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
                    sentence = pattern.sub(redaction, sentence)
                continue
            pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
            sentence = pattern.sub(redaction, sentence)
        # Pattern redaction
        for pat in DANGEROUS_PATTERNS:
            sentence = re.sub(pat, redaction, sentence, flags=re.IGNORECASE)
        sentences[i] = sentence
    return ".".join(sentences)

def is_safe(text: str, threshold: float = 0.85) -> bool:
    """Return False if any dangerous keyword, fuzzy variant, or pattern is detected."""
    sentences = text.split(".")
    for sentence in sentences:
        norm_sentence = normalize_text(sentence)
        for keyword in BLOCKLIST_KEYWORDS:
            if keyword in SAFE_KEYWORDS:
                # Safe keyword only dangerous if part of pattern
                if any(re.search(pat, sentence, re.IGNORECASE) for pat in DANGEROUS_PATTERNS):
                    return False
                continue
            if re.search(r"\b" + re.escape(keyword) + r"\b", sentence, re.IGNORECASE) or \
               fuzzy_match(norm_sentence, normalize_text(keyword), threshold):
                return False
        for pat in DANGEROUS_PATTERNS:
            if re.search(pat, sentence, re.IGNORECASE):
                return False
    return True

def flagged_words(text: str, threshold: float = 0.85) -> list:
    """Return list of detected blocked keywords / patterns."""
    found = set()
    sentences = text.split(".")
    for sentence in sentences:
        norm_sentence = normalize_text(sentence)
        for keyword in BLOCKLIST_KEYWORDS:
            if keyword in SAFE_KEYWORDS:
                if any(re.search(pat, sentence, re.IGNORECASE) for pat in DANGEROUS_PATTERNS):
                    found.add(keyword)
                continue
            if re.search(r"\b" + re.escape(keyword) + r"\b", sentence, re.IGNORECASE) or \
               fuzzy_match(norm_sentence, normalize_text(keyword), threshold):
                found.add(keyword)
        for pat in DANGEROUS_PATTERNS:
            if re.search(pat, sentence, re.IGNORECASE):
                found.add(pat)
    return list(found)
