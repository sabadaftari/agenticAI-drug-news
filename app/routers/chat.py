# app/routers/chat.py
from uuid import uuid4
from fastapi import APIRouter
from schemas import UserQuery, ChatResponse
from services.memory import init_pinecone, store_conversation
from services.pubmed import (fetch_pubmed_articles, 
                             fetch_europe_pmc_articles,
                             fetch_new_drug_development_trials,)
from services.llm import summarize_info
from services.utils import (process_article_for_summary,
                            select_disease_informed_articles,)
from services.notification import send_slack_dm, create_gmail_draft
from config import NOTIFICATION_TYPE

router = APIRouter()
index = init_pinecone()  # initialize Pinecone index once

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(user_input: UserQuery):
    conversation_id = user_input.conversation_id or str(uuid4())
    user_query = user_input.query.strip()

    # --- fetching all the data needed from APIs. ---
    news_data_pubmed = fetch_pubmed_articles(user_input, max_results=200)
    news_data_EUpmc = fetch_europe_pmc_articles(user_input, max_results=200) # to be explored in the future if needed.
    new_drug_clinical_trials = fetch_new_drug_development_trials(user_input)
    
    # --- attatch all the parts of the abstracts from relevent articles---
    relevant_articles= select_disease_informed_articles(user_input,news_data_pubmed) #filter new articles for the specific disease
    llm_input=[]
    for r_a in relevant_articles:
        llm_input.append(process_article_for_summary(r_a))
    
    # use the top 10 headlines only (adjust as needed)
    news_titles = [article["title"] for article in relevant_articles[:10]]
    short_news_text = "\n".join(news_titles)

    # --- summarize the News with the LLM ---
    system_prompt = (
        "You are a helpful pharmaceutical assistant with in-depth knowledge of new drug development and clinical trials."
    )
    user_prompt = f"""
    Article Headlines: {short_news_text}

    Article Context and Detail: {llm_input}

    Clinical Trial News: {new_drug_clinical_trials[0]}

    Newly Trialed Drugs: {new_drug_clinical_trials[1]}

    Provide a concise summary with two sections:

    Section 1: Drug Development Summary
    - Summarize the overall news and insights regarding the drug development related to the specified disease.

    Section 2: New Drug Details
    - List the names of the newest drugs mentioned and briefly describe what each drug does.
    """

    llm_summary = summarize_info(system_prompt, user_prompt)
    final_response = f"{llm_summary}" # convert to string

    # write the output on a text file
    with open("example.txt", "w", encoding="utf-8") as file: 
        file.write(final_response)
        
    # --- store the conversation in vector databse with conversation ID so we knwo the user.---
    store_conversation(index, user_query, final_response, conversation_id)
    
    # --- choose which notification method to use ---
    notification_type = NOTIFICATION_TYPE.lower()
    if notification_type == "slack":
        send_slack_dm(final_response)
    elif notification_type == "gmail":
        create_gmail_draft(final_response)

    return ChatResponse(
        response=final_response,
        conversation_id=conversation_id
    ) # return the final response to the client.
