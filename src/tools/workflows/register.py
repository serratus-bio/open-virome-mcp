import logging
from src.tools.workflows.metadata_anomaly import (
    graph as metadata_anomaly_graph,
)


def register_workflows(mcp):
    """Register all workflow tools with the MCP server instance.

    Args:
        mcp: The FastMCP server instance
    """
    logging.info("Registering workflow tools")

    @mcp.tool("get_metadata_anomaly")
    async def metadata_anomaly_tool(input_data: str):
        """Fetch metadata anomalies based on input data."""
        logging.info("Starting metadata anomaly workflow")
        try:
            inputs = {"messages": [{"role": "human", "content": input_data}]}
            output = await metadata_anomaly_graph.ainvoke(inputs)
            return output

        except Exception as error:
            logging.error("Error in metadata anomaly workflow: %s", error)
            return {"error": str(error)}
