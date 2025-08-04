import logging
from src.tools.workflows.virus_metadata_analysis import (
    graph as virus_metadata_analysis_graph,
)


def register_workflows(mcp):
    """Register all workflow tools with the MCP server instance.

    Args:
        mcp: The FastMCP server instance
    """
    logging.info("Registering workflow tools")

    @mcp.tool("get_virus_metadata_analysis")
    async def virus_metadata_analysis_tool(
        virus_species: str = "Papaya meleira virus",
        hypothesis: str = "This virus may be a cofactor of cancer in humans.",
    ):
        """Run metadata analysis based on input virus and hypothesis."""
        logging.info("Starting metadata anomaly workflow")
        try:
            inputs = {
                "user_input": {
                    "species_label": virus_species,
                    "hypothesis": hypothesis,
                },
            }
            output = await virus_metadata_analysis_graph.ainvoke(inputs)
            return output

        except Exception as error:
            logging.error("Error in metadata anomaly workflow: %s", error)
            return {"error": str(error)}
