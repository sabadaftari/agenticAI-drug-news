import xmltodict
import requests
from datetime import datetime, timedelta
from typing import List
def fetch_pubmed_articles(query: str, 
                          max_results:int =10, 
                          past_num_days:int=30) -> List[dict]:

    # query includes the date filter
    search_query = f"{query} AND (\"last {past_num_days} days\"[dp])"

    endpoint = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": search_query,  
        "retmode": "xml",
        "retmax": max_results,
    }

    response = requests.get(endpoint, params=params)
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
    # if nothing was found
    if not articles:
        print(f"We have found no articles pulished on PubMed during the past {past_num_days}.")

    return articles

def fetch_europe_pmc_articles(query:str, 
                              max_results:int=10, 
                              past_num_days:int=30) -> List[dict]:
    
    # calculate the date range
    end_date = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=past_num_days)).strftime("%Y-%m-%d")

    endpoint = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    # query includes the time filter
    search_query = f"{query} AND FIRST_PDATE:[{start_date} TO {end_date}]"
    
    params = {
        "query": search_query,  # Ensures results are from BioRxiv
        "format": "json",
        "pageSize": max_results
    }

    response = requests.get(endpoint, params=params)
    
    # in case we get API error
    if response.status_code != 200:
        print(f"Error: Failed to fetch data. Status Code: {response.status_code}")
        return []

    data = response.json()

    articles = []
    for item in data.get("resultList", {}).get("result", []):
        articles.append({
            "title": item.get("title", "No title available"),
            "authors": item.get("authorString", "No authors available"),
            "abstract": item.get("abstractText", "No abstract available"),
            "doi": item.get("doi", "No DOI available"),
            "url": f"https://europepmc.org/article/{item.get('source', '')}/{item.get('id', '')}"
        })

    # if nothing was found
    if not articles:
        print(f"We have found no articles pulished on Europe PMC during the past {past_num_days}.")

    return articles

def fetch_new_drug_development_trials(condition, days=30, max_results=10):
    
    # Set up the API endpoint and parameters
    endpoint = "https://clinicaltrials.gov/api/query/study_fields"
    # Calculate the start date (studies updated after this date)
    start_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    fields = "NCTId,BriefTitle,OverallStatus,LastUpdatePostDate,InterventionName,InterventionType"
    
    params = {
        "expr": condition,
        "fields": fields,
        "min_rnk": 1,
        "max_rnk": max_results,
        "fmt": "json"
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return [], None
    
    data = response.json()
    studies = data.get("studies", [])
    next_page_token = data.get("nextPageToken")
    
    results = []
    for study in studies:
        identification = study.get("protocolSection", {}).get("identificationModule", {})
        status = study.get("protocolSection", {}).get("statusModule", {})
        nct_id = identification.get("nctId", "N/A")
        title = identification.get("briefTitle", "N/A")
        overall_status = status.get("overallStatus", "N/A")
        
        results.append({
            "nctId": nct_id,
            "title": title,
            "overallStatus": overall_status
        })
    
    return results, next_page_token

# fetch_new_drug_development_trials("cardiovascular disease")





