token_map = {}  # user_id: access_token

def save_token(user_id, token):
    token_map[user_id] = token

def get_token(user_id):
    return token_map.get(user_id)

conversation_refs = {}

def save_conversation_reference(user_id, reference):
    conversation_refs[user_id] = reference

def get_conversation_reference(user_id):
    return conversation_refs.get(user_id)