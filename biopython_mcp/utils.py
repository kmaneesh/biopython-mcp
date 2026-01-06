"""Common utility functions for BioPython MCP server."""

import os
import re
import time
from contextlib import contextmanager
from typing import Any, Generator


def validate_sequence(sequence: str) -> str:
    """
    Validate and clean a biological sequence.

    Args:
        sequence: Biological sequence string (DNA, RNA, or protein)

    Returns:
        Cleaned sequence string

    Raises:
        ValueError: If sequence is empty or contains invalid characters
    """
    if not sequence:
        raise ValueError("Sequence cannot be empty")

    sequence = sequence.strip().upper()

    valid_chars = set("ACGTUNRYWSMKBDHV-")
    if not all(c in valid_chars for c in sequence):
        protein_chars = set("ACDEFGHIKLMNPQRSTVWY*-")
        if not all(c in protein_chars for c in sequence):
            raise ValueError(
                f"Sequence contains invalid characters. "
                f"Valid DNA/RNA: {valid_chars}, Valid protein: {protein_chars}"
            )

    return sequence


def format_sequence_output(sequence: str, line_length: int = 60) -> str:
    """
    Format a sequence into lines of specified length.

    Args:
        sequence: Biological sequence string
        line_length: Number of characters per line (default: 60)

    Returns:
        Formatted sequence string with line breaks
    """
    lines = []
    for i in range(0, len(sequence), line_length):
        lines.append(sequence[i : i + line_length])
    return "\n".join(lines)


def parse_fasta(fasta_string: str) -> list[dict[str, str]]:
    """
    Parse a FASTA format string into a list of sequence records.

    Args:
        fasta_string: FASTA formatted string

    Returns:
        List of dictionaries containing 'id', 'description', and 'sequence'
    """
    records: list[dict[str, str]] = []
    current_id: str | None = None
    current_description: str | None = None
    current_sequence: list[str] = []

    for line in fasta_string.split("\n"):
        line = line.strip()
        if not line:
            continue

        if line.startswith(">"):
            if current_id is not None:
                records.append(
                    {
                        "id": current_id,
                        "description": current_description or "",
                        "sequence": "".join(current_sequence),
                    }
                )

            header = line[1:].split(None, 1)
            current_id = header[0]
            current_description = header[1] if len(header) > 1 else ""
            current_sequence = []
        else:
            current_sequence.append(line)

    if current_id is not None:
        records.append(
            {
                "id": current_id,
                "description": current_description or "",
                "sequence": "".join(current_sequence),
            }
        )

    return records


def format_fasta(records: list[dict[str, str]], line_length: int = 60) -> str:
    """
    Format sequence records into FASTA format.

    Args:
        records: List of dictionaries with 'id', 'description', and 'sequence'
        line_length: Number of characters per line (default: 60)

    Returns:
        FASTA formatted string
    """
    fasta_lines = []

    for record in records:
        header = f">{record['id']}"
        if record.get("description"):
            header += f" {record['description']}"
        fasta_lines.append(header)

        sequence = record["sequence"]
        for i in range(0, len(sequence), line_length):
            fasta_lines.append(sequence[i : i + line_length])

    return "\n".join(fasta_lines)


def calculate_molecular_weight(sequence: str, seq_type: str = "protein") -> float:
    """
    Calculate the molecular weight of a sequence.

    Args:
        sequence: Biological sequence string
        seq_type: Type of sequence - 'protein' or 'dna' or 'rna' (default: 'protein')

    Returns:
        Molecular weight in Daltons
    """
    protein_weights = {
        "A": 89.1,
        "C": 121.2,
        "D": 133.1,
        "E": 147.1,
        "F": 165.2,
        "G": 75.1,
        "H": 155.2,
        "I": 131.2,
        "K": 146.2,
        "L": 131.2,
        "M": 149.2,
        "N": 132.1,
        "P": 115.1,
        "Q": 146.2,
        "R": 174.2,
        "S": 105.1,
        "T": 119.1,
        "V": 117.1,
        "W": 204.2,
        "Y": 181.2,
    }

    dna_weights = {"A": 331.2, "T": 322.2, "G": 347.2, "C": 307.2}

    rna_weights = {"A": 347.2, "U": 324.2, "G": 363.2, "C": 323.2}

    sequence = sequence.upper()
    weight = 0.0

    if seq_type == "protein":
        weights = protein_weights
    elif seq_type == "dna":
        weights = dna_weights
    elif seq_type == "rna":
        weights = rna_weights
    else:
        raise ValueError(f"Invalid seq_type: {seq_type}")

    for char in sequence:
        weight += weights.get(char, 0.0)

    return round(weight, 2)


# Entrez utilities
class EntrezRateLimiter:
    """Rate limiter for NCBI Entrez API calls.

    Enforces NCBI rate limits:
    - 3 requests/second without API key
    - 10 requests/second with API key
    """

    def __init__(self) -> None:
        """Initialize rate limiter with API key detection."""
        self.has_api_key = bool(os.environ.get("NCBI_API_KEY"))
        self.delay = 0.1 if self.has_api_key else 0.34  # 10/sec or ~3/sec
        self.last_call: float = 0.0

    def wait(self) -> None:
        """Wait if necessary to respect rate limits."""
        elapsed = time.time() - self.last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_call = time.time()


# Global singleton instance
_rate_limiter = EntrezRateLimiter()


@contextmanager
def entrez_rate_limit() -> Generator[EntrezRateLimiter, None, None]:
    """Context manager for rate-limited Entrez calls.

    Automatically enforces NCBI rate limits based on API key availability.

    Example:
        with entrez_rate_limit():
            handle = Entrez.esearch(...)
    """
    _rate_limiter.wait()
    yield _rate_limiter


def parse_ids(ids: str | list[str]) -> list[str]:
    """Parse and normalize ID inputs to consistent format.

    Args:
        ids: Single ID, comma/semicolon/whitespace-separated string, or list of IDs

    Returns:
        List of cleaned ID strings

    Examples:
        >>> parse_ids("123456")
        ['123456']
        >>> parse_ids("123456,789012")
        ['123456', '789012']
        >>> parse_ids(["123456", "789012"])
        ['123456', '789012']
        >>> parse_ids("123, 456; 789")
        ['123', '456', '789']
    """
    if isinstance(ids, str):
        # Split on commas, semicolons, and whitespace
        id_list = re.split(r'[,;\s]+', ids)
    else:
        id_list = ids

    # Clean and filter
    return [id_str.strip() for id_str in id_list if id_str.strip()]


def format_entrez_error(exception: Exception, context: dict[str, Any]) -> dict[str, Any]:
    """Format Entrez API errors with helpful context.

    Args:
        exception: The exception that occurred
        context: Dictionary of context (database, query, ids, etc.)

    Returns:
        Formatted error dictionary with success=False

    Examples:
        >>> try:
        ...     # Entrez call
        ... except Exception as e:
        ...     return format_entrez_error(e, {"database": "pubmed", "query": "test"})
    """
    error_msg = str(exception)

    # Detect specific error types
    rate_limit_exceeded = "429" in error_msg or "rate limit" in error_msg.lower()
    invalid_id = "invalid" in error_msg.lower() or "not found" in error_msg.lower()

    return {
        "success": False,
        "error": error_msg,
        "error_type": (
            "rate_limit" if rate_limit_exceeded else "invalid_id" if invalid_id else "unknown"
        ),
        "rate_limit_exceeded": rate_limit_exceeded,
        **context,
    }
