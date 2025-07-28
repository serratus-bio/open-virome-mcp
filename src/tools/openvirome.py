import requests
from src.resources.psql import run_sql_query


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

    url = "https://zrdbegawce.execute-api.us-east-1.amazonaws.com/prod/" + route
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://mcp.openvirome.com/",
        "Origin": "https://mcp.openvirome.com",
    }
    response = requests.post(url, headers=headers, json=data, timeout=300)
    return response.json()


def get_similar_viruses():
    return [
        {
            "name": "Virus A",
            "similarity": 0.95,
        },
        {
            "name": "Virus B",
            "similarity": 0.90,
        },
    ]


def get_palm_ids_by_species(species: str) -> dict[str, object]:
    """
    Fetch palm_ids from the Serratus database based on a virus species name.
    Args:
        species: The species of the virus to search for.
    Returns:
        A dictionary containing the palm_ids and their associated tax_ids and percent_identity.
    """
    query = """
    SELECT palm_id, a.tax_id, percent_identity FROM
        (
            SELECT tax_id FROM public.tax_names
            WHERE tax_names.name_txt = %s
        ) as a
        LEFT JOIN
        (
            SELECT * FROM public.palm_gb
        ) as b
        on a.tax_id = b.tax_id
    WHERE percent_identity >= 90
    """
    rows = run_sql_query(query, params=(species,))
    if len(rows) <= 1:
        return {"data": []}

    return {"data": rows}
