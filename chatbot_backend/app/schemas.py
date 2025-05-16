from pydantic import BaseModel, EmailStr

from typing import List, Optional, Dict, Any

# Base user schema
class UserBase(BaseModel):
    username: str
    email: EmailStr

# For user creation (signup)
class UserCreate(UserBase):
    password: str

# Response schema (what we return to client)
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# For login requests
class UserLogin(BaseModel):
    username: str
    password: str

class ChatMessage(BaseModel):
    user_id: str
    message: str
    email: EmailStr | None = None  # Only required at end


class ChatRequest(BaseModel):
    user_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str


class AgentReply(BaseModel):
    session_id: str
    content: str
    user_id: int




class Condition(BaseModel):
    field: str             # e.g. "order_age_hours"
    operator: str          # e.g. "<"
    value: Any             # e.g. 24

class RuleCreate(BaseModel):
    tool_name: str
    condition: str
    on_deny_message: Optional[str] = None
    escalate_after_retries: int = 2