"""Common utility functions for BioPython MCP server."""

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
    records = []
    current_id = None
    current_description = None
    current_sequence = []

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
