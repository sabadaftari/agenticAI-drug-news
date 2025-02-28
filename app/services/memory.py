
from uuid import uuid4
from pinecone import Pinecone, ServerlessSpec
import openai

from config import (
    PINECONE_API_KEY,
    PINECONE_ENV,
    PINECONE_INDEX_NAME,
    EMBEDDING_DIMENSION
)

# Lazy-load the embedding model
_index = None

def get_embedding(text: str) -> list:

    response = openai.Embedding.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    embedding = response["data"][0]["embedding"]
    return embedding

def init_pinecone():

    global _index
    if _index is None:        
        pc = Pinecone(
            api_key=PINECONE_API_KEY
        )

        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            pc.create_index(
                name=PINECONE_INDEX_NAME, 
                dimension=EMBEDDING_DIMENSION, 
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=PINECONE_ENV
                )
            )
       
        _index = pc.Index(PINECONE_INDEX_NAME)
    return _index


def store_conversation(index, user_query: str, bot_response: str, conversation_id: str):

    user_emb = get_embedding(user_query)
    bot_emb = get_embedding(bot_response)
    
    # to avoide overwriting we use unique IDs (e.g. uuid, timestamps)
    user_id = f"{conversation_id}-user-{uuid4()}"
    bot_id = f"{conversation_id}-assistant-{uuid4()}"

    index.upsert([
        (user_id, user_emb, {"role": "user", "content": user_query, "conversation_id": conversation_id}),
        (bot_id, bot_emb, {"role": "assistant", "content": bot_response, "conversation_id": conversation_id})
    ])
