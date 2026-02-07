from sqlmodel import Session
from app.db.models import Message


def save_message(
    conversation_id: int,
    user_id: str,
    role: str,
    content: str,
    session: Session,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
