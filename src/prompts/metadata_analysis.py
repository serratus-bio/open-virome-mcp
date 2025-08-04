from src.tools.workflows.state import MetadataCounts, MWASResult


def validate_hypothesis_system_prompt() -> str:
    """
    Generate a system prompt for validating a hypothesis based on metadata counts and MWAS results.
    Returns:
        A string prompt for hypothesis validation.
    """
    return (
        "You are an expert bioinformatics research assistant being used to analyze a"
        " hypothesis based on associated metadata from the Sequence Read"
        " Archive.\n\nValidate the following hypothesis based on metadata counts and"
        " statistical significance test results:\n\n"
    )


def validate_hypothesis_user_prompt(
    hypothesis: str,
    metadata_counts: MetadataCounts,
    mwas_results: list[MWASResult],
) -> str:
    """
    Generate a prompt to validate a hypothesis based on metadata counts and MWAS results.
    Args:
        hypothesis: The user hypothesis to validate.
        metadata_counts: Metadata counts to analyze.
        mwas_results: MWAS results to analyze.
    Returns:
        A string prompt for hypothesis validation.
    """
    prompt = (
        f"Hypothesis: {hypothesis}\n\nMetadata Counts: {metadata_counts}\n\nMWAS"
        f" Results: {mwas_results}\n\nDetermine if the hypothesis is supported by the"
        " data, and provide a structured report detailing the validation in the"
        " following format:\nValidation Report:\n- Rating: [0-100]\n- Supporting"
        " Metadata Counts: [list of 0-5 metadata counts]\n- Supporting MWAS Results:"
        " [list of 0-5 MWAS results]\n- Reasoning: [explanation of the validation]If"
        " the hypothesis is not supported, provide reasoning for why it is not"
        " supported and suggest alternative hypotheses or areas for further"
        " investigation.Leave fields blank if not applicable."
    )
    return prompt


def anomaly_detection_system_prompt() -> str:
    """
    Generate a system prompt for detecting anomalies in metadata counts and MWAS results.
    Returns:
        A string prompt for anomaly detection.
    """
    return (
        "You are an expert bioinformatics research assistant being used to analyze a"
        " hypothesis based on associated metadata from the Sequence Read"
        " Archive.\n\nDetect anomalies in the following metadata counts and statistical"
        " significance test results:\n\n"
    )


def anomaly_detection_user_prompt(
    hypothesis: str,
    metadata_counts: MetadataCounts,
    mwas_results: list[MWASResult],
) -> str:
    """
    Generate a prompt to find anomalies in metadata counts and MWAS results.
    Args:
        hypothesis: The user hypothesis to analyze for anomalies.
        metadata_counts: Metadata counts to analyze for anomalies.
        mwas_results: MWAS results to analyze for anomalies.
    Returns:
        A string prompt for anomaly detection.
    """
    prompt = (
        f"Hypothesis: {hypothesis}\n\nMetadata Counts: {metadata_counts}\n\nMWAS"
        f" Results: {mwas_results}\n\nIdentify any anomalies or unexpected patterns in"
        " the data.Output should be a structured report detailing the anomalies found"
        " in the following format:\nAnomaly Report:\n- Rating: [0-100]\n- Supporting"
        " Metadata Counts: [list of 0-5 metadata counts]\n- Supporting MWAS Results:"
        " [list of 0-5 MWAS results]\n- Reasoning: [explanation of the anomalies"
        " found]If no anomalies are found, provide a report indicating that no"
        " anomalies were identified.Leave fields blank if not applicable."
    )
    return prompt
