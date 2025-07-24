import os
from neo4j import GraphDatabase, Driver, Session, Record
from typing import Any


class Neo4jConnection:
    def __init__(self, uri: str | None, user: str | None, pwd: str | None) -> None:
        self._uri: str | None = uri
        self._user: str | None = user
        self._pwd: str | None = pwd
        self._driver: Driver | None = None
        try:
            self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._pwd))  # type: ignore
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self._driver is not None:
            self._driver.close()

    def query(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        database: str | None = None,
    ) -> list[Record] | None:
        """
        Execute a Cypher query.

        Args:
            query: The Cypher query string.
            parameters: Optional dictionary of parameters to pass.
            database: Optional database name to run the query against.

        Returns:
            A list of neo4j.Record objects or None on failure.
        """
        assert self._driver is not None, "Driver not initialized!"
        session: Session | None = None
        response: list[Record] | None = None
        try:
            session = (
                self._driver.session(database=database)
                if database is not None
                else self._driver.session()
            )
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


def get_connection() -> Neo4jConnection:
    """
    Create a new Neo4jConnection instance using environment variables.

    Required environment variables:
        - NEO4J_URI
        - NEO4J_USER
        - NEO4J_PASSWORD

    Returns:
        An instance of Neo4jConnection.
    """
    return Neo4jConnection(
        uri=os.environ.get("NEO4J_URI"),
        user=os.environ.get("NEO4J_USER"),
        pwd=os.environ.get("NEO4J_PASSWORD"),
    )
