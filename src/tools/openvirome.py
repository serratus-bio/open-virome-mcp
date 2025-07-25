from src.resources.psql import run_sql_query


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


def get_palmids_by_species(species: str) -> dict[str, object]:
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
    return {"data": rows}
