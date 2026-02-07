"""IntentAgent — Detects user intent and extracts parameters.

Supports English, Urdu script, and Roman Urdu.
Returns a structured IntentResult with the intent type and extracted params.

This agent is stateless, reusable, and independent of other agents.
"""
import re
from dataclasses import dataclass, field

# Regex fragment for "description" misspellings
_DESC_KW = r'(?:desc|disc)(?:r?(?:i|u)ption|ription|ruption)?'

# ── Intent keywords per language ────────────────────────────────────

_EN_INTENTS: dict[str, list[str]] = {
    "complete": ["complete", "mark", "done", "finish"],
    "delete":   ["delete", "remove"],
    "update":   ["update", "change", "rename", "edit"],
    "list":     ["show", "list", "all my", "what", "pending", "incomplete", "completed"],
    "add":      ["add", "create", "remember", "save", "new task"],
}

_ROMAN_UR_INTENTS: dict[str, list[str]] = {
    "complete": ["mukammal", "mukamal", "hogaya", "hogya", "hogai", "complete karo",
                 "mark karo", "done karo", "finish karo", "khatam"],
    "delete":   ["hatao", "mitao", "delete karo", "nikalo", "remove karo"],
    "update":   ["badlo", "badal", "update karo", "change karo", "edit karo", "tabdeel"],
    "list":     ["dikhao", "dikha", "batao", "bata", "show karo", "list karo",
                 "kya hai", "konse", "kaun se", "sab dikhao"],
    "add":      ["shamil", "shaamil", "dalo", "daalo", "add karo", "banao",
                 "naya task", "naya kaam", "yaad", "save karo"],
}

_UR_INTENTS: dict[str, list[str]] = {
    "complete": ["مکمل", "ہوگیا", "ہوگئی", "مکمل کرو", "ختم", "ختم کرو"],
    "delete":   ["حذف", "ہٹاؤ", "مٹاؤ", "حذف کرو", "نکالو", "ڈیلیٹ"],
    "update":   ["تبدیل", "بدلو", "اپڈیٹ", "تبدیل کرو", "بدل دو", "ایڈٹ"],
    "list":     ["دکھاؤ", "بتاؤ", "دکھاؤ سب", "کیا ہے", "کون سے", "ٹاسک دکھاؤ"],
    "add":      ["شامل", "ڈالو", "بناؤ", "نیا ٹاسک", "نیا کام", "یاد", "شامل کرو"],
}

# ── Status filter keywords ──────────────────────────────────────────

_FILTER_PENDING = {
    "en":       ["pending", "incomplete", "not done", "remaining"],
    "roman_ur": ["pending", "adhura", "adhoora", "baqi", "remaining"],
    "ur":       ["زیر التوا", "ادھورا", "باقی", "نامکمل"],
}

_FILTER_COMPLETED = {
    "en":       ["completed", "done", "finished"],
    "roman_ur": ["mukammal", "mukamal", "hogaya", "hogya", "complete", "done"],
    "ur":       ["مکمل", "ہوگیا", "ہوگئی", "ختم شدہ"],
}


@dataclass
class IntentResult:
    """Structured output from intent detection."""
    intent: str                           # add, list, complete, delete, update
    task_id: int | None = None
    title: str | None = None
    description: str | None = None
    status_filter: str = "all"            # all, pending, completed
    update_field: str | None = None       # "title" or "description"
    update_value: str | None = None
    raw_message: str = ""


def detect_intent(message: str, language: str) -> IntentResult:
    """Detect intent and extract parameters from the message.

    Args:
        message: The raw user message.
        language: Detected language ("en", "ur", "roman_ur").

    Returns:
        IntentResult with parsed intent and parameters.
    """
    result = IntentResult(intent="add", raw_message=message)
    lower = message.lower().strip()

    # 1. Detect intent
    result.intent = _match_intent(lower, language)

    # 2. Extract task ID (works across all languages — numbers are universal)
    result.task_id = _parse_task_id(message)

    # 3. Extract intent-specific parameters
    if result.intent == "add":
        result.title, result.description = _extract_add_params(message, language)

    elif result.intent == "list":
        result.status_filter = _detect_status_filter(lower, language)

    elif result.intent == "update":
        result.update_field, result.update_value = _extract_update_params(message, lower)

    return result


def _match_intent(lower: str, language: str) -> str:
    """Match intent keywords in order of priority."""
    if language == "ur":
        intent_map = _UR_INTENTS
    elif language == "roman_ur":
        intent_map = _ROMAN_UR_INTENTS
    else:
        intent_map = _EN_INTENTS

    # Check all intent maps (primary language + English fallback)
    for intent_order in ["complete", "delete", "update", "list", "add"]:
        keywords = intent_map.get(intent_order, [])
        if any(kw in lower for kw in keywords):
            return intent_order

    # Fallback: also check English keywords for non-English messages
    if language != "en":
        for intent_order in ["complete", "delete", "update", "list", "add"]:
            keywords = _EN_INTENTS.get(intent_order, [])
            if any(kw in lower for kw in keywords):
                return intent_order

    return "add"


def _parse_task_id(message: str) -> int | None:
    """Extract task ID from the message (language-agnostic)."""
    # "task 5", "task #5", "ٹاسک 5"
    match = re.search(r'(?:task|ٹاسک)\s*#?\s*(\d+)', message, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # "id:4", "id 4", "نمبر 4"
    match = re.search(r'(?:id|نمبر)\s*:?\s*(\d+)', message, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Standalone number
    match = re.search(r'\b(\d+)\b', message)
    if match:
        return int(match.group(1))
    return None


def _extract_add_params(message: str, language: str) -> tuple[str | None, str | None]:
    """Extract title and optional description for add intent."""
    # Remove command keywords to get raw content
    if language == "en":
        keywords = ["add", "create", "remember", "save", "new task"]
    elif language == "roman_ur":
        keywords = ["add karo", "shamil karo", "shaamil karo", "dalo", "daalo",
                     "banao", "naya task", "naya kaam", "yaad rakhna", "yaad",
                     "save karo", "add", "create"]
    else:
        keywords = ["شامل کرو", "ڈالو", "بناؤ", "نیا ٹاسک", "نیا کام", "یاد رکھو",
                     "شامل", "add", "create"]

    raw = _strip_command(message, keywords)
    if not raw:
        return None, None

    # Try to parse "title" with description "desc"
    match = re.match(
        r'^["\']?(.+?)["\']?\s+(?:with\s+)?(?:description|desc|تفصیل)\s+["\']?(.+?)["\']?\s*$',
        raw, re.IGNORECASE,
    )
    if match:
        return match.group(1).strip(), match.group(2).strip()

    title = raw.strip().strip("'\"")
    return title, None


def _strip_command(message: str, keywords: list[str]) -> str:
    """Remove the command keyword from the message and clean up fillers."""
    lower = message.lower()
    for kw in sorted(keywords, key=len, reverse=True):
        idx = lower.find(kw)
        if idx != -1:
            raw = message[idx + len(kw):].strip()
            # Clean English fillers
            for filler in ["a task to ", "a task ", "task to ", "task ", "to ",
                           "ek task ", "ek kaam ", "kaam "]:
                if raw.lower().startswith(filler):
                    raw = raw[len(filler):]
                    break
            return raw.strip().strip("'\"")
    return message.strip().strip("'\"")


def _detect_status_filter(lower: str, language: str) -> str:
    """Detect list filter from message."""
    pending_kws = _FILTER_PENDING.get(language, []) + _FILTER_PENDING["en"]
    completed_kws = _FILTER_COMPLETED.get(language, []) + _FILTER_COMPLETED["en"]

    if any(kw in lower for kw in pending_kws):
        return "pending"
    if any(kw in lower for kw in completed_kws):
        return "completed"
    return "all"


def _extract_update_params(message: str, lower: str) -> tuple[str | None, str | None]:
    """Extract update field and value."""
    is_desc = bool(re.search(
        r'\b' + _DESC_KW + r'\b|تفصیل|description',
        lower,
    ))

    if is_desc:
        desc_pattern = _DESC_KW + r'|تفصیل'
        match = re.search(
            r'(?:' + desc_pattern + r')\s+(?:to\s+|with\s+|se\s+|mein\s+)?["\']?(.+?)["\']?\s*$',
            message, re.IGNORECASE,
        )
        if match:
            return "description", match.group(1).strip().strip("'\"")
        return "description", None
    else:
        # Try "title to/with X"
        match = re.search(r'\btitle\s+(?:to|with)\s+["\']?(.+?)["\']?\s*$', message, re.IGNORECASE)
        if match:
            return "title", match.group(1).strip().strip("'\"")
        # Try "to/with/se X" or "ko X"
        match = re.search(r'\b(?:to|with|se|ko|mein|سے|کو|میں)\s+["\']?(.+?)["\']?\s*$', message, re.IGNORECASE)
        if match:
            return "title", match.group(1).strip().strip("'\"")
        return "title", None
