import logging
import base64
import json

import requests

from src.resources.psql import run_sql_query
from src.resources.neo4j import run_neo4j_query
from src.tools.workflows.state import MetadataFilter, SRAIdentifiers

### OpenVirome API interaction functions


def post_to_openvirome_api(route: str, data: dict) -> dict:
    """
    Post data to the OpenVirome API.
    Args:
        data: The data to post.
    Returns:
        The response from the API.
    """
    valid_routes = [
        "/identifiers",
        "/counts",
        "/results",
        "/mwas",
    ]
    if route not in valid_routes:
        raise ValueError(f"Invalid route: {route}. Valid routes are: {valid_routes}")

    url = "https://zrdbegawce.execute-api.us-east-1.amazonaws.com/prod" + route
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://mcp.openvirome.com/",
        "Origin": "https://mcp.openvirome.com",
    }
    logging.info("Posting to OpenVirome API at %s with data: %s", url, data)
    response = requests.post(url, headers=headers, json=data, timeout=300)
    response.raise_for_status()
    # check if the response is valid JSON, otherwise base64 decode it first
    try:
        return response.json()
    except ValueError:
        try:
            decoded_data = base64.b64decode(response.text)
            decoded_data = decoded_data.decode("utf-8")
            return json.loads(decoded_data)
        except Exception as e:
            logging.error("Failed to decode response: %s", e)
            raise ValueError("Response is not valid JSON and cannot be decoded") from e


def get_sra_identifiers_by_filters(
    filters: list[MetadataFilter],
    palmprint_only: bool = True,
) -> SRAIdentifiers:
    """
    Fetch SRA identifiers based on metadata filters.
    Args:
        filters: List of metadata filters to apply.
        palmprint_only: Whether to filter for runs that contain palmprint data.
    Returns:
        A dictionary containing SRA identifiers grouped by biosample, bioproject, and run.
    """
    if not filters:
        return {}

    data = {
        "filters": filters,
        "palmprintOnly": palmprint_only,
    }
    response = post_to_openvirome_api("/identifiers", data)
    return response


def get_counts_by_identifiers(
    table: str,
    group_by: str,
    id_column: str,
    ids: list[str],
    palmprint_only: bool = True,
    sort_by_column: str | None = None,
    sort_by_direction: str | None = None,
    page_start: int | None = None,
    page_end: int | None = None,
) -> dict[str, object]:
    """
        Fetch metadata counts from the OpenVirome API based on SRA ids.
    Args:
        table: The metadata table to query.
        group_by: The column to group counts by.
        id_column: The SRA identifier column that joints to the metadata table.
        ids: List of SRA identifiers to search for.
        palmprint_only: Whether to filter for runs that contain palmprint data.
        sort_by_column: Column to sort the results by.
        sort_by_direction: Direction to sort the results (asc or desc).
        page_start: Start index for pagination.
        page_end: End index for pagination.
    Returns:
        A dictionary containing metadata counts.
    """
    if not ids:
        return {}

    data = {
        "table": table,
        "groupBy": group_by,
        "idColumn": id_column,
        "ids": ids,
        "sortByColumn": sort_by_column,
        "sortByDirection": sort_by_direction,
        "palmprintOnly": palmprint_only,
        "pageStart": page_start,
        "pageEnd": page_end,
    }
    response = post_to_openvirome_api("/counts", data)
    return response


def get_results_by_identifiers(
    table: str,
    id_column: str,
    ids: list[str],
    palmprint_only: bool = True,
    sort_by_column: str | None = None,
    sort_by_direction: str | None = None,
    page_start: int | None = None,
    page_end: int | None = None,
) -> dict[str, object]:
    """
    Fetch results from the OpenVirome API based on SRA accessions.
    Args:
        table: The results table to query.
        id_column: The SRA identifier column that joints to the results table.
        ids: List of SRA identifiers to search for.
        palmprint_only: Whether to filter for runs that contain palmprint data.
        sort_by_column: Column to sort the results by.
        sort_by_direction: Direction to sort the results (asc or desc).
        page_start: Start index for pagination.
        page_end: End index for pagination.
    Returns:
        A dictionary containing results.
    """
    if not ids:
        return {}
    data = {
        "table": table,
        "idColumn": id_column,
        "ids": ids,
        "palmprintOnly": palmprint_only,
        "sortByColumn": sort_by_column,
        "sortByDirection": sort_by_direction,
        "pageStart": page_start,
        "pageEnd": page_end,
    }
    response = post_to_openvirome_api("/results", data)
    return response


def get_mwas_results_by_identifiers(
    id_column: str,
    ids: list[str],
    virus_families: list[str] | None = None,
    page_start: int | None = None,
    page_end: int | None = None,
) -> dict[str, object]:
    """
    Fetch MWAS results from the OpenVirome API based on SRA accessions.
    Args:
        id_column: The SRA identifier column that joints to the MWAS results table.
        ids: List of SRA identifiers to search for.
        virus_families: Optional list of virus families to filter results by.
        page_start: Start index for pagination.
        page_end: End index for pagination.
    Returns:
        A dictionary containing MWAS results.
    """
    if not ids:
        return {}
    data = {
        "idColumn": id_column,
        "ids": ids,
        "virusFamilies": virus_families,
        "pageStart": page_start,
        "pageEnd": page_end,
    }
    response = post_to_openvirome_api("/mwas", data)
    return response


### Serratus database interaction functions


def get_palm_ids_by_species(
    species: str, percent_identity: float = 90
) -> dict[str, object]:
    """
    Fetch palm_ids from the Serratus database based on a virus species name.
    Args:
        species: The species of the virus to search for.
    Returns:
        A dictionary containing the palm_ids and their associated tax_ids and percent_identity.
    """
    query = """
    SELECT palm_id, tax_species, gb_pid FROM
    palm_virome
    WHERE
        node_qc = 'true'
        AND tax_species LIKE %s
        AND gb_pid >= %s
    """
    species = f"%{species}%"
    rows = run_sql_query(query, params=(species, percent_identity))
    if len(rows) <= 1:
        return {"data": []}

    return {"data": rows}


# Can delete if unused, neo4j version is much faster
def get_similar_palm_ids_sql(
    palm_ids: list[str], percent_identity: float = 90
) -> dict[str, object]:
    """
    Fetch similar viruses based on palm_ids and percent_identity.
    Args:
        palm_ids: List of palm_ids to search for.
        percent_identity: Minimum percent identity for similarity.
    Returns:
        A dictionary containing similar viruses.
    """
    if not palm_ids:
        return {"data": []}
    query = """
    SELECT palm_id1, palm_id2, pident FROM public.palm_graph
    WHERE pident >= %s AND palm_id1 IN %s
    """
    rows = run_sql_query(
        query,
        params=(tuple(palm_ids), percent_identity),
    )
    if not rows:
        return {"data": []}
    return {"data": rows}


### Neo4j graph database interaction functions


def get_similar_palm_ids_neo4j(
    palm_ids: list[str], percent_identity: float = 90
) -> dict[str, object]:
    """
    Fetch similar viruses based on palm_ids and percent_identity using a graph query.
    Args:
        palm_ids: List of palm_ids to search for.
        percent_identity: Minimum percent identity for similarity.
    Returns:
        A dictionary containing similar viruses.
    """
    if not palm_ids:
        return {"data": []}
    percent_identity_normalized = percent_identity / 100.0
    columns = ["palm_id1", "palm_id2", "pident"]
    query = """
    MATCH (n:Palmprint)-[r:SEQUENCE_ALIGNMENT]-(m:Palmprint)
    WHERE r.percentIdentity >= $percent_identity AND n.palmId IN $palm_ids
    RETURN n.palmId AS palm_id1, m.palmId AS palm_id2, r.percentIdentity AS pident
    """
    params = {
        "palm_ids": palm_ids,
        "percent_identity": percent_identity_normalized,
    }

    rows = run_neo4j_query(query, params=params)
    if not rows:
        return {"data": []}

    # Modify data so it's consistent with the equivalent SQL query
    # Convert pident to int between 0 and 100
    clean_rows = [list(row.values()) for row in rows]
    for row in clean_rows:
        row[2] = int(row[2] * 100)
    # Prepend column names to the rows list
    clean_rows.insert(0, columns)

    return {"data": clean_rows}
