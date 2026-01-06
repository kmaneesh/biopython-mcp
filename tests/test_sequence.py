"""Tests for sequence operations."""

from biopython_mcp.sequence import (
    calculate_gc_content,
    find_motif,
    reverse_complement,
    transcribe_dna,
    translate_sequence,
)


class TestTranslateSequence:
    """Tests for translate_sequence function."""

    def test_translate_simple_dna(self) -> None:
        """Test translation of a simple DNA sequence."""
        result = translate_sequence("ATGGCCATTGTAATGGGCCGC")
        assert result["success"] is True
        assert result["protein_sequence"] == "MAIVMGR"
        assert result["protein_length"] == 7

    def test_translate_with_stop_codon(self) -> None:
        """Test translation stopping at stop codon."""
        result = translate_sequence("ATGTAAGCC", to_stop=True)
        assert result["success"] is True
        assert result["protein_length"] == 1

    def test_translate_invalid_sequence(self) -> None:
        """Test translation with invalid characters."""
        result = translate_sequence("ATGXYZ")
        assert result["success"] is False
        assert "error" in result


class TestReverseComplement:
    """Tests for reverse_complement function."""

    def test_reverse_complement_simple(self) -> None:
        """Test reverse complement of simple sequence."""
        result = reverse_complement("ATCG")
        assert result["success"] is True
        assert result["reverse_complement"] == "CGAT"

    def test_reverse_complement_longer(self) -> None:
        """Test reverse complement of longer sequence."""
        result = reverse_complement("ATGGCCATTGTAATGGGCCGC")
        assert result["success"] is True
        assert len(result["reverse_complement"]) == 21


class TestTranscribeDNA:
    """Tests for transcribe_dna function."""

    def test_transcribe_dna_to_rna(self) -> None:
        """Test DNA to RNA transcription."""
        result = transcribe_dna("ATCG")
        assert result["success"] is True
        assert result["output_sequence"] == "AUCG"
        assert result["operation"] == "transcription"

    def test_reverse_transcribe_rna_to_dna(self) -> None:
        """Test RNA to DNA reverse transcription."""
        result = transcribe_dna("AUCG", reverse=True)
        assert result["success"] is True
        assert result["output_sequence"] == "ATCG"
        assert result["operation"] == "reverse_transcription"


class TestCalculateGCContent:
    """Tests for calculate_gc_content function."""

    def test_gc_content_50_percent(self) -> None:
        """Test GC content calculation for 50% GC."""
        result = calculate_gc_content("ATGC")
        assert result["success"] is True
        assert result["gc_content_percent"] == 50.0

    def test_gc_content_high(self) -> None:
        """Test GC content calculation for high GC."""
        result = calculate_gc_content("GGCC")
        assert result["success"] is True
        assert result["gc_content_percent"] == 100.0

    def test_gc_content_counts(self) -> None:
        """Test nucleotide counts."""
        result = calculate_gc_content("ATGC")
        assert result["nucleotide_counts"]["A"] == 1
        assert result["nucleotide_counts"]["T"] == 1
        assert result["nucleotide_counts"]["G"] == 1
        assert result["nucleotide_counts"]["C"] == 1


class TestFindMotif:
    """Tests for find_motif function."""

    def test_find_motif_single_occurrence(self) -> None:
        """Test finding a motif with single occurrence."""
        result = find_motif("ATGCATGC", "ATG")
        assert result["success"] is True
        assert result["occurrences"] == 2
        assert result["positions"] == [0, 4]

    def test_find_motif_no_occurrence(self) -> None:
        """Test finding a motif with no occurrence."""
        result = find_motif("ATGC", "TTT")
        assert result["success"] is True
        assert result["occurrences"] == 0
        assert result["positions"] == []

    def test_find_motif_overlapping(self) -> None:
        """Test finding overlapping motifs."""
        result = find_motif("AAAA", "AA", overlapping=True)
        assert result["success"] is True
        assert result["occurrences"] == 3

    def test_find_motif_non_overlapping(self) -> None:
        """Test finding non-overlapping motifs."""
        result = find_motif("AAAA", "AA", overlapping=False)
        assert result["success"] is True
        assert result["occurrences"] == 2
