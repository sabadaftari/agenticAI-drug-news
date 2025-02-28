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

def select_disease_informed_articles(user_input: str, news_data_pubmed:list):

    relevant_articles = []
    for article_sections in news_data_pubmed:  # assuming each article is a list of sections
        # Join all '#text' values from the sections into one summary string.
        full_text = " ".join(
            section.get("#text", "") if isinstance(section, dict) else section
            for section in article_sections['abstract']
        ).lower()
        if user_input.query.lower() in full_text and user_input.query.lower() in article_sections['title']:
            relevant_articles.append(article_sections)
    return relevant_articles