import logging

from src.tools.workflows.register import register_workflows
from src.tools.openvirome import (
    get_similar_viruses,
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
