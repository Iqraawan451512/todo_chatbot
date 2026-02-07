"""Chat API endpoint.

POST /api/{user_id}/chat — the single conversational endpoint.
All task operations flow through this endpoint via the AI agent and MCP tools.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from app.db.engine import get_session
from app.services.conversations import get_or_create_conversation, load_history
from app.services.messages import save_message
from app.agent.runner import run_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: Optional[list[dict]] = None


@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(user_id: str, request: ChatRequest, session: Session = Depends(get_session)):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # 1. Resolve or create conversation
        conversation = get_or_create_conversation(
            user_id=user_id,
            conversation_id=request.conversation_id,
            session=session,
        )

        # 2. Load conversation history
        history_messages = load_history(conversation.id, session)
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history_messages
        ]

        # 3. Persist user message
        save_message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=request.message,
            session=session,
        )

        # 4. Run agent
        result = await run_agent(
            user_id=user_id,
            conversation_history=conversation_history,
            user_message=request.message,
        )

        # 5. Persist assistant response
        save_message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=result.response,
            session=session,
        )

        # 6. Return response
        return ChatResponse(
            conversation_id=conversation.id,
            response=result.response,
            tool_calls=result.tool_calls if result.tool_calls else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
