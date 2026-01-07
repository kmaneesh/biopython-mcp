"""Common utility functions for BioPython MCP server."""

import os
import pathlib
import re
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any


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
    # Split on commas, semicolons, and whitespace if string, otherwise use list as-is
    id_list = re.split(r"[,;\s]+", ids) if isinstance(ids, str) else ids

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


# Caching utilities
def _get_cache_dir() -> pathlib.Path:
    """
    Get or create the cache directory.

    Returns:
        Path to cache directory (~/.biopython-mcp/cache/)
    """
    cache_dir = pathlib.Path.home() / ".biopython-mcp" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _get_cache_key(database: str, operation: str, params: dict[str, Any]) -> str:
    """
    Generate a cache key from database, operation, and parameters.

    Args:
        database: Database name
        operation: Operation name (e.g., 'search', 'fetch', 'summary')
        params: Parameters dictionary

    Returns:
        SHA256 hash as hexadecimal string
    """
    import hashlib
    import json

    # Create a consistent string representation
    cache_data = {
        "database": database,
        "operation": operation,
        "params": params,
    }
    cache_string = json.dumps(cache_data, sort_keys=True)
    return hashlib.sha256(cache_string.encode()).hexdigest()


def get_cached_result(
    database: str, operation: str, params: dict[str, Any], ttl: int = 3600
) -> dict[str, Any] | None:
    """
    Get cached result if it exists and is not expired.

    Args:
        database: Database name
        operation: Operation name
        params: Parameters used for the query
        ttl: Time to live in seconds (default: 3600 = 1 hour)

    Returns:
        Cached result dictionary or None if not found/expired
    """
    import json

    cache_dir = _get_cache_dir()
    cache_key = _get_cache_key(database, operation, params)
    cache_file = cache_dir / database / f"{cache_key}.json"

    if not cache_file.exists():
        return None

    # Check if cache is expired
    cache_age = time.time() - cache_file.stat().st_mtime
    if cache_age > ttl:
        # Cache expired, remove it
        cache_file.unlink()
        return None

    try:
        with open(cache_file) as f:
            return json.load(f)  # type: ignore[no-any-return]
    except Exception:
        return None


def set_cached_result(
    database: str, operation: str, params: dict[str, Any], data: dict[str, Any]
) -> None:
    """
    Store result in cache.

    Args:
        database: Database name
        operation: Operation name
        params: Parameters used for the query
        data: Result data to cache
    """
    import json

    cache_dir = _get_cache_dir()
    db_cache_dir = cache_dir / database
    db_cache_dir.mkdir(parents=True, exist_ok=True)

    cache_key = _get_cache_key(database, operation, params)
    cache_file = db_cache_dir / f"{cache_key}.json"

    try:
        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass  # Silently fail if caching doesn't work


def clear_cache(database: str = "") -> int:
    """
    Clear cache files for a database or all databases.

    Args:
        database: Database name to clear (empty string clears all)

    Returns:
        Number of cache files removed
    """

    cache_dir = _get_cache_dir()
    count = 0

    if database:
        # Clear specific database cache
        db_cache_dir = cache_dir / database
        if db_cache_dir.exists():
            for cache_file in db_cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
    else:
        # Clear all database caches
        for db_dir in cache_dir.iterdir():
            if db_dir.is_dir():
                for cache_file in db_dir.glob("*.json"):
                    cache_file.unlink()
                    count += 1

    return count
