from mcp.server.fastmcp.prompts import base


def prompt_template_str(message: str) -> str:
    return f"Example string template:\n\n{message}"


def prompt_template_list(message: str) -> list[base.Message]:
    return [
        base.AssistantMessage("Example chat template"),
        base.UserMessage(message),
    ]
