import os
import logging

import psycopg2
from psycopg2.extensions import connection


def get_serratus_connection() -> connection:
    """Returns a psycopg2 connection to the Serratus PostgreSQL database."""
    return psycopg2.connect(
        database=os.environ.get("PG_DATABASE_SERRATUS"),
        host=os.environ.get("PG_HOST_SERRATUS"),
        user=os.environ.get("PG_USER_SERRATUS"),
        password=os.environ.get("PG_PASSWORD_SERRATUS"),
        port="5432",
    )


def get_logan_connection() -> connection:
    """Returns a psycopg2 connection to the Logan PostgreSQL database."""
    return psycopg2.connect(
        database=os.environ.get("PG_DATABASE_LOGAN"),
        host=os.environ.get("PG_HOST_LOGAN"),
        user=os.environ.get("PG_USER_LOGAN"),
        password=os.environ.get("PG_PASSWORD_LOGAN"),
        port="5432",
    )


def run_sql_query(
    query: str,
    conn: connection | None = None,
    params: tuple | None = None,
) -> list[list[str]]:
    """
    Run a SQL query using psycopg2 and return the results as a list of rows.

    Args:
        query: A valid SQL SELECT query string with `%s` placeholders for parameters.
        conn: Optional psycopg2 connection. If None, uses Serratus DB connection.
        params: Optional tuple of parameters to safely inject into the query.

    Returns:
        A list of rows, where each row is a list of strings (including header as first row).
    """
    logging.info("Running SQL query")
    close_conn = False
    if conn is None:
        conn = get_serratus_connection()
        close_conn = True

    try:
        cursor = conn.cursor()
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        str_rows = [
            [str(col) if col is not None else "" for col in row] for row in rows
        ]
        return [colnames] + str_rows
    finally:
        if close_conn:
            conn.close()
