"""ResponseAgent — Formats friendly responses in the detected language.

Generates user-facing messages in English, Urdu script, or Roman Urdu
based on the language detected by LanguageAgent.

This agent is stateless, reusable, and independent of other agents.
"""
from app.agent.intent_agent import IntentResult
from app.agent.task_agent import TaskResult


def format_response(
    language: str,
    intent: IntentResult,
    task_result: TaskResult,
) -> str:
    """Format a user-friendly response in the detected language.

    Args:
        language: Detected language ("en", "ur", "roman_ur").
        intent: The parsed intent from IntentAgent.
        task_result: The execution result from TaskAgent.

    Returns:
        A formatted response string.
    """
    if not task_result.success:
        return _format_error(language, intent, task_result)

    if intent.intent == "add":
        return _format_add(language, task_result, intent)
    elif intent.intent == "list":
        return _format_list(language, task_result, intent)
    elif intent.intent == "complete":
        return _format_complete(language, task_result)
    elif intent.intent == "delete":
        return _format_delete(language, task_result)
    elif intent.intent == "update":
        return _format_update(language, task_result, intent)

    return _t(language, "I didn't understand that.", "سمجھ نہیں آیا۔", "Samajh nahi aaya.")


# ── Response formatters ─────────────────────────────────────────────

def _format_add(language: str, result: TaskResult, intent: IntentResult) -> str:
    data = result.data
    title = data.get("title", intent.title)
    task_id = data.get("task_id", "?")

    base = _t(
        language,
        f"Added task '{title}' (ID: {task_id})",
        f"ٹاسک '{title}' شامل کر دیا گیا (ID: {task_id})",
        f"Task '{title}' add ho gaya (ID: {task_id})",
    )

    if intent.description:
        desc_note = _t(
            language,
            f" with description: {intent.description}",
            f" — تفصیل: {intent.description}",
            f" — description: {intent.description}",
        )
        base += desc_note

    return base


def _format_list(language: str, result: TaskResult, intent: IntentResult) -> str:
    tasks = result.data
    if not tasks:
        filter_text = intent.status_filter
        return _t(
            language,
            f"You have no {filter_text} tasks.",
            f"آپ کے کوئی {filter_text} ٹاسک نہیں ہیں۔",
            f"Aap ke koi {filter_text} tasks nahi hain.",
        )

    header = _t(
        language,
        f"Your tasks ({intent.status_filter}):" if intent.status_filter != "all" else "Your tasks:",
        f"آپ کے ٹاسک ({intent.status_filter}):" if intent.status_filter != "all" else "آپ کے ٹاسک:",
        f"Aap ke tasks ({intent.status_filter}):" if intent.status_filter != "all" else "Aap ke tasks:",
    )

    lines = []
    for t in tasks:
        status_label = _t(
            language,
            "done" if t["completed"] else "pending",
            "مکمل" if t["completed"] else "زیر التوا",
            "mukammal" if t["completed"] else "pending",
        )
        line = f"  {t['task_id']}. {t['title']} [{status_label}]"
        desc = t.get("description")
        if desc:
            desc_label = _t(language, "Description", "تفصیل", "Description")
            line += f"\n      {desc_label}: {desc}"
        lines.append(line)

    return f"{header}\n" + "\n".join(lines)


def _format_complete(language: str, result: TaskResult) -> str:
    data = result.data
    title = data.get("title", "")

    if data.get("status") == "already_completed":
        return _t(
            language,
            f"Task '{title}' is already completed.",
            f"ٹاسک '{title}' پہلے سے مکمل ہے۔",
            f"Task '{title}' pehle se mukammal hai.",
        )

    return _t(
        language,
        f"Marked task '{title}' as complete!",
        f"ٹاسک '{title}' مکمل ہو گیا!",
        f"Task '{title}' mukammal ho gaya!",
    )


def _format_delete(language: str, result: TaskResult) -> str:
    title = result.data.get("title", "")
    return _t(
        language,
        f"Deleted task '{title}'.",
        f"ٹاسک '{title}' حذف کر دیا گیا۔",
        f"Task '{title}' delete ho gaya.",
    )


def _format_update(language: str, result: TaskResult, intent: IntentResult) -> str:
    data = result.data
    if intent.update_field == "description":
        desc = data.get("description", intent.update_value)
        task_id = data.get("task_id", intent.task_id)
        return _t(
            language,
            f"Updated description for task {task_id} to: {desc}",
            f"ٹاسک {task_id} کی تفصیل اپڈیٹ ہو گئی: {desc}",
            f"Task {task_id} ki description update ho gayi: {desc}",
        )

    title = data.get("title", intent.update_value)
    return _t(
        language,
        f"Updated task title to '{title}'.",
        f"ٹاسک کا عنوان '{title}' میں تبدیل ہو گیا۔",
        f"Task ka title '{title}' mein badal gaya.",
    )


# ── Error responses ─────────────────────────────────────────────────

def _format_error(language: str, intent: IntentResult, result: TaskResult) -> str:
    error = result.error or "unknown"

    if error == "missing_title":
        return _t(
            language,
            "Please provide a task title. Example: 'Add a task to buy groceries'",
            "براہ کرم ٹاسک کا عنوان بتائیں۔ مثال: 'خریداری کا ٹاسک شامل کرو'",
            "Task ka title batayein. Example: 'Add karo buy groceries'",
        )

    if error == "missing_task_id":
        if intent.intent == "complete":
            return _t(language,
                "Please specify a task ID. Example: 'Complete task 3'",
                "براہ کرم ٹاسک نمبر بتائیں۔ مثال: 'ٹاسک 3 مکمل کرو'",
                "Task ka number batayein. Example: 'Task 3 complete karo'")
        if intent.intent == "delete":
            return _t(language,
                "Please specify a task ID. Example: 'Delete task 2'",
                "براہ کرم ٹاسک نمبر بتائیں۔ مثال: 'ٹاسک 2 حذف کرو'",
                "Task ka number batayein. Example: 'Task 2 delete karo'")
        return _t(language,
            "Please specify a task ID. Example: 'Update task 1 title to Call mom'",
            "براہ کرم ٹاسک نمبر بتائیں۔ مثال: 'ٹاسک 1 کا عنوان تبدیل کرو'",
            "Task ka number batayein. Example: 'Task 1 update karo'")

    if error == "missing_update_value":
        field = result.data.get("update_field", "title") if isinstance(result.data, dict) else "title"
        if field == "description":
            return _t(language,
                "Please provide the new description. Example: 'Update task 1 description to My new description'",
                "براہ کرم نئی تفصیل بتائیں۔",
                "Nayi description batayein. Example: 'Task 1 description update karo to nayi description'")
        return _t(language,
            "Please provide the new title. Example: 'Update task 1 title to New title'",
            "براہ کرم نیا عنوان بتائیں۔",
            "Naya title batayein. Example: 'Task 1 title update karo to naya title'")

    # Generic tool error
    return _t(
        language,
        f"Could not complete the operation: {error}",
        f"عمل مکمل نہیں ہو سکا: {error}",
        f"Operation complete nahi ho saka: {error}",
    )


# ── Helper ──────────────────────────────────────────────────────────

def _t(language: str, en: str, ur: str, roman_ur: str) -> str:
    """Pick the right translation based on language."""
    if language == "ur":
        return ur
    if language == "roman_ur":
        return roman_ur
    return en
