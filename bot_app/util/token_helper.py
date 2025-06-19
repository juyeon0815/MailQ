import os
import json
import time

class FileTokenStore:
    def __init__(self, directory="tokens"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def _get_path(self, user_id):
        return os.path.join(self.directory, f"{user_id}.json")

    def save_token(self, user_id, access_token, expires_in):
        token_data = {
            "access_token": access_token,
            "expires_at": time.time() + expires_in
        }
        with open(self._get_path(user_id), "w") as f:
            json.dump(token_data, f)
        print(f"[SAVE] token for {user_id}, expires in {expires_in}s")

    def get_token(self, user_id):
        try:
            with open(self._get_path(user_id), "r") as f:
                data = json.load(f)
            if time.time() > data["expires_at"]:
                print(f"[EXPIRED] token for {user_id}")
                return None
            return data["access_token"]
        except FileNotFoundError:
            return None

    def delete_token(self, user_id):
        try:
            os.remove(self._get_path(user_id))
            print(f"[DELETE] token for {user_id}")
        except FileNotFoundError:
            pass

    def cleanup_expired_tokens(self):
        now = time.time()
        for filename in os.listdir(self.directory):
            path = os.path.join(self.directory, filename)
            with open(path, "r") as f:
                data = json.load(f)
            if now > data.get("expires_at", 0):
                os.remove(path)
                print(f"[CLEANUP] expired token removed: {filename}")


conversation_refs = {}

def save_conversation_reference(user_id, reference):
    conversation_refs[user_id] = reference

def get_conversation_reference(user_id):
    return conversation_refs.get(user_id)
