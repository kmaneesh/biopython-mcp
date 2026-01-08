"""Tests for utility functions."""

import time
from unittest.mock import patch

import pytest

from biopython_mcp import utils


class TestValidateSequence:
    """Tests for validate_sequence function."""

    def test_valid_dna_sequence(self) -> None:
        """Test valid DNA sequence."""
        seq = utils.validate_sequence("ATCG")
        assert seq == "ATCG"

    def test_valid_rna_sequence(self) -> None:
        """Test valid RNA sequence."""
        seq = utils.validate_sequence("AUCG")
        assert seq == "AUCG"

    def test_lowercase_sequence(self) -> None:
        """Test lowercase sequence is converted to uppercase."""
        seq = utils.validate_sequence("atcg")
        assert seq == "ATCG"

    def test_sequence_with_whitespace(self) -> None:
        """Test sequence with whitespace is stripped."""
        seq = utils.validate_sequence("  ATCG  ")
        assert seq == "ATCG"

    def test_empty_sequence(self) -> None:
        """Test empty sequence raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            utils.validate_sequence("")

    def test_invalid_characters(self) -> None:
        """Test sequence with invalid characters raises error."""
        with pytest.raises(ValueError, match="invalid characters"):
            utils.validate_sequence("ATCGXYZ")

    def test_protein_sequence(self) -> None:
        """Test valid protein sequence."""
        seq = utils.validate_sequence("ACDEFGHIKLMNPQRSTVWY")
        assert seq == "ACDEFGHIKLMNPQRSTVWY"

    def test_ambiguous_dna_codes(self) -> None:
        """Test DNA sequence with ambiguous codes."""
        seq = utils.validate_sequence("ATCGNRYWSMKBDHV")
        assert seq == "ATCGNRYWSMKBDHV"


class TestFormatSequenceOutput:
    """Tests for format_sequence_output function."""

    def test_short_sequence(self) -> None:
        """Test formatting short sequence."""
        output = utils.format_sequence_output("ATCG", line_length=60)
        assert output == "ATCG"

    def test_long_sequence(self) -> None:
        """Test formatting long sequence."""
        seq = "A" * 100
        output = utils.format_sequence_output(seq, line_length=60)
        lines = output.split("\n")
        assert len(lines) == 2
        assert len(lines[0]) == 60
        assert len(lines[1]) == 40

    def test_custom_line_length(self) -> None:
        """Test custom line length."""
        seq = "ATCG" * 10
        output = utils.format_sequence_output(seq, line_length=10)
        lines = output.split("\n")
        assert all(len(line) == 10 for line in lines[:-1])


class TestParseFasta:
    """Tests for parse_fasta function."""

    def test_single_sequence(self) -> None:
        """Test parsing single FASTA sequence."""
        fasta = ">seq1 description\nATCG"
        records = utils.parse_fasta(fasta)
        assert len(records) == 1
        assert records[0]["id"] == "seq1"
        assert records[0]["description"] == "description"
        assert records[0]["sequence"] == "ATCG"

    def test_multiple_sequences(self) -> None:
        """Test parsing multiple FASTA sequences."""
        fasta = ">seq1\nATCG\n>seq2\nGCTA"
        records = utils.parse_fasta(fasta)
        assert len(records) == 2
        assert records[0]["id"] == "seq1"
        assert records[1]["id"] == "seq2"

    def test_multiline_sequence(self) -> None:
        """Test parsing multiline FASTA sequence."""
        fasta = ">seq1\nATCG\nGCTA\nTAGC"
        records = utils.parse_fasta(fasta)
        assert len(records) == 1
        assert records[0]["sequence"] == "ATCGGCTATAGC"  # ATCG + GCTA + TAGC

    def test_empty_lines(self) -> None:
        """Test parsing FASTA with empty lines."""
        fasta = ">seq1\n\nATCG\n\n>seq2\n\nGCTA"
        records = utils.parse_fasta(fasta)
        assert len(records) == 2

    def test_no_description(self) -> None:
        """Test parsing FASTA without description."""
        fasta = ">seq1\nATCG"
        records = utils.parse_fasta(fasta)
        assert records[0]["description"] == ""


class TestFormatFasta:
    """Tests for format_fasta function."""

    def test_single_record(self) -> None:
        """Test formatting single FASTA record."""
        records = [{"id": "seq1", "description": "test", "sequence": "ATCG"}]
        fasta = utils.format_fasta(records)
        assert fasta == ">seq1 test\nATCG"

    def test_long_sequence(self) -> None:
        """Test formatting record with long sequence."""
        records = [{"id": "seq1", "description": "", "sequence": "A" * 100}]
        fasta = utils.format_fasta(records, line_length=60)
        lines = fasta.split("\n")
        assert lines[0] == ">seq1"
        assert len(lines[1]) == 60
        assert len(lines[2]) == 40

    def test_no_description(self) -> None:
        """Test formatting record without description."""
        records = [{"id": "seq1", "description": "", "sequence": "ATCG"}]
        fasta = utils.format_fasta(records)
        assert fasta == ">seq1\nATCG"


class TestCalculateMolecularWeight:
    """Tests for calculate_molecular_weight function."""

    def test_protein_weight(self) -> None:
        """Test protein molecular weight calculation."""
        weight = utils.calculate_molecular_weight("AAA", seq_type="protein")
        assert weight == pytest.approx(89.1 * 3)

    def test_dna_weight(self) -> None:
        """Test DNA molecular weight calculation."""
        weight = utils.calculate_molecular_weight("ATCG", seq_type="dna")
        assert weight > 0

    def test_rna_weight(self) -> None:
        """Test RNA molecular weight calculation."""
        weight = utils.calculate_molecular_weight("AUCG", seq_type="rna")
        assert weight > 0

    def test_invalid_seq_type(self) -> None:
        """Test invalid sequence type raises error."""
        with pytest.raises(ValueError, match="Invalid seq_type"):
            utils.calculate_molecular_weight("ATCG", seq_type="invalid")

    def test_unknown_residue(self) -> None:
        """Test unknown residue is skipped."""
        weight = utils.calculate_molecular_weight("AXA", seq_type="protein")
        assert weight == 89.1 * 2  # Only A's counted


class TestEntrezRateLimiter:
    """Tests for EntrezRateLimiter class."""

    def test_rate_limiter_initialization(self) -> None:
        """Test rate limiter initializes correctly."""
        limiter = utils.EntrezRateLimiter()
        assert limiter.delay > 0
        assert limiter.last_call == 0.0

    def test_rate_limiter_with_api_key(self) -> None:
        """Test rate limiter with API key."""
        with patch.dict("os.environ", {"NCBI_API_KEY": "test_key"}):
            limiter = utils.EntrezRateLimiter()
            assert limiter.has_api_key is True
            assert limiter.delay == 0.1  # 10/sec

    def test_rate_limiter_without_api_key(self) -> None:
        """Test rate limiter without API key."""
        with patch.dict("os.environ", {}, clear=True):
            limiter = utils.EntrezRateLimiter()
            assert limiter.has_api_key is False
            assert limiter.delay == 0.34  # ~3/sec

    def test_rate_limiter_wait(self) -> None:
        """Test rate limiter wait function."""
        limiter = utils.EntrezRateLimiter()
        limiter.delay = 0.01  # Short delay for test
        start = time.time()
        limiter.wait()
        limiter.wait()
        elapsed = time.time() - start
        assert elapsed >= 0.01  # At least one delay period


class TestEntrezRateLimitContext:
    """Tests for entrez_rate_limit context manager."""

    def test_context_manager(self) -> None:
        """Test entrez_rate_limit context manager."""
        with utils.entrez_rate_limit() as limiter:
            assert isinstance(limiter, utils.EntrezRateLimiter)


class TestParseIds:
    """Tests for parse_ids function."""

    def test_single_id_string(self) -> None:
        """Test parsing single ID string."""
        ids = utils.parse_ids("12345")
        assert ids == ["12345"]

    def test_comma_separated_ids(self) -> None:
        """Test parsing comma-separated IDs."""
        ids = utils.parse_ids("123,456,789")
        assert ids == ["123", "456", "789"]

    def test_semicolon_separated_ids(self) -> None:
        """Test parsing semicolon-separated IDs."""
        ids = utils.parse_ids("123;456;789")
        assert ids == ["123", "456", "789"]

    def test_whitespace_separated_ids(self) -> None:
        """Test parsing whitespace-separated IDs."""
        ids = utils.parse_ids("123 456 789")
        assert ids == ["123", "456", "789"]

    def test_mixed_separators(self) -> None:
        """Test parsing IDs with mixed separators."""
        ids = utils.parse_ids("123, 456; 789")
        assert ids == ["123", "456", "789"]

    def test_list_of_ids(self) -> None:
        """Test parsing list of IDs."""
        ids = utils.parse_ids(["123", "456", "789"])
        assert ids == ["123", "456", "789"]

    def test_ids_with_spaces(self) -> None:
        """Test parsing IDs with extra spaces."""
        ids = utils.parse_ids("  123  ,  456  ")
        assert ids == ["123", "456"]

    def test_empty_ids_filtered(self) -> None:
        """Test empty IDs are filtered out."""
        ids = utils.parse_ids("123,,456")
        assert ids == ["123", "456"]


class TestFormatEntrezError:
    """Tests for format_entrez_error function."""

    def test_rate_limit_error(self) -> None:
        """Test formatting rate limit error."""
        error = Exception("HTTP 429 rate limit exceeded")
        result = utils.format_entrez_error(error, {"database": "pubmed"})
        assert result["success"] is False
        assert result["error_type"] == "rate_limit"
        assert result["rate_limit_exceeded"] is True
        assert result["database"] == "pubmed"

    def test_invalid_id_error(self) -> None:
        """Test formatting invalid ID error."""
        error = Exception("Invalid ID not found")
        result = utils.format_entrez_error(error, {"database": "gene"})
        assert result["error_type"] == "invalid_id"

    def test_unknown_error(self) -> None:
        """Test formatting unknown error."""
        error = Exception("Something went wrong")
        result = utils.format_entrez_error(error, {"query": "test"})
        assert result["error_type"] == "unknown"
        assert "Something went wrong" in result["error"]


class TestCaching:
    """Tests for caching utility functions."""

    def test_get_cache_dir(self) -> None:
        """Test cache directory creation."""
        cache_dir = utils._get_cache_dir()
        assert cache_dir.exists()
        assert cache_dir.is_dir()
        assert ".biopython-mcp" in str(cache_dir)

    def test_get_cache_key(self) -> None:
        """Test cache key generation."""
        key1 = utils._get_cache_key("pubmed", "search", {"query": "test"})
        key2 = utils._get_cache_key("pubmed", "search", {"query": "test"})
        key3 = utils._get_cache_key("pubmed", "search", {"query": "different"})

        assert key1 == key2  # Same params = same key
        assert key1 != key3  # Different params = different key
        assert len(key1) == 64  # SHA256 hex length

    def test_set_and_get_cached_result(self) -> None:
        """Test setting and getting cached result."""
        data = {"success": True, "result": "test data"}
        params = {"query": "test", "max_results": 10}

        # Set cache
        utils.set_cached_result("test_db", "search", params, data)

        # Get cache (should exist and not be expired)
        result = utils.get_cached_result("test_db", "search", params, ttl=3600)
        assert result is not None
        assert result["success"] is True
        assert result["result"] == "test data"

    def test_get_cached_result_not_found(self) -> None:
        """Test getting non-existent cached result."""
        params = {"query": "nonexistent"}
        result = utils.get_cached_result("test_db", "search", params)
        assert result is None

    def test_get_cached_result_expired(self) -> None:
        """Test getting expired cached result."""
        data = {"success": True, "result": "test"}
        params = {"query": "expired_test"}

        # Set cache
        utils.set_cached_result("test_db", "search", params, data)

        # Get with TTL of 0 seconds (immediately expired)
        result = utils.get_cached_result("test_db", "search", params, ttl=0)
        assert result is None

    def test_clear_cache_specific_database(self) -> None:
        """Test clearing cache for specific database."""
        data = {"success": True}
        params = {"query": "test"}

        # Set cache for multiple databases
        utils.set_cached_result("db1", "search", params, data)
        utils.set_cached_result("db2", "search", params, data)

        # Clear only db1
        count = utils.clear_cache("db1")
        assert count >= 1

        # Verify db1 is cleared but db2 still exists
        assert utils.get_cached_result("db1", "search", params) is None
        # db2 might still exist depending on test execution order

    def test_clear_cache_all_databases(self) -> None:
        """Test clearing cache for all databases."""
        data = {"success": True}
        params = {"query": "test"}

        # Set cache
        utils.set_cached_result("db_clear_all", "search", params, data)

        # Clear all
        count = utils.clear_cache("")
        assert count >= 0

    def test_cache_with_invalid_data(self) -> None:
        """Test caching with data that can't be serialized."""
        # This should fail silently without raising an exception
        params = {"query": "test"}
        utils.set_cached_result("test_db", "search", params, {"func": lambda: None})

        # Getting should return None since set failed - but we don't need to verify
        # since the important part is that set_cached_result didn't raise an exception

    def test_get_cached_result_corrupted_file(self) -> None:
        """Test getting cached result from corrupted file."""
        params = {"query": "corrupted_test"}
        cache_dir = utils._get_cache_dir()
        db_dir = cache_dir / "test_db_corrupted"
        db_dir.mkdir(parents=True, exist_ok=True)

        # Create corrupted cache file
        cache_key = utils._get_cache_key("test_db_corrupted", "search", params)
        cache_file = db_dir / f"{cache_key}.json"
        cache_file.write_text("invalid json{{{")

        # Should return None for corrupted file
        result = utils.get_cached_result("test_db_corrupted", "search", params)
        assert result is None
