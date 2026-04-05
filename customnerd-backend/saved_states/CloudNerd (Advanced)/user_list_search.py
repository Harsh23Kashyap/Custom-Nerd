import logging
import os

from Bio import Entrez
from Bio.Entrez import efetch

logger = logging.getLogger(__name__)


def fetch_articles_by_pmids(pmid_list):
    """
    Fetches articles from PubMed using a list of PMIDs.
    Requires ENTREZ_EMAIL (NCBI policy); only set that in deployments that use PMID fetch.
    """
    if not pmid_list:
        return []

    email = (os.getenv("ENTREZ_EMAIL") or "").strip().strip('"')
    if not email:
        logger.warning(
            "ENTREZ_EMAIL is not set; skipping PubMed efetch. "
            "Add ENTREZ_EMAIL to variables.env only if you use PMID / PubMed article fetch."
        )
        return []

    Entrez.email = email
    articles = []
    for pmid in pmid_list:
        try:
            handle = efetch(db="pubmed", id=pmid, rettype="xml")
            article_data = Entrez.read(handle)["PubmedArticle"]
            articles.extend(article_data)
        except Exception as e:
            print(f"Error fetching article with PMID {pmid}: {e}")
            continue
    return articles