from .email_utils import send_feedback_email
import uuid
from sqlalchemy.orm import Session
from .models import ChatSession, ChatMessage,User, ToolRetry
from datetime import datetime

def get_or_create_active_session(db: Session, user: User) -> str:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user.id, ChatSession.ended_at == None)
        .order_by(ChatSession.started_at.desc())
        .first()
    )
    if session:
        return session

    # Create new session
    session_id = str(uuid.uuid4())
    new_session = ChatSession(user_id=user.id, session_id=session_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def save_message(db: Session, user_id: int, session_id: str, sender: str, message: str):
    msg = ChatMessage(
        user_id=user_id,
        session_id=session_id,
        sender=sender,
        message=message,
    )
    db.add(msg)
    db.commit()



def end_chat_session(db: Session, user: User, ended_by: str, user_email: str | None = None) -> str:
    # Fetch the latest active chat session
    session = (db.query(ChatSession)\
        .filter(ChatSession.user_id == User.id, ChatSession.ended_at == None)\
        .order_by(ChatSession.started_at.desc())\
        .first())

    if not session:
        return "No active session found."

    # Mark the session as ended
    session.ended_at = datetime.utcnow()
    session.ended_by = ended_by
    user.has_escalated = False  # Reset escalation status
    print(user.has_escalated)
    db.commit()

    # Prepare chat history (optional if you want to send it)
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session.session_id)\
        .order_by(ChatMessage.timestamp.asc())\
        .all()

    chat_history = "\n".join([f"{msg.sender}: {msg.message}" for msg in messages])

    if user_email:
        send_feedback_email(user_email, chat_history)
        email_status = "Feedback email sent."
    else:
        email_status = "No email provided."

    return f"Chat ended by {ended_by}. {email_status}"



def get_or_increment_retry(user_id: int, tool_name: str, context_key: str | None, db: Session):
    retry = db.query(ToolRetry).filter_by(
        user_id=user_id,
        tool_name=tool_name,
        context_key=context_key
    ).first()

    if not retry:
        retry = ToolRetry(
            user_id=user_id,
            tool_name=tool_name,
            context_key=context_key,
            retry_count=0
        )
    else:
        retry.retry_count += 1

    retry.last_attempt_at = datetime.utcnow()
    db.add(retry)
    db.commit()
    return retry.retry_count
