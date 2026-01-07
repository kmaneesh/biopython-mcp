"""Tests for structure analysis module."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from biopython_mcp import structure


class TestFetchPDBStructure:
    """Tests for fetch_pdb_structure function."""

    @patch("biopython_mcp.structure.PDB.PDBList")
    def test_fetch_pdb_success(self, mock_pdblist: MagicMock) -> None:
        """Test successful PDB structure fetch."""
        mock_list_instance = MagicMock()
        mock_list_instance.retrieve_pdb_file.return_value = "/tmp/pdb1abc.ent"
        mock_pdblist.return_value = mock_list_instance

        result = structure.fetch_pdb_structure("1ABC")

        assert result["success"] is True
        assert result["pdb_id"] == "1ABC"
        assert "file_path" in result
        mock_list_instance.retrieve_pdb_file.assert_called_once()

    @patch("biopython_mcp.structure.PDB.PDBList")
    def test_fetch_pdb_failure(self, mock_pdblist: MagicMock) -> None:
        """Test PDB fetch failure."""
        mock_list_instance = MagicMock()
        mock_list_instance.retrieve_pdb_file.side_effect = Exception("Network error")
        mock_pdblist.return_value = mock_list_instance

        result = structure.fetch_pdb_structure("1ABC")

        assert result["success"] is False
        assert "error" in result
        assert "Network error" in result["error"]


class TestCalculateStructureStats:
    """Tests for calculate_structure_stats function."""

    @patch("biopython_mcp.structure.PDB.PDBParser")
    @patch("builtins.open", mock_open(read_data="PDB DATA"))
    def test_calculate_stats_success(self, mock_parser: MagicMock) -> None:
        """Test successful structure statistics calculation."""
        # Mock structure
        mock_structure = MagicMock()
        mock_model = MagicMock()
        mock_chain = MagicMock()
        mock_residue = MagicMock()
        mock_atom = MagicMock()

        # Set up chain
        mock_chain.get_id.return_value = "A"
        mock_chain.__iter__.return_value = [mock_residue]

        # Set up residue
        mock_residue.get_id.return_value = ("H_ALA", 1, " ")
        mock_residue.__iter__.return_value = [mock_atom]

        # Set up model
        mock_model.__iter__.return_value = [mock_chain]

        # Set up structure
        mock_structure.__iter__.return_value = [mock_model]

        mock_parser_instance = MagicMock()
        mock_parser_instance.get_structure.return_value = mock_structure
        mock_parser.return_value = mock_parser_instance

        result = structure.calculate_structure_stats("/tmp/test.pdb")

        assert result["success"] is True
        assert "num_atoms" in result
        assert "num_residues" in result
        assert "num_chains" in result

    @patch("biopython_mcp.structure.PDB.PDBParser")
    def test_calculate_stats_file_not_found(self, mock_parser: MagicMock) -> None:
        """Test statistics calculation with non-existent file."""
        mock_parser_instance = MagicMock()
        mock_parser_instance.get_structure.side_effect = FileNotFoundError("File not found")
        mock_parser.return_value = mock_parser_instance

        result = structure.calculate_structure_stats("/nonexistent/file.pdb")

        assert result["success"] is False
        assert "error" in result

    @patch("biopython_mcp.structure.PDB.PDBParser")
    def test_calculate_stats_parse_error(self, mock_parser: MagicMock) -> None:
        """Test statistics calculation with parse error."""
        mock_parser_instance = MagicMock()
        mock_parser_instance.get_structure.side_effect = Exception("Parse error")
        mock_parser.return_value = mock_parser_instance

        result = structure.calculate_structure_stats("/tmp/test.pdb")

        assert result["success"] is False
        assert "Parse error" in result["error"]


class TestFindActiveSite:
    """Tests for find_active_site function."""

    @patch("biopython_mcp.structure.PDB.PDBParser")
    @patch("builtins.open", mock_open(read_data="PDB DATA"))
    def test_find_active_site_success(self, mock_parser: MagicMock) -> None:
        """Test successful active site finding."""
        # Mock atoms with coordinates
        mock_atom1 = MagicMock()
        mock_atom1.get_coord.return_value = [0.0, 0.0, 0.0]
        mock_atom1.get_parent.return_value.get_id.return_value = ("H_SER", 100, " ")
        mock_atom1.get_parent.return_value.get_parent.return_value.get_id.return_value = "A"
        mock_atom1.get_name.return_value = "OG"

        mock_atom2 = MagicMock()
        mock_atom2.get_coord.return_value = [1.0, 0.0, 0.0]
        mock_atom2.get_parent.return_value.get_id.return_value = ("H_HIS", 101, " ")
        mock_atom2.get_parent.return_value.get_parent.return_value.get_id.return_value = "A"
        mock_atom2.get_name.return_value = "ND1"

        mock_target_atom = MagicMock()
        mock_target_atom.get_coord.return_value = [0.5, 0.0, 0.0]

        # Mock residue
        mock_residue = MagicMock()
        mock_residue.get_id.return_value = ("H_LIG", 200, " ")
        mock_residue.__iter__.return_value = [mock_target_atom]

        # Mock chain
        mock_chain = MagicMock()
        mock_chain.__iter__.return_value = [mock_residue]
        mock_chain.__getitem__.return_value = mock_residue

        # Mock model
        mock_model = MagicMock()
        mock_model.__iter__.return_value = [mock_chain]
        mock_model.__getitem__.return_value = mock_chain

        # Mock structure
        mock_structure = MagicMock()
        mock_structure.__iter__.return_value = [mock_model]
        mock_structure.__getitem__.return_value = mock_model

        # Mock atom search
        mock_structure.get_atoms.return_value = [mock_atom1, mock_atom2, mock_target_atom]

        mock_parser_instance = MagicMock()
        mock_parser_instance.get_structure.return_value = mock_structure
        mock_parser.return_value = mock_parser_instance

        result = structure.find_active_site("/tmp/test.pdb", "A", 200)

        assert result["success"] is True
        assert "residues" in result

    @patch("biopython_mcp.structure.PDB.PDBParser")
    def test_find_active_site_residue_not_found(self, mock_parser: MagicMock) -> None:
        """Test active site finding with non-existent residue."""
        mock_chain = MagicMock()
        mock_chain.__getitem__.side_effect = KeyError("Residue not found")

        mock_model = MagicMock()
        mock_model.__getitem__.return_value = mock_chain

        mock_structure = MagicMock()
        mock_structure.__getitem__.return_value = mock_model

        mock_parser_instance = MagicMock()
        mock_parser_instance.get_structure.return_value = mock_structure
        mock_parser.return_value = mock_parser_instance

        result = structure.find_active_site("/tmp/test.pdb", "A", 999)

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @patch("biopython_mcp.structure.PDB.PDBParser")
    def test_find_active_site_parse_error(self, mock_parser: MagicMock) -> None:
        """Test active site finding with parse error."""
        mock_parser_instance = MagicMock()
        mock_parser_instance.get_structure.side_effect = Exception("Parse error")
        mock_parser.return_value = mock_parser_instance

        result = structure.find_active_site("/tmp/test.pdb", "A", 100)

        assert result["success"] is False
        assert "error" in result
