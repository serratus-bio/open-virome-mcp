import logging

from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP
from src.prompts.register import register_prompts
from src.tools.register import register_tools
from src.resources.register import register_resources


load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

mcp = FastMCP("OpenVirome MCP")

register_tools(mcp)
register_prompts(mcp)
register_resources(mcp)
