from langchain_openai import ChatOpenAI
from app.config import OPENAI_API_KEY

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0
)