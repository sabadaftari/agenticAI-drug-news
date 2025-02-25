import xmltodict
import requests
from typing import Any

def fetch_pubmed_articles(query: Any, max_results=10):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,  
        "retmode": "xml",
        "retmax": max_results,
    }

    response = requests.get(base_url, params=params)
    data = xmltodict.parse(response.content)
    
    article_ids = data["eSearchResult"].get("IdList", {}).get("Id", [])
    
    articles = []
    if article_ids:
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(article_ids),
            "retmode": "xml",
        }

        fetch_response = requests.get(fetch_url, params=fetch_params)
        fetch_data = xmltodict.parse(fetch_response.content)

        # parse article information
        for article in fetch_data["PubmedArticleSet"]["PubmedArticle"]:
            title = article["MedlineCitation"]["Article"]["ArticleTitle"]
            abstract = article["MedlineCitation"]["Article"].get("Abstract", {}).get("AbstractText", "No abstract available")
            journal = article["MedlineCitation"]["Article"]["Journal"]["Title"]
            pubmed_id = article["MedlineCitation"]["PMID"]["#text"]
            article_url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"

            articles.append({
                "title": title,
                "abstract": abstract,
                "journal": journal,
                "url": article_url
            })
    return articles

fetch_pubmed_articles("coronary artery disease AND drug")

