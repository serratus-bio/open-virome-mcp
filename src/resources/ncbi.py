import os

from Bio import Entrez


Entrez.email = os.environ.get("ENTREZ_EMAIL")


def get_pubmed_article(pmid: str) -> str:
    """Fetch a PubMed article by ID and return the abstract as plain text."""
    with Entrez.efetch(
        db="pubmed", id=pmid, rettype="abstract", retmode="text"
    ) as handle:
        return handle.read()
