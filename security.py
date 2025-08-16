import re

BLOCKLIST = [
    "ignore previous",
    "system command",
    "delete all",
    "shutdown",
    "format disk"
]

# Precompile regex for performance
BLOCKLIST_PATTERNS = [
    re.compile(re.escape(bad), re.IGNORECASE) for bad in BLOCKLIST
]

def sanitize_input(text: str) -> str:
    """Remove suspicious phrases from user text."""
    clean_text = text
    for pattern in BLOCKLIST_PATTERNS:
        clean_text = pattern.sub("[REDACTED]", clean_text)
    return clean_text

def is_safe(text: str) -> bool:
    """Check if text is safe for LLM processing."""
    return not any(pattern.search(text) for pattern in BLOCKLIST_PATTERNS)

if __name__ == "__main__":
    test_text = "Please shutdown the system command after backup."
    print("Original:", test_text)
    print("Sanitized:", sanitize_input(test_text))
    print("Is safe?", is_safe(test_text))
