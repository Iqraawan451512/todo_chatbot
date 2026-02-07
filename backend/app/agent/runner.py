"""Agent orchestrator — chains sub-agents to process user messages.

Pipeline:  LanguageAgent → IntentAgent → TaskAgent → ResponseAgent

The orchestrator is stateless. Each sub-agent is independent and
reusable. All task mutations go through MCP tools exclusively.
"""
from dataclasses import dataclass, field

from app.agent.language_agent import detect_language
from app.agent.intent_agent import detect_intent
from app.agent.task_agent import execute_task
from app.agent.response_agent import format_response


@dataclass
class AgentResult:
    response: str
    tool_calls: list[dict] = field(default_factory=list)


async def run_agent(
    user_id: str,
    conversation_history: list[dict],
    user_message: str,
) -> AgentResult:
    """Orchestrate sub-agents to process the user message.

    Pipeline:
        1. LanguageAgent — detect language (en / ur / roman_ur)
        2. IntentAgent   — parse intent + extract parameters
        3. TaskAgent      — execute MCP tool calls
        4. ResponseAgent  — format response in detected language

    Args:
        user_id: The authenticated user's ID.
        conversation_history: Prior messages (available for future use).
        user_message: The new user message to process.

    Returns:
        AgentResult with the response and tool calls made.
    """
    # 1. Detect language
    lang_result = detect_language(user_message)
    language = lang_result.language

    # 2. Parse intent and extract parameters
    intent = detect_intent(user_message, language)

    # 3. Execute MCP tool calls
    task_result = execute_task(user_id, intent)

    # 4. Format response in the detected language
    response = format_response(language, intent, task_result)

    return AgentResult(response=response, tool_calls=task_result.tool_calls)
