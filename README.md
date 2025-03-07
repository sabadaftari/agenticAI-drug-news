# Agentic AI-Driven Assistant with Notifications

This project is a FastAPI-based microservice that acts as an AI-driven assistant. It processes user queries to fetch and summarize external data—such as clinical trial information or pharmaceutical news—and then sends the generated summary as a Slack DM or creates a Gmail draft. The project leverages the following components:

- **OpenAI API**: For generating concise summaries and insights.
- **Research Publication websites API**: For retrieving real-time data from the literature and clinical trials.
- **Pinecone**: For storing conversation embeddings and enabling multi-turn memory.
- **Notification Services**: To send the final summary as either a Slack DM or a Gmail draft.

## Features

- **Real-Time Data Fetching**: Retrieves the latest clinical trial data and news over the past two years via the clinicaltrial.gov API, EuropePMC API and PubMed API.
- **AI Summarization**: Generates a formatted summary with OpenAI’s ChatCompletion API. You can adjust your desired llm.
- **Conversation Memory**: Uses Pinecone to store and retrieve conversation context.
- **Integrated Notifications**: Sends summaries as Slack direct messages or creates Gmail drafts based on configuration.
- **Multi-Turn Conversation Support**: Uses conversation IDs to maintain context across multiple interactions.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/agentic-ai-assistant.git
   cd agentic-ai-assistant

2. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt

3. **Configure Environment Variables**:
    Create a .env file in the root directory with content similar to the following:

    ```bash
    # OpenAI configuration
    OPENAI_API_KEY=your_openai_api_key_here
    OPENAI_MODEL=gpt-4-mini
    EMBEDDING_DIMENSION=1536

    # Pinecone configuration
    PINECONE_API_KEY=your_pinecone_api_key_here
    PINECONE_ENV=us-east-1
    PINECONE_INDEX_NAME=pharma-assistant-memory
    
4. **Run the Application**: 
    If you are going to make a gmail draft please run the command below first and complete the login flow. so that it saves the authorized credentials (with refresh token, client_id, client_secret, token_uri, etc.) to token.json. If you are using only slack notification then skip to FastAPI server.
    ```bash
    python gmail_auth_flow.py
    ```
    Start the FastAPI server using Uvicorn:

    ```bash
    uvicorn app.main:app --reload
    ```
    or 
    ```bash
    python main.py
    ```
    if you are using docker to run the app, start with the commands below after you made an image:
    ```bash
    docker run -p 8000:8000 name_of_image
    ```

5. **API Endpoints**:
    This endpoint processes a chat query, retrieves relevant data, generates a summary using an LLM, stores the conversation, and sends a notification.You can pass your disease name and conversation ID.

    ### POST `/api/chat`

    #### Request

    - **Method:** POST
    - **URL:** `/api/chat`
    - **Headers:** `Content-Type: application/json`
    - **Body Example:**

    ```json
    {
    "query": "Cardiovascular",
    "conversation_id": "e4691926-3e4e-4816-b1b8-d3a455cd0215"
    }
    ```
    ```bash
    curl -X POST -H "Content-Type: application/json" \
            -d "{\"query\": \”Cardiovascular\”, \"conversation_id\": \"e4691926-3e4e-4816-b1b8-d3a455cd0215\"}" \
            http://127.0.0.1:8000/api/chat | jq

**Contributing**:
Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
If you are a pharmseudical expert and you would like to request some features email me at sabadaftari@gmail.com
