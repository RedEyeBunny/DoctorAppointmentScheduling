conversation_store = {}

def get_session(session_id):
    if session_id not in conversation_store:
        conversation_store[session_id] = []
    return conversation_store[session_id]
