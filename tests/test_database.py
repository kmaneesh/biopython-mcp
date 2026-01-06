"""Tests for database operations."""

import os

import pytest

from biopython_mcp.database import fetch_genbank, fetch_sequence_by_id, fetch_uniprot, search_pubmed


class TestFetchGenBank:
    """Tests for fetch_genbank function."""

    @pytest.mark.entrez
    def test_fetch_genbank_valid(self) -> None:
        """Test fetching valid GenBank record."""
        result = fetch_genbank("NM_000207", email=os.environ["NCBI_EMAIL"])
        assert result["success"] is True
        assert result["accession"] == "NM_000207"
        assert "data" in result
        assert result["length"] > 0

    def test_fetch_genbank_invalid(self) -> None:
        """Test fetching invalid GenBank record."""
        result = fetch_genbank("INVALID_ID", email="test@example.com")
        assert result["success"] is False
        assert "error" in result


class TestFetchUniProt:
    """Tests for fetch_uniprot function."""

    @pytest.mark.network
    def test_fetch_uniprot_valid(self) -> None:
        """Test fetching valid UniProt record."""
        # Use a well-known stable UniProt accession.
        result = fetch_uniprot("P69905")
        assert result["success"] is True
        assert result["uniprot_id"] == "P69905"
        assert "data" in result
        assert result["length"] > 0

    def test_fetch_uniprot_formats(self) -> None:
        """Test different UniProt formats."""
        for fmt in ["fasta", "txt", "xml"]:
            result = fetch_uniprot("INVALID", format=fmt)
            assert "format" in result or "error" in result


class TestSearchPubMed:
    """Tests for search_pubmed function."""

    @pytest.mark.entrez
    def test_search_pubmed_valid(self) -> None:
        """Test searching PubMed."""
        result = search_pubmed("cancer", max_results=3, email=os.environ["NCBI_EMAIL"])
        assert result["success"] is True
        assert "results" in result
        assert result["count"] <= 3

    def test_search_pubmed_parameters(self) -> None:
        """Test PubMed search parameters."""
        result = search_pubmed("test", max_results=1, email="test@example.com")
        assert "query" in result


class TestFetchSequenceById:
    """Tests for fetch_sequence_by_id function."""

    @pytest.mark.entrez
    def test_fetch_sequence_valid(self) -> None:
        """Test fetching valid sequence."""
        result = fetch_sequence_by_id("nucleotide", "NM_000207", email=os.environ["NCBI_EMAIL"])
        assert result["success"] is True
        assert result["database"] == "nucleotide"
        assert result["length"] > 0

    def test_fetch_sequence_invalid_db(self) -> None:
        """Test fetching from invalid database."""
        result = fetch_sequence_by_id("invalid_db", "test", email="test@example.com")
        assert result["success"] is False
