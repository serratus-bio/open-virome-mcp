# OpenVirome MCP server

## Getting Started

### Install uv

It's recommended to use `uv` for package management and virtual env. It is required by the MCP python sdk to host the MCP inspection server which is useful for debugging.

See docs for installation: https://docs.astral.sh/uv/#installation

### Set up virtual environment

```bash
uv venv
source .venv/bin/activate
```

### Install dependencies

```bash
uv sync
```

### Set up environment variables

Copy the example environment variables and fill in

```bash
cp .env.example .env
```

### Run MCP inspector in browser

`uv run mcp dev main.py`

In left panel, enter command and argument values if not already pre-filled, then click 'Connect':

```md
> Transport type: STDI
> Command: uv
> Arguments: run --with mcp mcp run main.py
```

### Run server locally

`uv run main.py`

### Run MCP client integration

```json
{
  "mcpServers": {
    "open-virome-mcp": {
      "command": "python",
      "args": ["main.py"]
    }
  }
}
```

## Notes

### MCP reminders

- **Resources** are how you expose data to LLMs. They're similar to GET endpoints in a REST API - they provide data but shouldn't perform significant computation or have side effects.
- **Tools** let LLMs take actions through your server. Unlike resources, tools are expected to perform computation and have side effects. Tools will return structured results by default, if their return type annotation is compatible.
- **Prompts** are reusable templates that help LLMs interact with your server effectively:

### Referenced repos:

- https://github.com/modelcontextprotocol/python-sdk

### Formatting and linting

These can be added as github actions later

Format: `black .`

Lint: `pylint src`
