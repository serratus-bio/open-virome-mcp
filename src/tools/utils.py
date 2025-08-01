import re
from typing import List


def extract_accessions(message: str) -> List[str]:
    """
    Extract SRX and ERX accessions from text using regex
    Args:
        message: Text message to extract accessions from
    Returns:
        List of unique SRX and ERX accessions
    """
    # Find all matches in the message
    accessions = re.findall(r"(?:SRX|ERX)[0-9]{4,}+", message)
    # Return unique accessions
    return list(set(accessions))
