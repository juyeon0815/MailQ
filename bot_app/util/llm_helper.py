from openai import AzureOpenAI
import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()    

api_key = os.getenv("OPENAI_API_KEY")
api_version = os.getenv("OPENAI_API_VERSION")
api_endpoint = os.getenv("OPENAI_API_ENDPOINT")
model = os.getenv("OPENAI_MODEL")



def generate_response(prompt: str, content: str) -> str:

    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_endpoint
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
