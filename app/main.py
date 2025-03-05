import uvicorn
from fastapi import FastAPI
from routers import chat
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)

app = FastAPI(
    title="Agentic AI-driven Research Summerizing Assistant",
    description="FastAPI microservice using OpenAI models for stock insights and conversation memory",
    version="1.0.0"
)

app.include_router(chat.router, prefix="/api", tags=["Chat"]) # include router

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, log_level="info")