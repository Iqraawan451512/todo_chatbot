from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select
from app.db.models import Conversation, Message


def get_or_create_conversation(
    user_id: str,
    conversation_id: Optional[int],
    session: Session,
) -> Conversation:
    if conversation_id is not None:
        conversation = session.get(Conversation, conversation_id)
        if conversation is not None and conversation.user_id == user_id:
            return conversation

    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def load_history(conversation_id: int, session: Session) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return list(session.exec(statement).all())
