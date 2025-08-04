from typing_extensions import Any

from langchain_openai import AzureChatOpenAI


def get_openai_client(
    model_name: str = "gpt-4o", temperature: float = 0.0
) -> AzureChatOpenAI:
    """
    Create an OpenAI client for the specified model.

    Args:
        model_name (str): The name of the OpenAI model to use.
        temperature (float): The temperature for the model's response.

    Returns:
        AzureChatOpenAI: An instance of the OpenAI client.
    """

    existing_deployments = {
        "gpt-4o": "open-virome-llm",
        "o1-mini": "open-virome-llm-o1-mini",
        "gpt-4o-mini": "open-virome-llm-gpt-4o-mini",
    }
    if model_name not in existing_deployments:
        raise ValueError(
            f"{model_name} not registered. Existing deployments:"
            f" {existing_deployments.keys()}"
        )

    deployment_name = existing_deployments[model_name]

    return AzureChatOpenAI(
        azure_deployment=deployment_name,
        api_version="2024-09-01-preview",
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )


def run_llm_completion(
    messages: list[dict],
    model: AzureChatOpenAI | None = None,
    model_name: str = "gpt-4o",
    temperature: float = 0.0,
    structured_output: Any = None,
) -> str:
    """
    Run a completion using the specified OpenAI client.

    Args:
        client (AzureChatOpenAI): The OpenAI client instance.
        messages (list[dict]): The messages to send to the model.
        model_name (str): The name of the model to use.
        temperature (float): The temperature for the model's response.

    Returns:
        str: The response from the model.
    """
    if model is None:
        model = get_openai_client(model_name, temperature)
    if not messages or not isinstance(messages, list):
        raise ValueError("Messages must be a non-empty list of dictionaries.")
    if structured_output is not None:
        model = model.with_structured_output(structured_output)

    response = model.invoke(messages)

    if structured_output is not None:
        return response

    return response.content
