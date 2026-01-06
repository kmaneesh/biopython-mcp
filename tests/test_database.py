"""Tests for database operations."""

import pytest

from src.database import fetch_genbank, fetch_sequence_by_id, fetch_uniprot, search_pubmed


class TestFetchGenBank:
    """Tests for fetch_genbank function."""

    @pytest.mark.skip(reason="Requires network access")
    def test_fetch_genbank_valid(self) -> None:
        """Test fetching valid GenBank record."""
        result = fetch_genbank("NM_000207", email="test@example.com")
        assert result["success"] is True
        assert result["accession"] == "NM_000207"

    def test_fetch_genbank_invalid(self) -> None:
        """Test fetching invalid GenBank record."""
        result = fetch_genbank("INVALID_ID", email="test@example.com")
        assert result["success"] is False
        assert "error" in result


class TestFetchUniProt:
    """Tests for fetch_uniprot function."""

    @pytest.mark.skip(reason="Requires network access")
    def test_fetch_uniprot_valid(self) -> None:
        """Test fetching valid UniProt record."""
        result = fetch_uniprot("P12345")
        assert result["success"] is True
        assert result["uniprot_id"] == "P12345"

    def test_fetch_uniprot_formats(self) -> None:
        """Test different UniProt formats."""
        for fmt in ["fasta", "txt", "xml"]:
            result = fetch_uniprot("INVALID", format=fmt)
            assert "format" in result or "error" in result


class TestSearchPubMed:
    """Tests for search_pubmed function."""

    @pytest.mark.skip(reason="Requires network access")
    def test_search_pubmed_valid(self) -> None:
        """Test searching PubMed."""
        result = search_pubmed("cancer", max_results=5, email="test@example.com")
        assert result["success"] is True
        assert "results" in result

    def test_search_pubmed_parameters(self) -> None:
        """Test PubMed search parameters."""
        result = search_pubmed("test", max_results=1, email="test@example.com")
        assert "query" in result


class TestFetchSequenceById:
    """Tests for fetch_sequence_by_id function."""

    @pytest.mark.skip(reason="Requires network access")
    def test_fetch_sequence_valid(self) -> None:
        """Test fetching valid sequence."""
        result = fetch_sequence_by_id("nucleotide", "NM_000207", email="test@example.com")
        assert result["success"] is True
        assert result["database"] == "nucleotide"

    def test_fetch_sequence_invalid_db(self) -> None:
        """Test fetching from invalid database."""
        result = fetch_sequence_by_id("invalid_db", "test", email="test@example.com")
        assert result["success"] is False
