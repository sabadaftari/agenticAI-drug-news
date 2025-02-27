from services.llm import summarize_info
from services.pubmed import (fetch_pubmed_articles, 
                             fetch_europe_pmc_articles,
                             fetch_new_drug_development_trials)

def process_article_for_summary(article):
    # retrieve the title (if present)
    title = article.get("title", "")
    
    # retrieve the abstract sections (ensure it's a list)
    abstract_sections = article.get("abstract", [])
    
    # format each section with its label and text
    formatted_sections = []
    for section in abstract_sections:
        if isinstance(section, dict):
            label = section.get('@Label', 'SECTION')
            text = section.get('#text', '')
            formatted_sections.append(f"{label}: {text}")
        else:
            # if a section isn't a dict, include it as-is
            formatted_sections.append(str(section))
    
    # combine title and abstract sections into one string
    combined_text = f"Title: {title}\n\nAbstract:\n" + "\n\n".join(formatted_sections)
    return combined_text

def select_disease_informed_articles(user_input: str):

    relevant_articles = []
    for article_sections in news_data_pubmed:  # assuming each article is a list of sections
        # Join all '#text' values from the sections into one summary string.
        full_text = " ".join(
            section.get("#text", "") if isinstance(section, dict) else section
            for section in article_sections['abstract']
        ).lower()
        if user_input.lower() in full_text and user_input.lower() in article_sections['title']:
            relevant_articles.append(article_sections)
    return relevant_articles
    
if __name__ == "__main__":
    user_input = "cardiovascular"

    # --- fetching all the data needed from APIs. ---
    news_data_pubmed = fetch_pubmed_articles(user_input, max_results=200)
    news_data_EUpmc = fetch_europe_pmc_articles(user_input, max_results=200) # to be explored in the future if needed.
    new_drug_clinical_trials = fetch_new_drug_development_trials(user_input)
    
    # --- attatch all the parts of the abstracts from relevent articles---
    relevant_articles= select_disease_informed_articles(user_input) #filter new articles for the specific disease
    llm_input=[]
    for r_a in relevant_articles:
        llm_input.append(process_article_for_summary(r_a))
    
    # use the top 10 headlines only (adjust as needed)
    news_titles = [article["title"] for article in relevant_articles[:10]]
    short_news_text = "\n".join(news_titles)

    # --- summarize the News with the LLM ---
    system_prompt = "You are a helpful pharmaseudical assistant with knowledge of the new drugs development research regarding diseases."
    user_prompt = f"""
                        Article Headlines: {short_news_text}

                        Article Context and Detail: {llm_input} 

                        Clinical Trial News: {new_drug_clinical_trials[0]}

                        Newly Trialed Drugs: {new_drug_clinical_trials[1]}

                        Provide a concise summary of the news and any insights on the drug development regarding a specific given disease.
                        """
    llm_summary = summarize_info(system_prompt, user_prompt)

