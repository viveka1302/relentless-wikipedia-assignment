from langchain_google_genai import ChatGoogleGenerativeAI
from .connection import GOOGLE_API_KEY
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key= GOOGLE_API_KEY,
    google_api_key= GOOGLE_API_KEY
)