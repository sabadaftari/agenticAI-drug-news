import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # or another model
EMBEDDING_DIMENSION = 1536

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "YOUR_PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-west4-gcp")  # or your region
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "pharma-assistant-memory")

NOTIFICATION_TYPE = os.getenv("NOTIFICATION_TYPE")

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_USER_ID = os.getenv("SLACK_USER_ID")

GMAIL_CREDENTIALS_JSON = os.getenv("GMAIL_CREDENTIALS_JSON")