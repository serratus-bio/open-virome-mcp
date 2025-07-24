import logging
from src.prompts.summarize import (
    prompt_template_str,
    prompt_template_list,
)


def register_prompts(mcp):
    """Register all prompts with the MCP server instance.

    Args:
        mcp: The FastMCP server instance
    """
    logging.info("Registering prompts")

    @mcp.prompt(
        title="prompt_template_str", description="Example string template prompt"
    )
    def prompt_template_str_handler(message: str) -> str:
        """Handle the prompt for string template."""
        return prompt_template_str(message)

    @mcp.prompt(
        title="prompt_template_list", description="Example chat template prompt"
    )
    def prompt_template_list_handler(message: str) -> list:
        """Handle the prompt for chat template."""
        return prompt_template_list(message)
