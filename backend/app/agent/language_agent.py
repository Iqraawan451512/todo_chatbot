"""LanguageAgent — Detects the language of a user message.

Supported languages:
  - "en"        — English
  - "ur"        — Urdu script
  - "roman_ur"  — Roman Urdu (Urdu written in Latin characters)

This agent is stateless, reusable, and independent of other agents.
"""
import re
from dataclasses import dataclass

# Unicode range for Arabic/Urdu script characters
_URDU_RANGE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')

# Common Roman Urdu words used in everyday conversation
_ROMAN_URDU_WORDS = {
    # task-related
    "karo", "kardo", "karna", "karein", "kar",
    "banao", "banana", "banaein",
    "dalo", "daalo", "dalna",
    "dikhao", "dikhaein", "dikha",
    "batao", "bataein", "bata",
    "hatao", "hataein", "hata",
    "mitao", "mitaein", "mita",
    "badlo", "badlein", "badal",
    "nikalo", "nikalein",
    # common verbs/words
    "mujhe", "meri", "mera", "mere",
    "yeh", "ye", "woh", "wo",
    "hai", "hain", "tha", "thi", "the",
    "nahi", "nahin", "nhi",
    "aur", "ya", "lekin", "magar",
    "sab", "saray", "tamam",
    "kaam", "kaamm",
    "hogaya", "hogya", "hogai",
    "mukammal", "mukamal",
    "shaamil", "shamil",
    "naya", "nayi", "naye", "nae",
    "purana", "purani", "purane",
    "abhi", "filhal",
    "wala", "wali", "wale",
    "chahiye", "chahie",
    "zaroor", "zaruri", "zaroori",
    "task", "tasks",
    # greetings & fillers
    "salam", "assalam", "walaikum",
    "shukriya", "mashallah",
    "theek", "thik", "accha", "acha",
    "haan", "ji", "jee",
    "bhai", "yaar",
}


@dataclass
class LanguageResult:
    """Result of language detection."""
    language: str          # "en", "ur", or "roman_ur"
    confidence: float      # 0.0 to 1.0


def detect_language(message: str) -> LanguageResult:
    """Detect the language of the user message.

    Args:
        message: The raw user message.

    Returns:
        LanguageResult with detected language and confidence.
    """
    text = message.strip()
    if not text:
        return LanguageResult(language="en", confidence=0.5)

    # Check for Urdu script characters
    urdu_chars = len(_URDU_RANGE.findall(text))
    total_alpha = sum(1 for c in text if c.isalpha())

    if total_alpha > 0 and urdu_chars / total_alpha > 0.3:
        confidence = min(urdu_chars / total_alpha, 1.0)
        return LanguageResult(language="ur", confidence=confidence)

    # Check for Roman Urdu words
    words = set(re.findall(r'[a-zA-Z]+', text.lower()))
    if not words:
        return LanguageResult(language="en", confidence=0.5)

    roman_urdu_matches = words & _ROMAN_URDU_WORDS
    ratio = len(roman_urdu_matches) / len(words)

    if ratio >= 0.3 or len(roman_urdu_matches) >= 2:
        return LanguageResult(language="roman_ur", confidence=min(ratio + 0.3, 1.0))

    return LanguageResult(language="en", confidence=1.0 - ratio)
