from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models, auth
from contextlib import asynccontextmanager
from .db import Base, engine, get_db, SessionLocal
from .utils import end_chat_session, get_or_create_active_session, save_message
from .chatbot_logic import chatbot_response
from .models import ChatSession, User, ChatMessage, Rule
from sqlalchemy import desc
from .schemas import AgentReply,RuleCreate
from .intent import detect_intent
from fastapi.middleware.cors import CORSMiddleware
from .test import seed_orders

#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

#seed_orders(80)
# Initialize DB tables (only needed once)


app = FastAPI()
# Allow your Vue frontend (or everything during dev)
origins = [
    "http://localhost:5173",  # Vue dev server
    # Add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Specific domains, or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)

# Signup route
@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return auth.create_user(db, user)

# Login route
@app.post("/login", response_model=schemas.UserResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    return user



@app.post("/rules/")
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    db_rule = Rule(
        tool_name=rule.tool_name,
        conditions=rule.condition,
        on_deny_message=rule.on_deny_message,
        escalate_after_retries=rule.escalate_after_retries
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return {"message": "Rule created", "rule_id": db_rule.id}




def generate_reply(db : Session,message: str,user:User) -> str:
    
    intent = detect_intent(message.message)
    
    if intent == "goodbye":
        end_chat_session(db,user,"user", message.email)
        return {"response": "Goodbye! Feel free to come back anytime."}
    
    elif intent == "escalation":
        user.has_escalated = True
        db.commit()
        return {"response": "Sure, I'll connect you to a human agent now."}
    
    else:
        response = chatbot_response(message.message)
        return {"response": response}
    





# NEW: Chat route
@app.post("/chat")
def chat(message: schemas.ChatMessage, db: Session = Depends(get_db)):


    user = db.query(User).filter(User.id == message.user_id).first()

    session = get_or_create_active_session(db, user)

    save_message(db, message.user_id, session.session_id, "user", message.message)
    
    if not user.has_escalated:

        bot_reply = generate_reply(db,message,user)

        save_message(db, message.user_id, session.session_id, "bot", bot_reply["response"])        

        return {"reply": bot_reply}
    
    generate_reply(db,message,user)

@app.get("/escalated-users")
def get_escalated_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.ended_at == None).all()

    result = []

    for session in sessions:
        user = db.query(User).filter(User.id == session.user_id,User.has_escalated == True).first()
        if not user:
            continue

        last_message = db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session.session_id)\
            .order_by(desc(ChatMessage.timestamp))\
            .first()

        result.append({
            "user_id": user.id,
            "user_name": user.username,
            "email": user.email,
            "last_message": last_message.message if last_message else None,
            "last_message_time": last_message.timestamp if last_message else None
        })

    return result

@app.get("/agent/chat/{user_id}")
def get_user_escalated_chat(user_id: int, db: Session = Depends(get_db)):
    # Find the most recent escalated session for the user that's still active
    session = db.query(ChatSession)\
        .filter(
            ChatSession.user_id == user_id,
            ChatSession.ended_at == None
        )\
        .order_by(desc(ChatSession.started_at))\
        .first()

    if not session:
        raise HTTPException(status_code=404, detail="No active escalated session found for this user.")

    # Get all messages from that session
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.session_id == session.session_id,
                ChatMessage.user_id == user_id)\
        .order_by(ChatMessage.timestamp.asc())\
        .all()

    chat = [
        {
            "sender": msg.sender,
            "content": msg.message,
            "timestamp": msg.timestamp
        }
        for msg in messages
    ]

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "chat": chat
    }


@app.post("/agent/reply")
def agent_reply(payload: AgentReply, db: Session = Depends(get_db)):
    # Check if session exists and is escalated
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    

    session =  get_or_create_active_session(db, user)

    if not session:
        raise HTTPException(status_code=404, detail="No active escalated session found.")

    save_message(db, payload.user_id, session.session_id, "Agent", payload.content)

    return {
        "message": "Reply sent successfully.",
        "sent": {
            "content": payload.content,
        }
    }




# NEW: End chat and trigger feedback email
@app.post("/end_chat")
def end_chat(message: schemas.ChatMessage):
    status_msg = end_chat_session(message.user_id, message.email)
    return {"status": status_msg}

