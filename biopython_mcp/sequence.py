"""Sequence analysis tools using BioPython."""

from typing import Any

from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction

from biopython_mcp.utils import validate_sequence


def translate_sequence(sequence: str, table: int = 1, to_stop: bool = False) -> dict[str, Any]:
    """
    Translate a DNA or RNA sequence to protein.

    Args:
        sequence: DNA or RNA sequence string
        table: Genetic code table to use (default: 1 for standard code)
        to_stop: Stop translation at first stop codon (default: False)

    Returns:
        Dictionary containing the translated protein sequence and metadata
    """
    try:
        seq = Seq(validate_sequence(sequence))
        protein = seq.translate(table=table, to_stop=to_stop)

        return {
            "success": True,
            "input_sequence": str(sequence),
            "input_length": len(sequence),
            "protein_sequence": str(protein),
            "protein_length": len(protein),
            "table": table,
            "stopped_at_stop_codon": to_stop,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "input_sequence": sequence}


def reverse_complement(sequence: str) -> dict[str, Any]:
    """
    Get the reverse complement of a DNA sequence.

    Args:
        sequence: DNA sequence string

    Returns:
        Dictionary containing the reverse complement and metadata
    """
    try:
        seq = Seq(validate_sequence(sequence))
        rev_comp = seq.reverse_complement()

        return {
            "success": True,
            "input_sequence": str(sequence),
            "reverse_complement": str(rev_comp),
            "length": len(sequence),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "input_sequence": sequence}


def transcribe_dna(sequence: str, reverse: bool = False) -> dict[str, Any]:
    """
    Transcribe DNA to RNA (or reverse transcribe RNA to DNA).

    Args:
        sequence: DNA or RNA sequence string
        reverse: If True, reverse transcribe RNA to DNA (default: False)

    Returns:
        Dictionary containing the transcribed sequence and metadata
    """
    try:
        seq = Seq(validate_sequence(sequence))

        if reverse:
            result = seq.back_transcribe()
            operation = "reverse_transcription"
        else:
            result = seq.transcribe()
            operation = "transcription"

        return {
            "success": True,
            "input_sequence": str(sequence),
            "output_sequence": str(result),
            "operation": operation,
            "length": len(sequence),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "input_sequence": sequence}


def calculate_gc_content(sequence: str) -> dict[str, Any]:
    """
    Calculate the GC content of a DNA or RNA sequence.

    Args:
        sequence: DNA or RNA sequence string

    Returns:
        Dictionary containing GC content percentage and counts
    """
    try:
        seq = Seq(validate_sequence(sequence))
        gc_percent = gc_fraction(seq) * 100

        g_count = sequence.upper().count("G")
        c_count = sequence.upper().count("C")
        a_count = sequence.upper().count("A")
        t_count = sequence.upper().count("T")
        u_count = sequence.upper().count("U")

        return {
            "success": True,
            "sequence_length": len(sequence),
            "gc_content_percent": round(gc_percent, 2),
            "nucleotide_counts": {
                "G": g_count,
                "C": c_count,
                "A": a_count,
                "T": t_count,
                "U": u_count,
            },
            "gc_count": g_count + c_count,
            "at_count": a_count + t_count,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "sequence": sequence}


def find_motif(sequence: str, motif: str, overlapping: bool = True) -> dict[str, Any]:
    """
    Find all occurrences of a motif in a sequence.

    Args:
        sequence: DNA, RNA, or protein sequence to search
        motif: Motif pattern to find
        overlapping: Allow overlapping matches (default: True)

    Returns:
        Dictionary containing motif positions and count
    """
    try:
        sequence = validate_sequence(sequence)
        motif = validate_sequence(motif)

        positions = []
        start = 0

        while True:
            pos = sequence.upper().find(motif.upper(), start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + (1 if overlapping else len(motif))

        return {
            "success": True,
            "sequence_length": len(sequence),
            "motif": motif,
            "motif_length": len(motif),
            "occurrences": len(positions),
            "positions": positions,
            "overlapping_search": overlapping,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "sequence": sequence, "motif": motif}
