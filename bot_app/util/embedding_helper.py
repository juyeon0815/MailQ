# embedding_helper.py
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

embedding_model = os.getenv("EMBEDDING_MODEL")

client = AzureOpenAI(
    api_key=os.getenv("EMBEDDING_API_KEY"),
    api_version=os.getenv("EMBEDDING_API_VERSION"),
    azure_endpoint=os.getenv("EMBEDDING_API_ENDPOINT")
)

def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        input=text,
        model=embedding_model
    )
    return response.data[0].embedding
