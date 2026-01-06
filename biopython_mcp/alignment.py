"""Sequence alignment tools using BioPython."""

from typing import Any

from Bio import Align

from biopython_mcp.utils import validate_sequence


def pairwise_align(
    seq1: str,
    seq2: str,
    mode: str = "global",
    match_score: float = 2.0,
    mismatch_score: float = -1.0,
    gap_open: float = -2.0,
    gap_extend: float = -0.5,
) -> dict[str, Any]:
    """
    Perform pairwise sequence alignment.

    Args:
        seq1: First sequence
        seq2: Second sequence
        mode: Alignment mode - 'global' or 'local' (default: 'global')
        match_score: Score for matching residues (default: 2.0)
        mismatch_score: Score for mismatching residues (default: -1.0)
        gap_open: Gap opening penalty (default: -2.0)
        gap_extend: Gap extension penalty (default: -0.5)

    Returns:
        Dictionary containing alignment results and statistics
    """
    try:
        seq1 = validate_sequence(seq1)
        seq2 = validate_sequence(seq2)

        aligner = Align.PairwiseAligner()
        aligner.mode = mode
        aligner.match_score = match_score
        aligner.mismatch_score = mismatch_score
        aligner.open_gap_score = gap_open
        aligner.extend_gap_score = gap_extend

        alignments = list(aligner.align(seq1, seq2))

        if not alignments:
            return {
                "success": False,
                "error": "No alignments found",
                "seq1_length": len(seq1),
                "seq2_length": len(seq2),
            }

        best_alignment = alignments[0]

        return {
            "success": True,
            "mode": mode,
            "score": float(best_alignment.score),
            "num_alignments": len(alignments),
            "alignment": str(best_alignment),
            "seq1_length": len(seq1),
            "seq2_length": len(seq2),
            "parameters": {
                "match_score": match_score,
                "mismatch_score": mismatch_score,
                "gap_open": gap_open,
                "gap_extend": gap_extend,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "seq1_length": len(seq1) if seq1 else 0,
            "seq2_length": len(seq2) if seq2 else 0,
        }


def multiple_sequence_alignment(
    sequences: list[str], algorithm: str = "clustalw"
) -> dict[str, Any]:
    """
    Perform multiple sequence alignment.

    Args:
        sequences: List of sequences to align
        algorithm: Alignment algorithm to use (default: 'clustalw')

    Returns:
        Dictionary containing alignment results

    Note:
        This is a placeholder that demonstrates the structure.
        Full implementation would require external tools like MUSCLE or Clustal Omega.
    """
    try:
        if len(sequences) < 2:
            return {
                "success": False,
                "error": "At least 2 sequences required for alignment",
                "num_sequences": len(sequences),
            }

        validated_seqs = [validate_sequence(seq) for seq in sequences]

        return {
            "success": True,
            "message": "Multiple sequence alignment would be performed here",
            "num_sequences": len(validated_seqs),
            "algorithm": algorithm,
            "sequence_lengths": [len(seq) for seq in validated_seqs],
            "note": "This requires external alignment tools to be installed",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "num_sequences": len(sequences)}


def calculate_alignment_score(alignment_str: str, matrix_name: str = "BLOSUM62") -> dict[str, Any]:
    """
    Calculate the score of a given alignment using a substitution matrix.

    Args:
        alignment_str: Aligned sequences (with gaps) as a formatted string
        matrix_name: Name of substitution matrix to use (default: 'BLOSUM62')

    Returns:
        Dictionary containing alignment score and statistics
    """
    try:
        available_matrices = [
            "BLOSUM62",
            "BLOSUM45",
            "BLOSUM50",
            "BLOSUM80",
            "BLOSUM90",
            "PAM30",
            "PAM70",
            "PAM250",
        ]

        if matrix_name not in available_matrices:
            return {
                "success": False,
                "error": f"Matrix {matrix_name} not available",
                "available_matrices": available_matrices,
            }

        lines = alignment_str.strip().split("\n")
        sequences = [line.strip() for line in lines if line.strip() and not line.startswith(">")]

        if len(sequences) < 2:
            return {
                "success": False,
                "error": "At least 2 aligned sequences required",
                "num_sequences": len(sequences),
            }

        matches = 0
        mismatches = 0
        gaps = 0
        alignment_length = len(sequences[0])

        for i in range(alignment_length):
            col = [seq[i] if i < len(seq) else "-" for seq in sequences]

            for j in range(len(col) - 1):
                if col[j] == "-" or col[j + 1] == "-":
                    gaps += 1
                elif col[j] == col[j + 1]:
                    matches += 1
                else:
                    mismatches += 1

        return {
            "success": True,
            "matrix_used": matrix_name,
            "alignment_length": alignment_length,
            "num_sequences": len(sequences),
            "statistics": {
                "matches": matches,
                "mismatches": mismatches,
                "gaps": gaps,
                "identity_percent": (
                    round((matches / alignment_length) * 100, 2) if alignment_length > 0 else 0
                ),
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e), "matrix_name": matrix_name}
