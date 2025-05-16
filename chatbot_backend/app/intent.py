intent_keywords = {
    "goodbye": ["bye", "goodbye", "see you", "farewell", "exit", "quit"],
    "escalation": ["human", "agent", "real person", "talk to support", "speak to someone"]
}

def detect_intent(user_input):
    
    for intent, keywords in intent_keywords.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            return intent
    return "chat"  # Default: send to chatbot
