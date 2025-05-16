from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum
from .db import Base
from sqlalchemy.sql import func
import enum
from sqlalchemy.orm import relationship

class UserRole(enum.Enum):
    user = "user"
    manager = "manager"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tier = Column(String, default="standard")
    has_escalated = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "tier": self.tier,
        }

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    product_name = Column(String, nullable=False)
    status = Column(String, default="active")  # active, cancelled, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    dispatched_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    product_type = Column(String, nullable=True) # e.g. "limited","speacial"

    user = relationship("User")

    @staticmethod
    def format_dt(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None
    
    def to_dict(self):
        return {
            "id": self.id,
            "product_name": self.product_name,
            "status": self.status,
            "created_at": str(self.format_dt(self.created_at)),
            "cancelled_at": str(self.cancelled_at) if self.cancelled_at else None,
            "product_type": self.product_type,
        }

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id=Column(Integer,ForeignKey("users.id"))
    tool_name = Column(String, nullable=False)  # e.g. "cancel_order"
    conditions = Column(String,nullable = False)
    on_deny_message = Column(String, nullable=True)
    escalate_after_retries = Column(Integer, default=4)  # how many times user can insist before escalation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")

    @staticmethod
    def format_dt(dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S%z") if dt else None
    
    def to_dict(self):
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "conditions": self.conditions,
            "on_deny_message": self.on_deny_message,
            "escalate_after_retries": self.escalate_after_retries,
            "created_at": str(self.format_dt(self.created_at)),
            "updated_at": str(self.format_dt(self.updated_at)),
        }

class ToolRetry(Base):
    __tablename__ = "tool_retries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    tool_name = Column(String, nullable=False)
    context_key = Column(String, nullable=True)  # e.g., "order_123"
    retry_count = Column(Integer, default=0)
    last_attempt_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tool_name": self.tool_name,
            "context_key": self.context_key,
            "retry_count": self.retry_count,
            "last_attempt_at": str(self.last_attempt_at),
        }



class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id"))
    user_id = Column(Integer, ForeignKey("users.id"))  # optional for anonymous
    sender = Column(String)  # "user", "bot", "assistant"
    message = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    retries = Column(Integer, default=0)  # number of times user insisted on a message



class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String, unique=True, index=True)  # UUID
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    ended_by = Column(String, nullable=True)  # user/bot/timeout
