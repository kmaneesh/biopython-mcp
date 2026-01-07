"""Tests for phylogenetics module."""

from io import StringIO
from unittest.mock import MagicMock, mock_open, patch

import pytest

from biopython_mcp import phylo


class TestBuildPhylogeneticTree:
    """Tests for build_phylogenetic_tree function."""

    @patch("biopython_mcp.phylo.Phylo")
    @patch("biopython_mcp.phylo.AlignIO")
    @patch("biopython_mcp.phylo.DistanceCalculator")
    @patch("biopython_mcp.phylo.DistanceTreeConstructor")
    def test_build_tree_upgma_success(
        self,
        mock_constructor: MagicMock,
        mock_calculator: MagicMock,
        mock_alignio: MagicMock,
        mock_phylo: MagicMock,
    ) -> None:
        """Test successful tree building with UPGMA."""
        # Mock alignment
        mock_alignment = MagicMock()
        mock_alignio.read.return_value = mock_alignment

        # Mock distance matrix
        mock_calc_instance = MagicMock()
        mock_distance_matrix = MagicMock()
        mock_calc_instance.get_distance.return_value = mock_distance_matrix
        mock_calculator.return_value = mock_calc_instance

        # Mock tree
        mock_tree = MagicMock()
        mock_constructor_instance = MagicMock()
        mock_constructor_instance.upgma.return_value = mock_tree
        mock_constructor.return_value = mock_constructor_instance

        # Mock tree writing
        tree_str = StringIO()
        mock_phylo.write.return_value = None

        result = phylo.build_phylogenetic_tree("/tmp/test.fasta", method="upgma")

        assert result["success"] is True
        assert result["method"] == "upgma"
        assert "tree" in result

    @patch("biopython_mcp.phylo.Phylo")
    @patch("biopython_mcp.phylo.AlignIO")
    @patch("biopython_mcp.phylo.DistanceCalculator")
    @patch("biopython_mcp.phylo.DistanceTreeConstructor")
    def test_build_tree_nj_success(
        self,
        mock_constructor: MagicMock,
        mock_calculator: MagicMock,
        mock_alignio: MagicMock,
        mock_phylo: MagicMock,
    ) -> None:
        """Test successful tree building with neighbor joining."""
        mock_alignment = MagicMock()
        mock_alignio.read.return_value = mock_alignment

        mock_calc_instance = MagicMock()
        mock_distance_matrix = MagicMock()
        mock_calc_instance.get_distance.return_value = mock_distance_matrix
        mock_calculator.return_value = mock_calc_instance

        mock_tree = MagicMock()
        mock_constructor_instance = MagicMock()
        mock_constructor_instance.nj.return_value = mock_tree
        mock_constructor.return_value = mock_constructor_instance

        mock_phylo.write.return_value = None

        result = phylo.build_phylogenetic_tree("/tmp/test.fasta", method="nj")

        assert result["success"] is True
        assert result["method"] == "nj"
        mock_constructor_instance.nj.assert_called_once()

    def test_build_tree_invalid_method(self) -> None:
        """Test tree building with invalid method."""
        result = phylo.build_phylogenetic_tree("/tmp/test.fasta", method="invalid")

        assert result["success"] is False
        assert "method" in result["error"].lower()

    @patch("biopython_mcp.phylo.AlignIO")
    def test_build_tree_file_not_found(self, mock_alignio: MagicMock) -> None:
        """Test tree building with non-existent file."""
        mock_alignio.read.side_effect = FileNotFoundError("File not found")

        result = phylo.build_phylogenetic_tree("/nonexistent/file.fasta")

        assert result["success"] is False
        assert "error" in result

    @patch("biopython_mcp.phylo.AlignIO")
    def test_build_tree_parse_error(self, mock_alignio: MagicMock) -> None:
        """Test tree building with parse error."""
        mock_alignio.read.side_effect = Exception("Parse error")

        result = phylo.build_phylogenetic_tree("/tmp/test.fasta")

        assert result["success"] is False
        assert "Parse error" in result["error"]


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
        mock_matrix.names = ["seq1", "seq2"]
        mock_matrix.matrix = [[0.0], [0.5, 0.0]]
        mock_calc_instance.get_distance.return_value = mock_matrix
        mock_calculator.return_value = mock_calc_instance

        result = phylo.calculate_distance_matrix("/tmp/test.fasta")

        assert result["success"] is True
        assert "matrix" in result
        assert "names" in result
        assert result["names"] == ["seq1", "seq2"]

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
        mock_matrix.names = ["seq1"]
        mock_matrix.matrix = [[0.0]]
        mock_calc_instance.get_distance.return_value = mock_matrix
        mock_calculator.return_value = mock_calc_instance

        result = phylo.calculate_distance_matrix("/tmp/test.fasta", model="blosum62")

        assert result["success"] is True
        assert result["model"] == "blosum62"

    @patch("biopython_mcp.phylo.AlignIO")
    def test_calculate_distance_matrix_file_not_found(self, mock_alignio: MagicMock) -> None:
        """Test distance matrix with non-existent file."""
        mock_alignio.read.side_effect = FileNotFoundError("File not found")

        result = phylo.calculate_distance_matrix("/nonexistent/file.fasta")

        assert result["success"] is False
        assert "error" in result

    @patch("biopython_mcp.phylo.AlignIO")
    def test_calculate_distance_matrix_error(self, mock_alignio: MagicMock) -> None:
        """Test distance matrix calculation error."""
        mock_alignio.read.side_effect = Exception("Calculation error")

        result = phylo.calculate_distance_matrix("/tmp/test.fasta")

        assert result["success"] is False
        assert "Calculation error" in result["error"]


class TestDrawTree:
    """Tests for draw_tree function."""

    @patch("biopython_mcp.phylo.Phylo")
    @patch("biopython_mcp.phylo.matplotlib")
    def test_draw_tree_success(self, mock_matplotlib: MagicMock, mock_phylo: MagicMock) -> None:
        """Test successful tree drawing."""
        # Mock tree
        mock_tree = MagicMock()
        mock_stringio = StringIO(">tree\nA:0.1,B:0.2;")
        mock_phylo.read.return_value = mock_tree

        # Mock matplotlib
        mock_pyplot = MagicMock()
        mock_matplotlib.pyplot = mock_pyplot

        result = phylo.draw_tree(">tree\nA:0.1,B:0.2;", output_file="/tmp/tree.png")

        assert result["success"] is True
        assert result["output_file"] == "/tmp/tree.png"
        mock_pyplot.savefig.assert_called_once_with("/tmp/tree.png")

    @patch("biopython_mcp.phylo.Phylo")
    def test_draw_tree_parse_error(self, mock_phylo: MagicMock) -> None:
        """Test tree drawing with parse error."""
        mock_phylo.read.side_effect = Exception("Invalid tree format")

        result = phylo.draw_tree("invalid tree data")

        assert result["success"] is False
        assert "Invalid tree format" in result["error"]

    @patch("biopython_mcp.phylo.Phylo")
    @patch("biopython_mcp.phylo.matplotlib")
    def test_draw_tree_save_error(self, mock_matplotlib: MagicMock, mock_phylo: MagicMock) -> None:
        """Test tree drawing with save error."""
        mock_tree = MagicMock()
        mock_phylo.read.return_value = mock_tree

        mock_pyplot = MagicMock()
        mock_pyplot.savefig.side_effect = Exception("Cannot write file")
        mock_matplotlib.pyplot = mock_pyplot

        result = phylo.draw_tree(">tree\nA:0.1;", output_file="/tmp/tree.png")

        assert result["success"] is False
        assert "Cannot write file" in result["error"]

    @patch("biopython_mcp.phylo.Phylo")
    @patch("biopython_mcp.phylo.matplotlib")
    def test_draw_tree_default_output(
        self, mock_matplotlib: MagicMock, mock_phylo: MagicMock
    ) -> None:
        """Test tree drawing with default output file."""
        mock_tree = MagicMock()
        mock_phylo.read.return_value = mock_tree

        mock_pyplot = MagicMock()
        mock_matplotlib.pyplot = mock_pyplot

        result = phylo.draw_tree(">tree\nA:0.1;")

        assert result["success"] is True
        assert result["output_file"] == "phylogenetic_tree.png"
