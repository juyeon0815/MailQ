# app/util/embedding_helper.py

from chromadb import PersistentClient
from chromadb.config import Settings
from .openai_helper import get_embedding

# 새로운 방식으로 클라이언트 생성
chroma_client = PersistentClient(path="./chroma_db")

# 컬렉션 불러오기 또는 생성
collection = chroma_client.get_or_create_collection(name="emails")

def embed_and_store(user_email: str, message_id: str, message: dict):
    text = message.get("body", {}).get("content", "")
    print(text)
    if not text.strip():
        return  # 본문 없으면 스킵

    vector = get_embedding(text)
    metadata = {
        "user_email": user_email,
        "subject": message.get("subject", ""),
        "received": message.get("receivedDateTime", ""),
    }

    collection.add(
        ids=[f"{user_email}:{message_id}"],
        documents=[text],
        metadatas=[metadata],
        embeddings=[vector]
    )
