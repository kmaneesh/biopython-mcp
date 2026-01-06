"""Tests for alignment operations."""

from biopython_mcp.alignment import calculate_alignment_score, pairwise_align


class TestPairwiseAlign:
    """Tests for pairwise_align function."""

    def test_global_alignment_identical(self) -> None:
        """Test global alignment of identical sequences."""
        result = pairwise_align("ATCG", "ATCG", mode="global")
        assert result["success"] is True
        assert result["mode"] == "global"
        assert result["score"] > 0

    def test_global_alignment_different(self) -> None:
        """Test global alignment of different sequences."""
        result = pairwise_align("ATCG", "TTTT", mode="global")
        assert result["success"] is True
        assert result["mode"] == "global"

    def test_local_alignment(self) -> None:
        """Test local alignment."""
        result = pairwise_align("ATCGATCG", "ATCG", mode="local")
        assert result["success"] is True
        assert result["mode"] == "local"

    def test_custom_scoring(self) -> None:
        """Test alignment with custom scoring."""
        result = pairwise_align("ATCG", "ATCG", match_score=5.0, mismatch_score=-2.0, gap_open=-3.0)
        assert result["success"] is True
        assert result["parameters"]["match_score"] == 5.0


class TestCalculateAlignmentScore:
    """Tests for calculate_alignment_score function."""

    def test_alignment_score_blosum62(self) -> None:
        """Test alignment scoring with BLOSUM62."""
        alignment = ">seq1\nACDEFG\n>seq2\nACDEFG"
        result = calculate_alignment_score(alignment, matrix_name="BLOSUM62")
        assert result["success"] is True
        assert result["matrix_used"] == "BLOSUM62"

    def test_alignment_score_invalid_matrix(self) -> None:
        """Test alignment scoring with invalid matrix."""
        alignment = ">seq1\nACDEFG\n>seq2\nACDEFG"
        result = calculate_alignment_score(alignment, matrix_name="INVALID")
        assert result["success"] is False
        assert "available_matrices" in result

    def test_alignment_score_statistics(self) -> None:
        """Test alignment statistics calculation."""
        alignment = "ATCG\nATCG"
        result = calculate_alignment_score(alignment)
        assert result["success"] is True
        assert "statistics" in result
        assert "matches" in result["statistics"]
