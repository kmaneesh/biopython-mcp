"""Tests for database operations."""

import os

import pytest

from biopython_mcp.database import (
    clinvar_variant_lookup,
    entrez_fetch,
    entrez_info,
    entrez_search,
    entrez_summary,
    fetch_genbank,
    fetch_sequence_by_id,
    fetch_uniprot,
    gene_info_fetch,
    pubmed_search,
    search_pubmed,
    variant_literature_link,
)


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


# Tests for new Entrez tools
class TestEntrezInfo:
    """Tests for entrez_info function."""

    @pytest.mark.entrez
    def test_entrez_info_all_databases(self) -> None:
        """Test listing all databases."""
        result = entrez_info()
        assert result["success"] is True
        assert "databases" in result
        assert "pubmed" in result["databases"]
        assert result["count"] > 0

    @pytest.mark.entrez
    def test_entrez_info_specific_database(self) -> None:
        """Test getting info for specific database."""
        result = entrez_info("pubmed")
        assert result["success"] is True
        assert result["database"] == "pubmed"
        assert "description" in result
        assert "fields" in result


class TestEntrezSearch:
    """Tests for entrez_search function."""

    @pytest.mark.entrez
    def test_entrez_search_pubmed(self) -> None:
        """Test searching PubMed."""
        result = entrez_search("pubmed", "cancer", max_results=5)
        assert result["success"] is True
        assert len(result["ids"]) <= 5
        assert result["total_found"] > 0
        assert result["database"] == "pubmed"

    @pytest.mark.entrez
    def test_entrez_search_gene(self) -> None:
        """Test searching gene database."""
        result = entrez_search("gene", "BRCA1[Gene] AND Homo sapiens[Organism]", max_results=1)
        assert result["success"] is True
        assert "ids" in result

    def test_entrez_search_invalid_db(self) -> None:
        """Test searching invalid database."""
        result = entrez_search("invalid_db", "test")
        assert result["success"] is False
        assert "error" in result


class TestEntrezFetch:
    """Tests for entrez_fetch function."""

    @pytest.mark.entrez
    def test_entrez_fetch_single_id(self) -> None:
        """Test fetching single record."""
        result = entrez_fetch("nucleotide", "NM_000207", rettype="fasta", retmode="text")
        assert result["success"] is True
        assert result["count"] == 1
        assert "NM_000207" in result["ids"]

    @pytest.mark.entrez
    def test_entrez_fetch_multiple_ids_string(self) -> None:
        """Test fetching multiple IDs as comma-separated string."""
        result = entrez_fetch("gene", "672,7157", rettype="xml")
        assert result["success"] is True
        assert result["count"] == 2

    @pytest.mark.entrez
    def test_entrez_fetch_multiple_ids_list(self) -> None:
        """Test fetching multiple IDs as list."""
        result = entrez_fetch("gene", ["672", "7157"], rettype="xml")
        assert result["success"] is True
        assert result["count"] == 2

    def test_entrez_fetch_no_ids(self) -> None:
        """Test fetching with empty IDs."""
        result = entrez_fetch("pubmed", "")
        assert result["success"] is False
        assert "No valid IDs" in result["error"]


class TestEntrezSummary:
    """Tests for entrez_summary function."""

    @pytest.mark.entrez
    def test_entrez_summary_gene(self) -> None:
        """Test getting gene summary."""
        result = entrez_summary("gene", "672")  # BRCA1
        assert result["success"] is True
        assert result["count"] > 0
        assert "summaries" in result

    @pytest.mark.entrez
    def test_entrez_summary_multiple(self) -> None:
        """Test getting summaries for multiple IDs."""
        result = entrez_summary("gene", ["672", "7157"])
        assert result["success"] is True
        assert result["count"] == 2

    def test_entrez_summary_empty(self) -> None:
        """Test summary with empty IDs."""
        result = entrez_summary("pubmed", "")
        assert result["success"] is False


class TestClinvarVariantLookup:
    """Tests for clinvar_variant_lookup function."""

    @pytest.mark.entrez
    def test_clinvar_lookup_by_gene(self) -> None:
        """Test ClinVar lookup by gene."""
        result = clinvar_variant_lookup(gene="BRCA1", significance="pathogenic", max_results=3)
        assert result["success"] is True
        assert result["count"] <= 3
        assert "query_terms" in result

    @pytest.mark.entrez
    def test_clinvar_lookup_by_gene_only(self) -> None:
        """Test ClinVar lookup with gene only."""
        result = clinvar_variant_lookup(gene="BRCA2", max_results=2)
        assert result["success"] is True
        assert result["query_terms"]["gene"] == "BRCA2"

    def test_clinvar_lookup_no_params(self) -> None:
        """Test ClinVar lookup with no parameters."""
        result = clinvar_variant_lookup()
        assert result["success"] is False
        assert "At least one" in result["error"]


class TestGeneInfoFetch:
    """Tests for gene_info_fetch function."""

    @pytest.mark.entrez
    def test_gene_fetch_by_symbol(self) -> None:
        """Test fetching gene by symbol."""
        result = gene_info_fetch(gene_symbol="BRCA1")
        assert result["success"] is True
        assert result["symbol"] == "BRCA1"
        assert "summary" in result

    @pytest.mark.entrez
    def test_gene_fetch_by_id(self) -> None:
        """Test fetching gene by ID."""
        result = gene_info_fetch(gene_id="672")  # BRCA1
        assert result["success"] is True
        assert result["gene_id"] == "672"

    def test_gene_fetch_no_params(self) -> None:
        """Test gene fetch with no parameters."""
        result = gene_info_fetch()
        assert result["success"] is False
        assert "required" in result["error"].lower()


class TestPubmedSearch:
    """Tests for pubmed_search function."""

    @pytest.mark.entrez
    def test_pubmed_search_basic(self) -> None:
        """Test basic PubMed search."""
        result = pubmed_search("BRCA1", max_results=3)
        assert result["success"] is True
        assert len(result["articles"]) <= 3
        assert all("pmid" in article for article in result["articles"])
        assert all("abstract" in article for article in result["articles"])

    @pytest.mark.entrez
    def test_pubmed_search_year_filter(self) -> None:
        """Test PubMed search with year filter."""
        result = pubmed_search("cancer", year_start=2023, year_end=2024, max_results=2)
        assert result["success"] is True
        assert "articles" in result

    @pytest.mark.entrez
    def test_pubmed_search_no_results(self) -> None:
        """Test PubMed search with no results."""
        result = pubmed_search("zzzzzzznonexistent12345", max_results=1)
        assert result["success"] is True
        assert result["count"] == 0
        assert result["articles"] == []


class TestVariantLiteratureLink:
    """Tests for variant_literature_link function."""

    @pytest.mark.entrez
    def test_variant_link_clinvar(self) -> None:
        """Test linking ClinVar variant to literature."""
        # Use a real ClinVar ID that has literature
        result = variant_literature_link("12345", source_db="clinvar", max_results=5)
        assert result["success"] is True
        assert "linked_pmids" in result
        assert "articles" in result

    def test_variant_link_invalid_db(self) -> None:
        """Test with invalid source database."""
        result = variant_literature_link("12345", source_db="invalid")
        assert result["success"] is False
        assert "invalid" in result["error"].lower()
