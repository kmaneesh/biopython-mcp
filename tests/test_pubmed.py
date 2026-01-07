"""Tests for PubMed module."""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from biopython_mcp.modules import pubmed


class TestPubMedFetch:
    """Tests for pubmed_fetch function."""

    @patch("biopython_mcp.modules.pubmed.httpx.get")
    def test_pubmed_fetch_success(self, mock_get: MagicMock) -> None:
        """Test successful PMC article fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<article>Test Article</article>"
        mock_get.return_value = mock_response

        result = pubmed.pubmed_fetch("PMC123456", format="xml")

        assert result["success"] is True
        assert result["pmc_id"] == "PMC123456"
        assert result["format"] == "xml"
        assert "<article>" in result["content"]

    @patch("biopython_mcp.modules.pubmed.httpx.get")
    def test_pubmed_fetch_not_found(self, mock_get: MagicMock) -> None:
        """Test PMC article not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = pubmed.pubmed_fetch("PMC999999", format="xml")

        assert result["success"] is False
        assert "error" in result
        assert "404" in result["error"]

    @patch("biopython_mcp.modules.pubmed.httpx.get")
    def test_pubmed_fetch_timeout(self, mock_get: MagicMock) -> None:
        """Test PMC fetch timeout."""
        import httpx

        mock_get.side_effect = httpx.TimeoutException("Timeout")

        result = pubmed.pubmed_fetch("PMC123456", format="xml", timeout=1)

        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    @patch("biopython_mcp.modules.pubmed.httpx.get")
    def test_pubmed_fetch_invalid_format(self, mock_get: MagicMock) -> None:
        """Test invalid format parameter."""
        result = pubmed.pubmed_fetch("PMC123456", format="invalid")

        assert result["success"] is False
        assert "format" in result["error"].lower()


class TestGetPMCURL:
    """Tests for get_pmc_url function."""

    def test_get_pmc_url_with_prefix(self) -> None:
        """Test URL generation with PMC prefix."""
        url = pubmed.get_pmc_url("PMC123456")
        assert url == "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC123456/"

    def test_get_pmc_url_without_prefix(self) -> None:
        """Test URL generation without PMC prefix."""
        url = pubmed.get_pmc_url("123456")
        assert url == "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC123456/"


class TestGetDOIURL:
    """Tests for get_doi_url function."""

    def test_get_doi_url(self) -> None:
        """Test DOI URL generation."""
        url = pubmed.get_doi_url("10.1371/journal.pone.0012345")
        assert url == "https://doi.org/10.1371/journal.pone.0012345"


class TestPubMedReview:
    """Tests for pubmed_review function."""

    @patch("biopython_mcp.modules.pubmed.database")
    @patch("builtins.open", new_callable=mock_open)
    @patch("biopython_mcp.modules.pubmed.Path")
    def test_pubmed_review_success_full_format(
        self, mock_path: MagicMock, mock_file: MagicMock, mock_database: MagicMock
    ) -> None:
        """Test successful review generation in full format."""
        # Mock search result
        mock_database.entrez_search.return_value = {
            "success": True,
            "ids": ["12345", "67890"],
            "total_found": 2,
        }

        # Mock summary result
        mock_database.entrez_summary.return_value = {
            "success": True,
            "summaries": [
                {
                    "Id": "12345",
                    "Title": "Test Article 1",
                    "AuthorList": [{"LastName": "Smith", "Initials": "J"}],
                    "FullJournalName": "Test Journal",
                    "PubDate": "2024",
                    "ArticleIds": {"pmc": "PMC123", "doi": "10.1234/test"},
                }
            ],
        }

        # Mock fetch result for abstract
        mock_database.entrez_fetch.return_value = {
            "success": True,
            "data": "Test abstract content.",
        }

        # Mock path operations
        mock_path_instance = MagicMock()
        mock_path_instance.parent.mkdir = MagicMock()
        mock_path_instance.stat.return_value.st_size = 1024
        mock_path_instance.absolute.return_value = "/tmp/test.md"
        mock_path.return_value = mock_path_instance

        result = pubmed.pubmed_review(
            query="test query",
            output_path="/tmp/test.md",
            format="full",
            max_results=2,
            storage="file",
        )

        assert result["status"] == "success"
        assert result["articles_written"] == 1
        assert result["filepath"] == "/tmp/test.md"
        assert "file_size_kb" in result

    @patch("biopython_mcp.modules.pubmed.database")
    def test_pubmed_review_invalid_output_path(self, mock_database: MagicMock) -> None:
        """Test review with invalid output path."""
        result = pubmed.pubmed_review(query="test", output_path="/tmp/test.txt", format="full")

        assert result["status"] == "error"
        assert result["error_type"] == "validation_error"
        assert ".md" in result["message"]

    @patch("biopython_mcp.modules.pubmed.database")
    def test_pubmed_review_invalid_format(self, mock_database: MagicMock) -> None:
        """Test review with invalid format."""
        result = pubmed.pubmed_review(query="test", output_path="/tmp/test.md", format="invalid")

        assert result["status"] == "error"
        assert result["error_type"] == "validation_error"

    @patch("biopython_mcp.modules.pubmed.database")
    def test_pubmed_review_search_failure(self, mock_database: MagicMock) -> None:
        """Test review when search fails."""
        mock_database.entrez_search.return_value = {
            "success": False,
            "error": "Search failed",
        }

        result = pubmed.pubmed_review(query="test", output_path="/tmp/test.md")

        assert result["status"] == "error"
        assert result["error_type"] == "query_error"

    @patch("biopython_mcp.modules.pubmed.database")
    def test_pubmed_review_no_results(self, mock_database: MagicMock) -> None:
        """Test review when no articles found."""
        mock_database.entrez_search.return_value = {
            "success": True,
            "ids": [],
            "total_found": 0,
        }

        result = pubmed.pubmed_review(query="test", output_path="/tmp/test.md")

        assert result["status"] == "error"
        assert result["error_type"] == "query_error"
        assert "No articles found" in result["message"]

    @patch("biopython_mcp.modules.pubmed.database")
    @patch("builtins.open", new_callable=mock_open)
    @patch("biopython_mcp.modules.pubmed.Path")
    def test_pubmed_review_minimal_format(
        self, mock_path: MagicMock, mock_file: MagicMock, mock_database: MagicMock
    ) -> None:
        """Test review in minimal format."""
        mock_database.entrez_search.return_value = {
            "success": True,
            "ids": ["12345"],
            "total_found": 1,
        }

        mock_database.entrez_summary.return_value = {
            "success": True,
            "summaries": [
                {
                    "Id": "12345",
                    "Title": "Test Article",
                    "PubDate": "2024",
                    "ArticleIds": {"doi": "10.1234/test"},
                }
            ],
        }

        mock_path_instance = MagicMock()
        mock_path_instance.parent.mkdir = MagicMock()
        mock_path_instance.stat.return_value.st_size = 512
        mock_path_instance.absolute.return_value = "/tmp/test.md"
        mock_path.return_value = mock_path_instance

        result = pubmed.pubmed_review(query="test", output_path="/tmp/test.md", format="minimal")

        assert result["status"] == "success"
        assert result["format"] == "minimal"

    @patch("biopython_mcp.modules.pubmed.database")
    @patch("builtins.open", new_callable=mock_open)
    @patch("biopython_mcp.modules.pubmed.Path")
    def test_pubmed_review_summary_format(
        self, mock_path: MagicMock, mock_file: MagicMock, mock_database: MagicMock
    ) -> None:
        """Test review in summary format."""
        mock_database.entrez_search.return_value = {
            "success": True,
            "ids": ["12345"],
            "total_found": 1,
        }

        mock_database.entrez_summary.return_value = {
            "success": True,
            "summaries": [
                {
                    "Id": "12345",
                    "Title": "Test abstract Article",
                    "PubDate": "2024",
                    "ArticleIds": {"pmc": "PMC123"},
                }
            ],
        }

        mock_database.entrez_fetch.return_value = {
            "success": True,
            "data": "First sentence. Second sentence.",
        }

        mock_path_instance = MagicMock()
        mock_path_instance.parent.mkdir = MagicMock()
        mock_path_instance.stat.return_value.st_size = 768
        mock_path_instance.absolute.return_value = "/tmp/test.md"
        mock_path.return_value = mock_path_instance

        result = pubmed.pubmed_review(query="test", output_path="/tmp/test.md", format="summary")

        assert result["status"] == "success"
        assert result["format"] == "summary"

    @patch("biopython_mcp.modules.pubmed.database")
    @patch("builtins.open", side_effect=PermissionError("Cannot write"))
    @patch("biopython_mcp.modules.pubmed.Path")
    def test_pubmed_review_write_error(
        self, mock_path: MagicMock, mock_file: MagicMock, mock_database: MagicMock
    ) -> None:
        """Test review when file cannot be written."""
        mock_database.entrez_search.return_value = {
            "success": True,
            "ids": ["12345"],
            "total_found": 1,
        }

        mock_path_instance = MagicMock()
        mock_path_instance.parent.mkdir = MagicMock()
        mock_path.return_value = mock_path_instance

        result = pubmed.pubmed_review(query="test", output_path="/tmp/test.md")

        assert result["status"] == "error"
        assert result["error_type"] == "write_error"

    @patch("biopython_mcp.modules.pubmed.database")
    @patch("builtins.open", new_callable=mock_open)
    @patch("biopython_mcp.modules.pubmed.Path")
    def test_pubmed_review_obsidian_storage(
        self, mock_path: MagicMock, mock_file: MagicMock, mock_database: MagicMock
    ) -> None:
        """Test review with Obsidian storage format."""
        mock_database.entrez_search.return_value = {
            "success": True,
            "ids": ["12345"],
            "total_found": 1,
        }

        mock_database.entrez_summary.return_value = {
            "success": True,
            "summaries": [
                {
                    "Id": "12345",
                    "Title": "Test Article",
                    "PubDate": "2024",
                    "FullJournalName": "Test Journal",
                    "ArticleIds": {},
                }
            ],
        }

        mock_database.entrez_fetch.return_value = {"success": False}

        mock_path_instance = MagicMock()
        mock_path_instance.parent.mkdir = MagicMock()
        mock_path_instance.stat.return_value.st_size = 1024
        mock_path_instance.absolute.return_value = "/tmp/test.md"
        mock_path.return_value = mock_path_instance

        result = pubmed.pubmed_review(
            query="test query", output_path="/tmp/test.md", storage="obsidian"
        )

        assert result["status"] == "success"
        # Verify Obsidian frontmatter would be written
        mock_file.assert_called()
