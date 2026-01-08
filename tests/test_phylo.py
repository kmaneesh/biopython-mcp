"""Tests for phylogenetics module."""

from typing import Any
from unittest.mock import MagicMock, patch

from biopython_mcp import phylo


class TestBuildPhylogeneticTree:
    """Tests for build_phylogenetic_tree function."""

    @patch("biopython_mcp.phylo.Phylo")
    @patch("biopython_mcp.phylo.AlignIO")
    @patch("biopython_mcp.phylo.DistanceTreeConstructor")
    def test_build_tree_upgma_success(
        self,
        mock_constructor: MagicMock,
        mock_alignio: MagicMock,
        mock_phylo: MagicMock,
    ) -> None:
        """Test successful tree building with UPGMA."""
        # Mock alignment
        mock_alignment = MagicMock()
        mock_alignio.read.return_value = mock_alignment

        # Mock tree constructor
        mock_tree = MagicMock()
        mock_constructor_instance = MagicMock()
        mock_constructor_instance.build_tree.return_value = mock_tree
        mock_constructor.return_value = mock_constructor_instance

        # Mock tree writing - Phylo.write writes to StringIO
        def mock_write(tree: Any, file_handle: Any, format: str) -> None:
            file_handle.write("((Seq1:0.1,Seq2:0.2):0.3,Seq3:0.4);")

        mock_phylo.write.side_effect = mock_write

        sequences = ["ATCG", "ATGG", "GTCG"]
        result = phylo.build_phylogenetic_tree(sequences, method="upgma")

        assert result["success"] is True
        assert result["method"] == "upgma"
        assert "tree_newick" in result
        assert result["num_sequences"] == 3

    @patch("biopython_mcp.phylo.Phylo")
    @patch("biopython_mcp.phylo.AlignIO")
    @patch("biopython_mcp.phylo.DistanceTreeConstructor")
    def test_build_tree_nj_success(
        self,
        mock_constructor: MagicMock,
        mock_alignio: MagicMock,
        mock_phylo: MagicMock,
    ) -> None:
        """Test successful tree building with neighbor joining."""
        mock_alignment = MagicMock()
        mock_alignio.read.return_value = mock_alignment

        mock_tree = MagicMock()
        mock_constructor_instance = MagicMock()
        mock_constructor_instance.build_tree.return_value = mock_tree
        mock_constructor.return_value = mock_constructor_instance

        def mock_write(tree: Any, file_handle: Any, format: str) -> None:
            file_handle.write("((Seq1:0.1,Seq2:0.2):0.3,Seq3:0.4);")

        mock_phylo.write.side_effect = mock_write

        sequences = ["ATCG", "ATGG", "GTCG"]
        result = phylo.build_phylogenetic_tree(sequences, method="nj")

        assert result["success"] is True
        assert result["method"] == "nj"
        assert "tree_newick" in result

    def test_build_tree_invalid_method(self) -> None:
        """Test tree building with invalid method."""
        sequences = ["ATCG", "ATGG", "GTCG"]
        result = phylo.build_phylogenetic_tree(sequences, method="invalid")

        assert result["success"] is False
        assert "method" in result["error"].lower()

    def test_build_tree_too_few_sequences(self) -> None:
        """Test tree building with too few sequences."""
        sequences = ["ATCG", "ATGG"]
        result = phylo.build_phylogenetic_tree(sequences)

        assert result["success"] is False
        assert "at least 3" in result["error"].lower()

    @patch("biopython_mcp.phylo.AlignIO")
    def test_build_tree_parse_error(self, mock_alignio: MagicMock) -> None:
        """Test tree building with parse error."""
        mock_alignio.read.side_effect = Exception("Parse error")

        sequences = ["ATCG", "ATGG", "GTCG"]
        result = phylo.build_phylogenetic_tree(sequences)

        assert result["success"] is False
        assert "Parse error" in result["error"]

    def test_build_tree_label_mismatch(self) -> None:
        """Test tree building with mismatched labels."""
        sequences = ["ATCG", "ATGG", "GTCG"]
        labels = ["Seq1", "Seq2"]  # Only 2 labels for 3 sequences

        result = phylo.build_phylogenetic_tree(sequences, labels=labels)

        assert result["success"] is False
        assert "labels must match" in result["error"].lower()


class TestCalculateDistanceMatrix:
    """Tests for calculate_distance_matrix function."""

    @patch("biopython_mcp.phylo.AlignIO")
    @patch("biopython_mcp.phylo.DistanceCalculator")
    def test_calculate_distance_matrix_success(
        self, mock_calculator: MagicMock, mock_alignio: MagicMock
    ) -> None:
        """Test successful distance matrix calculation."""
        # Mock alignment
        mock_alignment = MagicMock()
        mock_alignio.read.return_value = mock_alignment

        # Mock distance matrix
        mock_calc_instance = MagicMock()
        mock_matrix = MagicMock()
        mock_matrix.names = ["Seq1", "Seq2"]
        # Mock __getitem__ for matrix access
        mock_matrix.__getitem__ = lambda self, idx: [0.0, 0.5][idx[0]] if idx[0] != idx[1] else 0.0
        mock_calc_instance.get_distance.return_value = mock_matrix
        mock_calculator.return_value = mock_calc_instance

        sequences = ["ATCG", "ATGG"]
        result = phylo.calculate_distance_matrix(sequences)

        assert result["success"] is True
        assert "distance_matrix" in result
        assert "labels" in result
        assert result["labels"] == ["Seq1", "Seq2"]
        assert result["num_sequences"] == 2

    @patch("biopython_mcp.phylo.AlignIO")
    @patch("biopython_mcp.phylo.DistanceCalculator")
    def test_calculate_distance_matrix_custom_model(
        self, mock_calculator: MagicMock, mock_alignio: MagicMock
    ) -> None:
        """Test distance matrix with custom model."""
        mock_alignment = MagicMock()
        mock_alignio.read.return_value = mock_alignment

        mock_calc_instance = MagicMock()
        mock_matrix = MagicMock()
        mock_matrix.names = ["Seq1", "Seq2"]
        mock_matrix.__getitem__ = lambda self, idx: 0.0 if idx[0] == idx[1] else 0.3
        mock_calc_instance.get_distance.return_value = mock_matrix
        mock_calculator.return_value = mock_calc_instance

        sequences = ["ATCG", "ATGG"]
        result = phylo.calculate_distance_matrix(sequences, model="blosum62")

        assert result["success"] is True
        assert result["model"] == "blosum62"

    def test_calculate_distance_matrix_too_few_sequences(self) -> None:
        """Test distance matrix with too few sequences."""
        sequences = ["ATCG"]
        result = phylo.calculate_distance_matrix(sequences)

        assert result["success"] is False
        assert "at least 2" in result["error"].lower()

    @patch("biopython_mcp.phylo.AlignIO")
    def test_calculate_distance_matrix_error(self, mock_alignio: MagicMock) -> None:
        """Test distance matrix calculation error."""
        mock_alignio.read.side_effect = Exception("Calculation error")

        sequences = ["ATCG", "ATGG"]
        result = phylo.calculate_distance_matrix(sequences)

        assert result["success"] is False
        assert "Calculation error" in result["error"]

    def test_calculate_distance_matrix_label_mismatch(self) -> None:
        """Test distance matrix with mismatched labels."""
        sequences = ["ATCG", "ATGG"]
        labels = ["Seq1"]  # Only 1 label for 2 sequences

        result = phylo.calculate_distance_matrix(sequences, labels=labels)

        assert result["success"] is False
        assert "labels must match" in result["error"].lower()


class TestDrawTree:
    """Tests for draw_tree function."""

    @patch("biopython_mcp.phylo.Phylo")
    def test_draw_tree_success(self, mock_phylo: MagicMock) -> None:
        """Test successful tree drawing in ASCII format."""
        # Mock tree
        mock_tree = MagicMock()
        mock_tree.count_terminals.return_value = 3
        mock_phylo.read.return_value = mock_tree

        # Mock draw_ascii - it writes to StringIO
        def mock_draw_ascii(tree: Any, file: Any) -> None:
            file.write("  _____ Seq1\n _|\n  |____ Seq2\n|\n|_______ Seq3\n")

        mock_phylo.draw_ascii = mock_draw_ascii

        tree_newick = "((Seq1:0.1,Seq2:0.2):0.3,Seq3:0.4);"
        result = phylo.draw_tree(tree_newick, output_format="ascii")

        assert result["success"] is True
        assert result["format"] == "ascii"
        assert "visualization" in result
        assert result["num_terminals"] == 3
        assert "Seq1" in result["visualization"]

    @patch("biopython_mcp.phylo.Phylo")
    def test_draw_tree_parse_error(self, mock_phylo: MagicMock) -> None:
        """Test tree drawing with parse error."""
        mock_phylo.read.side_effect = Exception("Invalid tree format")

        result = phylo.draw_tree("invalid tree data")

        assert result["success"] is False
        assert "Invalid tree format" in result["error"]

    def test_draw_tree_unsupported_format(self) -> None:
        """Test tree drawing with unsupported format."""
        tree_newick = "((Seq1:0.1,Seq2:0.2):0.3,Seq3:0.4);"
        result = phylo.draw_tree(tree_newick, output_format="png")

        assert result["success"] is False
        assert "unsupported format" in result["error"].lower()

    @patch("biopython_mcp.phylo.Phylo")
    def test_draw_tree_default_format(self, mock_phylo: MagicMock) -> None:
        """Test tree drawing with default (ascii) format."""
        mock_tree = MagicMock()
        mock_tree.count_terminals.return_value = 2
        mock_phylo.read.return_value = mock_tree

        def mock_draw_ascii(tree: Any, file: Any) -> None:
            file.write(" ___ A\n|\n|___ B\n")

        mock_phylo.draw_ascii = mock_draw_ascii

        tree_newick = "(A:0.1,B:0.2);"
        result = phylo.draw_tree(tree_newick)

        assert result["success"] is True
        assert result["format"] == "ascii"
