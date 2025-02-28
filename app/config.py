import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # or another model
EMBEDDING_DIMENSION = 1536

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "YOUR_PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-west4-gcp")  # or your region
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "stock-assistant-memory")
