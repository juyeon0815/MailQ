# app/util/openai_helper.py

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text: str) -> list:
    response = openai.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding
