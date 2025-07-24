import logging

from src.resources.psql import (
    get_serratus_connection,
    run_sql_query,
)
from src.resources.ncbi import get_pubmed_article


def register_resources(mcp):
    """Register all resources with the MCP server instance.

    Args:
        mcp: The FastMCP server instance
    """
    logging.info("Registering resources")

    def _handle_error(error_msg: str) -> dict[str, str]:
        logging.error(error_msg)
        return {"error": error_msg}

    @mcp.resource("db://serratus/palmdb/{palm_id}")
    def get_palm_id_data(palm_id: str) -> dict[str, object]:
        """Fetch data for a specific palm_id from the Serratus database."""
        query = "SELECT * FROM public.palmdb2 WHERE palm_id = %s"
        try:
            rows = run_sql_query(query, get_serratus_connection(), params=(palm_id,))
            if not rows:
                return _handle_error(f"Palm ID '{palm_id}' not found")
            return {"data": rows}
        except Exception as error:
            return _handle_error(f"Error fetching palm_id {palm_id}: {error}")

    @mcp.resource("db://ncbi/pubmed/{pmid}")
    def get_pubmed_data(pmid: str) -> dict[str, object]:
        """Fetch a PubMed article by ID and return the abstract."""
        try:
            abstract = get_pubmed_article(pmid)
            return {"pmid": pmid, "abstract": abstract}
        except Exception as error:
            return _handle_error(f"Error fetching PubMed article {pmid}: {error}")
