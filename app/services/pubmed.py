import xmltodict
import requests
from datetime import datetime, timedelta
from typing import List
from pytrials.client import ClinicalTrials
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def fetch_pubmed_articles(query: str, 
                          max_results:int =10, 
                          past_num_days:int=30) -> List[dict]:
    try:
        # query includes the date filter
        search_query = f"{query.query} AND (\"last {past_num_days} days\"[dp])"

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
        if not articles:
            logger.warning("No PubMed articles found in the past %d days.", past_num_days)
        return articles
    except requests.exceptions.Timeout as te:
        logger.error("Timeout occurred while fetching PubMed articles: %s", te, exc_info=True)
        return []
    except Exception as e:
        logger.error("Error fetching PubMed articles: %s", e, exc_info=True)
        return []

def fetch_europe_pmc_articles(query:str, 
                              max_results:int=10, 
                              past_num_days:int=30) -> List[dict]:
    try:
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

        if not articles:
            logger.warning("No Europe PMC articles found in the past %d days.", past_num_days)
        return articles
    except requests.exceptions.Timeout as te:
        logger.error("Timeout occurred while fetching Europe PMC articles: %s", te, exc_info=True)
        return []
    except Exception as e:
        logger.error("Error fetching Europe PMC articles: %s", e, exc_info=True)
        return []

def fetch_new_drug_development_trials(condition, days=730, max_results=10):
    try:
        ct = ClinicalTrials()

        # Get 50 full studies related to the condition input.
        ct.get_full_studies(search_expr=condition, max_studies=max_results) 

        # Get the NCTId, Condition ,Study Title, Interventions and First Posted fields from 1000 studies related to the disease, in csv format.
        rows = ct.get_study_fields(
            search_expr=condition,
            fields=["NCT Number", "Conditions", "Study Title", "Interventions", "First Posted"],
            max_studies=max_results,
            fmt="csv",
        ) # to explore more fields options check out pytrial/fields.csv

        fields = [
            row for row in rows 
            if len(row) > 3 and row[3] and "DRUG:" in row[3].upper()
        ] # keep only rows with a DRUG interventions assuming "Interventions" is in index 3
        
        drugs_with_date = process_fields(fields,days) # create a list of dictionaries with the drug name and LastUpdatePostDate.
        return fields, drugs_with_date
    except Exception as e:
        logger.error("Error fetching new drug development trials: %s", e, exc_info=True)
        return ([], [])

def process_fields(fields: str,days:int =730):
    try:
        # Calculate the date 30 days ago and today's date in YYYY-MM-DD format.
        today = datetime.today()
        start_date = today - timedelta(days=days)

        
        drugs_with_date = []
        for row in fields:
            
            drug_name = row[3].split("DRUG:")[-1].strip() # extract the drug name. 

            # get the First Posted from the row if available assumed to be at index 4
            last_update = row[4] if len(row) > 4 else None

            if len(row) > 4 and row[4]: # check if row[4] even exists
                date_str = row[4]
                try:

                    date_obj = datetime.strptime(date_str, "%Y-%m-%d") # change the string to date format
                    if start_date <= date_obj <= today:
                        drugs_with_date.append({
                                "drug_name": drug_name,
                                "First Posted": last_update
                            })
                except Exception as e:
                    print(f"Error parsing date '{date_str}': {e}")

        return drugs_with_date
    except Exception as e:
        logger.error("Error processing fields: %s", e, exc_info=True)
        return []
