import logging

from src.tools.workflows.register import register_workflows
from src.tools.openvirome import (
    get_similar_viruses,
    get_palm_ids_by_species,
)


def register_tools(mcp):
    """Register all tools with the MCP server instance.

    Args:
        mcp: The FastMCP server instance
    """
    logging.info("Registering tools")

    register_workflows(mcp)

    def _handle_error(error_msg: str) -> dict[str, str]:
        logging.error(error_msg)
        return {"error": error_msg}

    @mcp.tool("get_similar_viruses")
    def similar_viruses_tool():
        """Fetch similar viruses based on some criteria."""
        try:
            return get_similar_viruses()
        except Exception as error:
            return _handle_error(f"Error fetching similar viruses: {error}")

    @mcp.tool("get_palm_ids_by_species")
    def palm_ids_from_species_tool(species_name: str):
        """Fetch palm_ids from a given virus name."""
        try:
            palm_ids = get_palm_ids_by_species(species_name)
            if not palm_ids:
                return _handle_error(
                    f"No palm_ids found for species name: {species_name}"
                )
            return palm_ids
        except Exception as error:
            return _handle_error(f"Error fetching palm_ids for {species_name}: {error}")
